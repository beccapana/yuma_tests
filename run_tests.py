import os
import tests
import psutil
import time
from tests.m_tests import *
#from tests import *
from config import *

while True:
    process_info = find_process_by_name(YUMA_PROCESS_NAME)
    if process_info:
        #print(f"Процесс найден: {process_info}")
        break
    print("Yuma is not running. Waiting for it to start...")
    time.sleep(2)

start_tests()

test_check_moves()





