import cv2
import numpy as np
import mediapipe as mp
import math
import pyautogui
import time

# 初始化MediaPipe手部模型
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# 配置手部检测参数
hands = mp_hands.Hands(
    static_image_mode=False,        # 视频流模式
    max_num_hands=1,                # 最多检测一只手
    min_detection_confidence=0.7,   # 检测置信度阈值
    min_tracking_confidence=0.5     # 跟踪置信度阈值
)

# 创建一个白色的画布
canvas = None
is_drawing = False  # 是否正在绘制的标志
last_point = None   # 上一个绘制点，用于连线

# 模式定义
MODES = {
    0: "DRAW_MODE",     # 绘制模式
    1: "MOUSE_MODE"     # 鼠标控制模式
}
current_mode = 0  # 默认模式为绘制模式

# 鼠标控制相关变量
screen_width, screen_height = pyautogui.size()
mouse_down = False  # 鼠标是否按下
click_threshold = 35  # 点击阈值（像素），与绘制模式一致

# 平滑滤波相关变量
position_history = []  # 位置历史记录
max_history_length = 10  # 最大历史记录长度
last_mouse_time = time.time()  # 上次鼠标移动时间
min_move_interval = 0.01  # 最小移动间隔（秒）

# 手部关键点索引
WRIST = 0
THUMB_TIP = 4
INDEX_FINGER_TIP = 8
MIDDLE_FINGER_TIP = 12
RING_FINGER_TIP = 16
PINKY_TIP = 20

# 打开摄像头
cap = cv2.VideoCapture(0)

def is_fist(hand_landmarks, w, h):
    """检测是否是握拳手势"""
    # 获取手腕位置
    wrist = hand_landmarks.landmark[WRIST]
    wx, wy = int(wrist.x * w), int(wrist.y * h)
    
    # 获取所有指尖位置
    fingertips = [
        THUMB_TIP, INDEX_FINGER_TIP, MIDDLE_FINGER_TIP, 
        RING_FINGER_TIP, PINKY_TIP
    ]
    
    # 计算所有指尖到手腕的平均距离
    total_distance = 0
    for tip in fingertips:
        tip_point = hand_landmarks.landmark[tip]
        tx, ty = int(tip_point.x * w), int(tip_point.y * h)
        distance = math.hypot(tx - wx, ty - wy)
        total_distance += distance
    
    avg_distance = total_distance / len(fingertips)
    
    # 平均距离小于150像素即为握拳
    return avg_distance < 150

def smooth_mouse_position(current_x, current_y):
    """使用加权平均和历史记录进行平滑处理"""
    global position_history
    
    # 添加当前位置到历史记录
    position_history.append((current_x, current_y))
    
    # 保持历史记录长度
    if len(position_history) > max_history_length:
        position_history.pop(0)
    
    # 如果历史记录太少，直接返回当前位置
    if len(position_history) < 3:
        return current_x, current_y
    
    # 加权平均：最近的位置权重更大
    smoothed_x, smoothed_y = 0, 0
    total_weight = 0
    
    for i, (x, y) in enumerate(position_history):
        # 权重递增：越近的位置权重越大（从1到n）
        weight = i + 1
        smoothed_x += x * weight
        smoothed_y += y * weight
        total_weight += weight
    
    smoothed_x /= total_weight
    smoothed_y /= total_weight
    
    return smoothed_x, smoothed_y

