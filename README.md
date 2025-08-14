# 🚗 ROS 2 Camera-Based Line Follower

This is a ROS 2 Python node that makes a robot follow a **black line** using its camera feed.

It uses **OpenCV** to detect the line and simple **proportional control** to steer the robot toward it.

If the line is lost, the robot rotates slowly in place to find it again.

---

## 📦 Requirements

You’ll need:

* **ROS 2 Humble** (or a compatible version)
* **Gazebo**
* **Python 3**

## ⚙️ How It Works

1. **Camera Input**

   The node subscribes to a camera topic (default `/camera`) and converts the image from ROS format into an OpenCV `numpy` array using `cv_bridge`.
2. **Preprocessing**

   The image is converted to  **grayscale** , then thresholded to isolate **dark regions** (the black line).
3. **Line Detection**

   The largest contour found in the thresholded image is assumed to be the line.

   The **center position (cx)** of this contour is calculated.
4. **Error Calculation**

   The horizontal difference between `cx` and the image’s center is the  **error** .

   * Positive error → line is to the right → turn right
   * Negative error → line is to the left → turn left
5. **Control Output**

   The robot’s `/cmd_vel` velocity is updated using :

   ```
   angular_z = -error * Kp

   ```

   while moving forward at a fixed speed.

   If no line is detected, the robot stops forward motion and  **rotates in place** .
6. **Debug Display**

   Two OpenCV windows show:

   * **Camera View** with the detected line center marked.
   * **Mask** showing the binary thresholded image.

---

## 🎯 Tuning Parameters

* **`forward_speed`** : Forward motion speed in m/s (`0.3` default).
* **`kp`** : Proportional steering gain (`0.004` default). Higher = sharper turns.
* **`search_turn_speed`** : Rotation speed when no line detected (`0.2` default).
* **`use_crop`** : If `True`, only processes the bottom third of the image (reduces noise).

---
