import pytest
import os
import keyboard
import time
import pyautogui
import cv2
import numpy as np

def apply_color_mask(image, lower_bound, upper_bound):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    
    # Убираем шумы с помощью морфологических операций
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    return cv2.bitwise_and(image, image, mask=mask)

def get_color_bounds(flag_type):
    color_bounds = {
        "W": (np.array([35, 50, 50]), np.array([85, 255, 255])),  # Зеленый
        "A": (np.array([20, 50, 50]), np.array([35, 255, 255])),  # Желтый
        "S": (np.array([100, 50, 50]), np.array([140, 255, 255])),  # Синий
        "D": (np.array([0, 50, 50]), np.array([10, 255, 255]))   # Красный
    }
    return color_bounds.get(flag_type, (np.array([0, 0, 0]), np.array([179, 255, 255])))

def find_image_on_screen(template_path, flag_type, confidence=0.7, use_color=True):
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    if template is None:
        print(f"Error: Image {template_path} not found.")
        return None
    
    if use_color:
        screenshot_hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        template_hsv = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
        
        lower_bound, upper_bound = get_color_bounds(flag_type)
        
        masked_screenshot = apply_color_mask(screenshot, lower_bound, upper_bound)
        masked_template = apply_color_mask(template, lower_bound, upper_bound)
        
        result = cv2.matchTemplate(masked_screenshot, masked_template, cv2.TM_CCOEFF_NORMED)
        
        # Проверка среднего цвета найденной области
        h_mean_template = np.mean(template_hsv[:, :, 0])
        match_loc = cv2.minMaxLoc(result)[3]
        x, y = match_loc
        roi = screenshot_hsv[y:y + template.shape[0], x:x + template.shape[1]]
        if roi.shape[0] > 0 and roi.shape[1] > 0:
            h_mean_roi = np.mean(roi[:, :, 0])
            if abs(h_mean_template - h_mean_roi) > 15:
                print("Color mismatch detected. Ignoring match.")
                return None
    else:
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    print(f"Max accuracy: {max_val:.2f}, Required confidence: {confidence}")
    if max_val >= confidence:
        print(f"Image found! Coords: {max_loc}, accuracy: {max_val:.2f}")
        return max_loc
    else:
        print(f"Image not found (accuracy: {max_val:.2f}, required >= {confidence})")
        return None

def monitor_screen_for_image(template_path, interval=0.5):
    print("Running monitor screen")
    while True:
        find_image_on_screen(template_path)
        time.sleep(interval)

def press_key_for_duration(key, template_path, flag_type, interval=0.5, confidence=0.9):
    print(f"Pressing '{key}' with confidence {confidence}...")

    keyboard.press(key)  # Начинаем удерживать клавишу
    while True:
        match = find_image_on_screen(template_path, flag_type, confidence=confidence)  # Передаём явно
        if match:
            print(f"Image '{template_path}' found, releasing '{key}'!")
            break
        time.sleep(interval)  # Ждём перед следующей проверкой

    keyboard.release(key)  # Отпускаем клавишу после обнаружения изображения

def test_check_moves():
    press_key_for_duration("w", "flags/signal_W.png", "W", confidence=0.9)
    press_key_for_duration("a", "flags/signal_A.png", "A", confidence=0.9)
    #press_key_for_duration("s", "flags/signal_S.png", "S", confidence=0.9)
    #press_key_for_duration("d", "flags/signal_D.png", "D", confidence=0.9)