def control_mouse(hand_landmarks, w, h, frame):
    """控制鼠标模式下的手部交互 - 使用捏合手势点击"""
    global mouse_down, position_history, last_mouse_time
    
    # 获取食指尖和拇指尖的坐标
    index_finger = hand_landmarks.landmark[INDEX_FINGER_TIP]
    thumb = hand_landmarks.landmark[THUMB_TIP]

    ix, iy = int(index_finger.x * w), int(index_finger.y * h)
    tx, ty = int(thumb.x * w), int(thumb.y * h)
    
    # 计算两个指尖之间的距离
    distance = math.hypot(ix - tx, iy - ty)
    
    # 取两个指尖的中点作为鼠标位置
    mx, my = (ix + tx) // 2, (iy + ty) // 2
    
    # 映射摄像头坐标到屏幕坐标（考虑边界缓冲）
    margin = 50  # 边界缓冲像素
    screen_x = np.interp(mx, [margin, w - margin], [0, screen_width])
    screen_y = np.interp(my, [margin, h - margin], [0, screen_height])
    
    # 限制坐标在屏幕范围内
    screen_x = np.clip(screen_x, 0, screen_width)
    screen_y = np.clip(screen_y, 0, screen_height)
    
    # 使用平滑处理
    smoothed_x, smoothed_y = smooth_mouse_position(screen_x, screen_y)
    
    # 控制鼠标点击：距离小于阈值时点击
    if distance < click_threshold:
        if not mouse_down:
            # 首次进入阈值范围，执行鼠标按下
            pyautogui.mouseDown()
            mouse_down = True
            # 在画面上显示点击状态
            cv2.circle(frame, (mx, my), 15, (0, 0, 255), -1)
            cv2.putText(frame, "CLICK", (mx-20, my-20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            # 显示点击提示
            cv2.putText(frame, "Clicking...", (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    else:  # 距离大于阈值，释放鼠标
        if mouse_down:
            pyautogui.mouseUp()
            mouse_down = False
    
    # 限制鼠标移动频率，避免过于频繁的移动
    current_time = time.time()
    if current_time - last_mouse_time >= min_move_interval:
        pyautogui.moveTo(smoothed_x, smoothed_y, duration=0)
        last_mouse_time = current_time
    
    # 在画面上显示鼠标位置和状态
    circle_color = (0, 0, 255) if mouse_down else (0, 255, 255)
    circle_fill = -1 if mouse_down else 2
    circle_radius = 15 if mouse_down else 10
    
    # 显示当前点和拇指食指位置
    cv2.circle(frame, (ix, iy), 8, (0, 255, 0), -1)  # 食指尖 - 绿色
    cv2.circle(frame, (tx, ty), 8, (255, 0, 0), -1)  # 拇指尖 - 蓝色
    cv2.line(frame, (ix, iy), (tx, ty), (255, 255, 0), 2)  # 连接线
    
    # 显示中点（鼠标位置）
    cv2.circle(frame, (mx, my), circle_radius, circle_color, circle_fill)
    
    # 显示平滑位置（小绿点）
    pred_ix = int(np.interp(smoothed_x, [0, screen_width], [margin, w - margin]))
    pred_iy = int(np.interp(smoothed_y, [0, screen_height], [margin, h - margin]))
    cv2.circle(frame, (pred_ix, pred_iy), 5, (0, 255, 0), -1)
    
    # 显示距离信息
    cv2.putText(frame, f"Distance: {int(distance)}px", 
               (ix + 20, iy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # 显示距离阈值线
    if distance < click_threshold:
        cv2.putText(frame, "CLICK THRESHOLD", (ix + 20, iy + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    
    # 显示坐标信息
    cv2.putText(frame, f"Mouse: ({int(smoothed_x)}, {int(smoothed_y)})", 
               (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(frame, f"Click: {'ON' if mouse_down else 'OFF'}", 
               (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(frame, f"Dist: {int(distance)}/{click_threshold}", 
               (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 
               (0, 0, 255) if distance < click_threshold else (255, 255, 255), 1)
    
    return frame

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # 水平翻转图像
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # 初始化画布
    if canvas is None:
        canvas = np.ones((h, w, 3), dtype=np.uint8) * 255

    # 转换为RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    current_point = None  # 当前帧的绘制点
    preview_point = None  # 预览点（即使没有捏合也显示）

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            if MODES[current_mode] == "DRAW_MODE":
                # 绘制手部关键点
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # 绘制模式
                # 检测是否是握拳手势
                if is_fist(hand_landmarks, w, h):
                    # 检测到握拳，立即清除画布
                    canvas = np.ones((h, w, 3), dtype=np.uint8) * 255
                    continue
                
                # 获取食指尖和拇指尖的坐标
                index_finger = hand_landmarks.landmark[INDEX_FINGER_TIP]
                thumb = hand_landmarks.landmark[THUMB_TIP]

                ix, iy = int(index_finger.x * w), int(index_finger.y * h)
                tx, ty = int(thumb.x * w), int(thumb.y * h)
                
                # 计算两个指尖的中点作为预览点（总是显示）
                px, py = (ix + tx) // 2, (iy + ty) // 2
                preview_point = (px, py)

                # 计算两个指尖之间的距离
                distance = math.hypot(ix - tx, iy - ty)

                # 如果距离很近（小于35像素），则认为是捏合手势
                if distance < 40:
                    current_point = preview_point

                    # 在摄像头上显示当前画笔位置（绿色实心圆）
                    cv2.circle(frame, (px, py), 10, (0, 255, 0), -1)

                    # 设置绘制标志并更新点
                    if not is_drawing:
                        is_drawing = True
                    if last_point:
                        # 在画布上画线
                        cv2.line(canvas, last_point, current_point, (0, 0, 255), 5)
                    last_point = current_point
                else:
                    # 指尖分开，停止绘制
                    is_drawing = False
                    last_point = None
                    
                    # 即使没有捏合，也显示预览点（蓝色空心圆）
                    cv2.circle(frame, (px, py), 10, (255, 0, 0), 2)
                    
            elif MODES[current_mode] == "MOUSE_MODE":
                # 鼠标控制模式 - 简化显示
                # 只显示食指和拇指的关键点
                index_finger = hand_landmarks.landmark[INDEX_FINGER_TIP]
                thumb = hand_landmarks.landmark[THUMB_TIP]
                ix, iy = int(index_finger.x * w), int(index_finger.y * h)
                tx, ty = int(thumb.x * w), int(thumb.y * h)
                
                # 显示食指和拇指点
                cv2.circle(frame, (ix, iy), 6, (0, 255, 0), -1)
                cv2.circle(frame, (tx, ty), 6, (255, 0, 0), -1)
                
                frame = control_mouse(hand_landmarks, w, h, frame)

    # 显示预览点（如果有手部检测但没捏合，且是绘制模式）
    elif preview_point is not None and MODES[current_mode] == "DRAW_MODE":
        px, py = preview_point
        cv2.circle(frame, (px, py), 10, (255, 0, 0), 2)

    # 如果当前帧没有检测到捏合手势，但之前正在绘制，也需要停止
    if not current_point and is_drawing:
        is_drawing = False
        last_point = None

    # 将画布内容叠加到摄像头画面上（仅在绘制模式）
    if MODES[current_mode] == "DRAW_MODE":
        combined = cv2.addWeighted(frame, 0.7, canvas, 0.3, 0)
    else:
        combined = frame.copy()
        # 在鼠标模式下添加半透明背景，提高可读性
        overlay = combined.copy()
        cv2.rectangle(overlay, (0, 0), (300, 130), (0, 0, 0), -1)
        combined = cv2.addWeighted(overlay, 0.5, combined, 0.5, 0)

    # 显示当前模式
    mode_text = f"Mode: {MODES[current_mode]}"
    mode_color = (0, 255, 0) if MODES[current_mode] == "DRAW_MODE" else (0, 255, 255)
    cv2.putText(combined, mode_text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, mode_color, 2)
    
    # 显示操作说明
    cv2.putText(combined, "Press SPACE to switch mode", (10, h - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    if MODES[current_mode] == "DRAW_MODE":
        # 绘制模式说明
        cv2.putText(combined, "DRAW MODE:", (10, h - 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        cv2.putText(combined, "- Pinch: Draw (Green)", (10, h - 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(combined, "- Open: Preview (Blue)", (10, h - 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(combined, "- Fist: Clear canvas", (10, h - 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
    else:
        # 鼠标模式说明
        cv2.putText(combined, "MOUSE MODE:", (10, h - 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
        cv2.putText(combined, "- Index (Green): Cursor", (10, h - 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(combined, "- Thumb (Blue): Target", (10, h - 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(combined, f"- Pinch (<{click_threshold}px): Click", (10, h - 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    # 显示最终图像
    cv2.imshow('Air Drawing & Mouse Control', combined)

    # 按键控制
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('c') and MODES[current_mode] == "DRAW_MODE":
        canvas = np.ones((h, w, 3), dtype=np.uint8) * 255
    elif key == ord(' '):  # 空格键切换模式
        current_mode = (current_mode + 1) % len(MODES)
        print(f"切换到模式: {MODES[current_mode]}")
        # 切换到鼠标模式时，确保鼠标状态重置
        if MODES[current_mode] == "MOUSE_MODE" and mouse_down:
            pyautogui.mouseUp()
            mouse_down = False
        # 切换到绘制模式时，重置绘制状态
        elif MODES[current_mode] == "DRAW_MODE":
            is_drawing = False
            last_point = None
            position_history.clear()  # 清除鼠标位置历史

# 释放资源
hands.close()
cap.release()
cv2.destroyAllWindows()
