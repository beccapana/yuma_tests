import cv2
import numpy as np
import pyautogui
import time

def find_yuma_on_screen(confidence: float = 0.7): #TODO: to yuma_tests
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