提示：这只是个小学生的作品，漏洞有点多，有问题留言！谢！如果感觉项目不错，记得留下一颗star✨！
Note: This is just an elementary school student's work, so there are quite a few flaws. Leave a comment if you find any issues! Thanks! If you think the project is good, remember to leave a star✨ ! There will be an English introduction later.

一个基于计算机视觉的智能手势交互系统，通过摄像头识别手势，实现**空中绘画**和**鼠标控制**。无需任何外接硬件！

### ✨ 核心功能

*   **双模式操作**：一键切换**绘画模式**与**鼠标模式**。
*   **空中绘画**：捏合拇指和食指即可在空中作画。
*   **手势控制鼠标**：通过手势移动光标并点击。
*   **智能手势识别**：
    *   **捏合**：绘制或点击（距离 < 35像素）（离屏幕摄像头约20-30cm）
    *   **张开手掌**：预览画笔位置或移动鼠标
    *   **握拳**：瞬间清空画布
*   **实时视觉反馈**：屏幕实时显示模式、状态和光标位置。
*   **平滑算法**：先进的滤波算法，确保鼠标移动流畅无抖动。

### 🚀 快速开始

#### 环境准备
*   Python 3.11 最为合适
*   一个可用的摄像头

#### 安装步骤
只需要安装requirements.txt的库即可

#### 使用说明
1.  运行主程序：
    ```bash
    python main.py
    ```
2.  **按键控制**：
    *   `空格键`：在**绘画模式**和**鼠标模式**之间切换。
    *   `c` 键：清空画布（仅在绘画模式下有效）。
    *   `q` 键：退出程序。
3.  遵循屏幕上的指示和手势引导进行操作。

### 🛠️ 技术栈

*   **计算机视觉**：[OpenCV](https://opencv.org/) 用于视频流处理。
*   **手势识别**：[Google MediaPipe](https://mediapipe.dev/) 提供高精度手部关键点检测。
*   **系统控制**：[PyAutoGUI](https://pyautogui.readthedocs.io/) 实现跨平台的鼠标控制。
*   **核心库**：NumPy, Math。

如果还不错的话，一定一定要给一颗star！！！这对我帮助很大！

#######English###########
An intelligent gesture interaction system based on computer vision that recognizes gestures through a camera, enabling **air drawing** and **mouse control**. No additional hardware required! (This translation is AI-generated, so it may not be entirely accurate. Please understand, thank you—I’m still young and my English isn’t very good.)

### ✨ Core Features

* **Dual-Mode Operation**: Switch between **Drawing Mode** and **Mouse Mode** with one click.
* **Air Drawing**: Pinch your thumb and index finger to draw in the air.
* **Gesture-Based Mouse Control**: Move the cursor and click using hand gestures.
* **Intelligent Gesture Recognition**:
  * **Pinch**: Draw or click (distance < 35 pixels) (about 20-30cm from the camera)
  * **Open Palm**: Preview brush position or move the mouse
  * **Fist**: Instantly clear the canvas
* **Real-Time Visual Feedback**: Display mode, status, and cursor position in real-time on the screen.
* **Smoothing Algorithm**: Advanced filtering algorithm ensures smooth and jitter-free mouse movement.

### 🚀 Quick Start

#### Environment Setup
* Python 3.11 is recommended
* A usable camera

#### Installation Steps
Simply install the libraries listed in requirements.txt.

#### How to Use
1. Run the main program:
```bash
python main.py
```
2. **Keyboard Controls**:
* `Space`: Switch between **Drawing Mode** and **Mouse Mode**
* `c`: Clear the canvas (only works in Drawing Mode)
* `q`: Exit the program
3. Follow the on-screen instructions and gesture prompts to operate.

### 🛠️ Tech Stack

* **Computer Vision**: [OpenCV](https://opencv.org/) for video stream processing
* **Gesture Recognition**: [Google MediaPipe](https://mediapipe.dev/) for high-precision hand landmark detection
* **System Control**: [PyAutoGUI](https://pyautogui.readthedocs.io/) for cross-platform mouse control
* **Core Libraries**: NumPy, Math

If you find this useful, please give it a star! It would really help me a lot!
