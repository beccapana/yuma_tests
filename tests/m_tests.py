import pytest
import os
import keyboard
import time
import pyautogui
import cv2
import numpy as np

def find_image_on_screen(template_path, confidence=0.7):
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)  # Преобразуем в градации серого

    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)  # Загружаем образец
    if template is None:
        print(f"Error: Image {template_path} not found.")
        return None

    # Сравниваем изображения
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val >= confidence:  # Используем значение confidence как порог совпадения
        print(f"Image found! Coords: {max_loc}, accuracy: {max_val:.2f}")
        return max_loc
    else:
        print(f"Image not found (accuracy: {max_val:.2f}, would be >= {confidence})")
        return None
    

def monitor_screen_for_image(template_path, interval=0.5):
    print("Running monitor screen")
    while True:
        find_image_on_screen(template_path)
        time.sleep(interval)

def press_key_for_duration(key, template_path, interval=0.5, confidence=0.7):
    print(f"Pressing '{key}'...")

    keyboard.press(key)  # Начинаем удерживать клавишу
    while True:
        if find_image_on_screen(template_path, confidence):  # Проверяем наличие изображения
            print(f"Image '{template_path}' found, realising '{key}'!")
            break
        time.sleep(interval)  # Ждём перед следующей проверкой

    keyboard.release(key)  # Отпускаем клавишу после обнаружения изображения

def test_check_moves():
    press_key_for_duration("w", "flags/signal_W.png", confidence=0.8)
    #press_key_for_duration("a", "flags/signal_A.png", confidence=0.38)
    #press_key_for_duration("s", "flags/signal_true.png", confidence=0.55)
    #press_key_for_duration("d", "flags/signal_false.png", confidence=0.55)