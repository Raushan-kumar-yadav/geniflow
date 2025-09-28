import undetected_chromedriver as uc
import psutil
import time

# Start undetected Chrome
driver = uc.Chrome(headless=False)  # You can set a profile here if needed

# Give Chrome a moment to launch
time.sleep(2)

# Get PID of ChromeDriver
driver_pid = driver.service.process.pid
print(f"ChromeDriver PID: {driver_pid}")

# Find Chrome child processes (launched by ChromeDriver)
parent_process = psutil.Process(driver_pid)
child_processes = parent_process.children(recursive=True)

# Wait for interaction (optional)
print("Chrome is running... will terminate in 10 seconds")
time.sleep(10)

# Terminate Chrome processes
for child in child_processes:
    print(f"Terminating Chrome PID: {child.pid}")
    try:
        child.terminate()
    except Exception as e:
        print(f"Error terminating child PID {child.pid}: {e}")

# Terminate ChromeDriver process itself
print(f"Terminating ChromeDriver PID: {driver_pid}")
try:
    parent_process.terminate()
except Exception as e:
    print(f"Error terminating parent PID {driver_pid}: {e}")
