import time
import keyboard
import subprocess
import pyautogui
import cv2
import numpy as np
import psutil
from typing import Optional, Tuple
from tests.config import *

def test_check_moves():
    #print("=== НАЧАЛО test_check_moves ===") #ловил баг
    for key, flag in zip("wasd", "WASD"):
        print(f"Проверка флага '{flag}'...")
        press_key_for_duration(key, f"images/flags/signal_{flag}.png", flag, confidence=0.85)
        if flag == 'S': #ловлю баг
            handle_sound_issue()
        time.sleep(0.5)
    #print("=== КОНЕЦ test_check_moves ===") #ловил баг