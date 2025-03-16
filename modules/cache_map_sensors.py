import time
import requests
import threading

global_cpu_data = None
cpu_data_lock = threading.Lock()
CPU_FETCH_INTERVAL = 3  

_cache_thread_started = False

def update_global_cpu_data():
    global global_cpu_data
    while True:
        try:
            response = requests.get("http://localhost:5123/api/hardware/cpu", timeout=5)
            response.raise_for_status()
            data = response.json()
            with cpu_data_lock:
                global_cpu_data = data
        except Exception as e:
            with cpu_data_lock:
                global_cpu_data = {"error": str(e)}
        time.sleep(CPU_FETCH_INTERVAL)

def start_cache_updater():
    global _cache_thread_started
    if not _cache_thread_started:
        threading.Thread(target=update_global_cpu_data, daemon=True).start()
        _cache_thread_started = True

def get_cached_cpu_data():
    with cpu_data_lock:
        return global_cpu_data