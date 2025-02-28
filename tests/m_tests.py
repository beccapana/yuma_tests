import time
import keyboard
import subprocess
import pyautogui
import cv2
import numpy as np
import psutil
from typing import Optional, Tuple

def is_system_sound_muted(): #TODO: to config. ловил баг
    command = "(Get-AudioDevice -Playback).Mute"
    result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)
    return "True" in result.stdout

def unmute_system_sound(): #TODO: to config. ловил баг
    subprocess.run(["powershell", "-Command", "(Get-AudioDevice -Playback).Mute = $false"])

def handle_sound_issue(): #TODO: to config. ловил баг
    if is_system_sound_muted():
        print("Системный звук отключен. Включаем обратно...")
        unmute_system_sound()
        print("Системный звук включен. Продолжаем тест...")
        keyboard.press_and_release('d')
        time.sleep(1)

def run_bat_and_wait_for_output(bat_file: str, target_text: str): #TODO: to config
    process = subprocess.Popen(bat_file, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    
    for line in iter(process.stdout.readline, ''):
        print(line, end="")
        if target_text in line:
            print(f"\nНайдено: {target_text}. Завершаем ожидание.")
            process.terminate()
            break
    
    process.wait()

def apply_color_mask(image: np.ndarray, lower_bound: np.ndarray, upper_bound: np.ndarray): #TODO: to config
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return cv2.bitwise_and(image, image, mask=mask)

def get_color_bounds(flag_type: str): #TODO: to config
    color_bounds = {
        "W": (np.array([35, 50, 50]), np.array([85, 255, 255])),
        "A": (np.array([20, 50, 50]), np.array([35, 255, 255])),
        "S": (np.array([105, 80, 80]), np.array([135, 255, 255])),
        "D": (np.array([170, 50, 50]), np.array([180, 255, 255]))
    }
    return color_bounds.get(flag_type, (np.array([0, 0, 0]), np.array([180, 255, 255])))

def find_image_on_screen(template_path: str, flag_type: str, confidence: float = 0.7, use_color: bool = True): #TODO: to config
    screenshot = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    
    if template is None:
        print(f"Ошибка: изображение {template_path} не найдено.")
        return None

    if use_color:
        lower_bound, upper_bound = get_color_bounds(flag_type)
        screenshot = apply_color_mask(screenshot, lower_bound, upper_bound)
        template = apply_color_mask(template, lower_bound, upper_bound)
    else:
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    print(f"[{flag_type}] Макс. точность: {max_val:.2f}, Требуемая: {confidence}")
    return max_loc if max_val >= confidence else None

def press_key_for_duration(key: str, template_path: str, flag_type: str, interval: float = 0.5, confidence: float = 0.9): #TODO: to config
    print(f"Начало нажатия '{key}' для флага '{flag_type}' с точностью {confidence}...")
    keyboard.press(key)
    try:
        while not find_image_on_screen(template_path, flag_type, confidence=confidence):
            time.sleep(interval)
    finally:
        keyboard.release(key)
        print(f"Клавиша '{key}' отпущена для флага '{flag_type}'.")

def test_check_moves():
    #print("=== НАЧАЛО test_check_moves ===") #ловил баг
    for key, flag in zip("wasd", "WASD"):
        print(f"Проверка флага '{flag}'...")
        press_key_for_duration(key, f"images/flags/signal_{flag}.png", flag, confidence=0.85)
        if flag == 'S': #ловлю баг
            handle_sound_issue()
        time.sleep(0.5)
    #print("=== КОНЕЦ test_check_moves ===") #ловил баг

def log_running_processes(): #TODO: to config
    return [(proc.info['pid'], proc.info['name']) for proc in psutil.process_iter(attrs=['pid', 'name'])]

def monitor_sound_mute(): #TODO: to config
    previous_state = is_system_sound_muted()
    while True:
        current_state = is_system_sound_muted()
        if current_state != previous_state:
            print(f"Изменение звука обнаружено. Новый статус: {'Отключен' if current_state else 'Включен'}")
            print("Активные процессы:")
            for pid, name in log_running_processes():
                print(f"PID: {pid}, Name: {name}")
            previous_state = current_state
        time.sleep(1)

def find_yuma_on_screen(confidence: float = 0.7):
    yuma_images = {
        "Back": "images/yuma/YumaBack.png",
        "Front": "images/yuma/YumaFront.png",
        "Left": "images/yuma/YumaLeft.png",
        "Right": "images/yuma/YumaRight.png",
    }
    
    while True:
        screenshot = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)
        best_match = max(
            ((direction, cv2.matchTemplate(screenshot, cv2.imread(img_path, cv2.IMREAD_COLOR), cv2.TM_CCOEFF_NORMED))
             for direction, img_path in yuma_images.items() if cv2.imread(img_path, cv2.IMREAD_COLOR) is not None),
            key=lambda x: cv2.minMaxLoc(x[1])[1],
            default=(None, None)
        )
        
        if best_match[0]:
            print(f"Лучшее совпадение: {best_match[0]} с точностью {cv2.minMaxLoc(best_match[1])[1]:.2f}")
        time.sleep(1)
