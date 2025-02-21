import os
import time
import keyboard
import pytest
import pyautogui
import cv2
import numpy as np
from typing import Optional, Tuple

#Применяет цветовую маску к изображению
def apply_color_mask(image: np.ndarray, lower_bound: np.ndarray, upper_bound: np.ndarray):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return cv2.bitwise_and(image, image, mask=mask)

#Возвращает границы цвета для заданного флага
def get_color_bounds(flag_type: str):
    color_bounds = {
        "W": (np.array([35, 50, 50]), np.array([85, 255, 255])),  # Зеленый
        "A": (np.array([20, 50, 50]), np.array([35, 255, 255])),  # Желтый
        "S": (np.array([110, 100, 100]), np.array([130, 255, 255])),
        "D": (np.array([170, 50, 50]), np.array([180, 255, 255]))    #красный
        }
    return color_bounds.get(flag_type, (np.array([0, 0, 0]), np.array([179, 255, 255])))

#Ищет изображение на экране, используя шаблон
def find_image_on_screen(template_path: str, flag_type: str, confidence: float = 0.7, use_color: bool = True):
    screenshot = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    if template is None:
        print(f"Ошибка: изображение {template_path} не найдено.")
        return None

    if use_color:
        lower_bound, upper_bound = get_color_bounds(flag_type)
        masked_screenshot = apply_color_mask(screenshot, lower_bound, upper_bound)
        masked_template = apply_color_mask(template, lower_bound, upper_bound)
    else:
        masked_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        masked_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    
    result = cv2.matchTemplate(masked_screenshot, masked_template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    print(f"Макс. точность: {max_val:.2f}, Требуемая: {confidence}")
    return max_loc if max_val >= confidence else None

#Наблюдает за экраном, проверяя наличие изображения
def monitor_screen_for_image(template_path: str, interval: float = 0.5):
    print("Запущен мониторинг экрана...")
    while True:
        find_image_on_screen(template_path)
        time.sleep(interval)

#Удерживает клавишу, пока изображение не будет найдено
def press_key_for_duration(key: str, template_path: str, flag_type: str, interval: float = 0.5, confidence: float = 0.9):
    print(f"Нажатие '{key}' с точностью {confidence}...")
    keyboard.press(key)
    try:
        while not find_image_on_screen(template_path, flag_type, confidence=confidence):
            time.sleep(interval)
    finally:
        keyboard.release(key)
        print(f"Изображение '{template_path}' найдено, клавиша '{key}' отпущена.")

def test_check_moves():
    for key, flag in zip("wasd", "WASD"):
        press_key_for_duration(key, f"images/flags/signal_{flag}.png", flag, confidence=0.9)
