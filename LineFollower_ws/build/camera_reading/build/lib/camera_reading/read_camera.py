import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2 as cv
import numpy as np

class LineFollower(Node):
    def __init__(self):
        super().__init__('line_follower')

        # Adjust to match your bridged camera topic
        camera_topic = '/camera'

        self.bridge = CvBridge()

        # Camera subscriber
        self.subscription = self.create_subscription(
            Image,
            camera_topic,
            self.image_callback,
            10
        )

        # Cmd_vel publisher
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Control parameters
        self.forward_speed = 0.3
        self.kp = 0.004
        self.search_turn_speed = 0.2  # Rotate speed when no line detected
        self.use_crop = False         # Set to True when detection works well

        self.get_logger().info(f"Line Follower started. Listening to {camera_topic}")

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            height, width, _ = frame.shape

            # Crop only bottom part if enabled
            if self.use_crop:
                crop_height = height // 3
                roi = frame[height - crop_height:height, :]
            else:
                roi = frame

            # Convert to grayscale
            gray = cv.cvtColor(roi, cv.COLOR_BGR2GRAY)

            # Threshold for dark areas (tuned for Gazebo lighting)
            mask = cv.inRange(gray, 0, 150)

            # Find contours
            contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

            twist = Twist()

            if contours:
                # Largest contour = the line
                c = max(contours, key=cv.contourArea)
                M = cv.moments(c)

                if M["m00"] > 0:
                    cx = int(M["m10"] / M["m00"])
                    error = cx - width // 2

                    # Draw debug
                    cv.circle(roi, (cx, roi.shape[0] // 2), 5, (0, 0, 255), -1)

                    # Proportional steering
                    twist.linear.x = self.forward_speed
                    twist.angular.z = -error * self.kp
                    self.cmd_pub.publish(twist)

                    self.get_logger().info(f"Line detected: error={error}, angular={twist.angular.z:.3f}")
            else:
                # No line → rotate slowly to search
                twist.linear.x = 0.0
                twist.angular.z = self.search_turn_speed
                self.cmd_pub.publish(twist)
                self.get_logger().warn("No line detected — rotating to search.")

            # Debug windows
            cv.imshow("Camera View", roi)
            cv.imshow("Mask", mask)
            cv.waitKey(1)

        except Exception as e:
            self.get_logger().error(f"Error: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = LineFollower()
    rclpy.spin(node)
    cv.destroyAllWindows()
    rclpy.shutdown()


if __name__ == '__main__':
    main()



