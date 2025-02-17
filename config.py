import psutil 
import keyboard
import subprocess

def run_bat_and_wait_for_output(bat_file, target_text):
    process = subprocess.Popen(bat_file, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    
    for line in iter(process.stdout.readline, ''):
        print(line, end="")  # Отобразить вывод батника в консоли
        if target_text in line:
            print(f"\nНайдено: {target_text}. Завершаем ожидание.")
            process.terminate()  # Завершаем процесс, если нашли нужный текст
            break
    
    process.wait()
