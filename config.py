import psutil 
import keyboard

YUMA_PROCESS_NAME = "Igor"

def find_process_by_name(name):
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] and name.lower() in process.info['name'].lower():
            return process.info
    return None

def start_tests():
    print("Press NumPad '0' to start tests")
    keyboard.wait("num 0")
