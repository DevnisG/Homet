import multiprocessing
import os
import sys
import time
import flet as ft
from modules.translations import translate 

def cpu_stress(stop_event):
    while not stop_event.is_set():
        pass  

def cpu_relax(stop_event):
    while not stop_event.is_set():
        time.sleep(0.1)  

def memory_stress(stop_event):
    allocated_memory = []
    while not stop_event.is_set():
        allocated_memory.append(bytearray(1 * 10**9)) 
        time.sleep(0.1)  

def memory_release(stop_event):
    time.sleep(1) 

def cpu_ram_load_test(results_container: ft.Column):
    results_container.controls.clear()
    try:
        num_cores = os.cpu_count() or 2
        results_container.controls.append(ft.Icon(name=ft.icons.FRONT_LOADER, size=64, color="#4c8ea6"))
        results_container.controls.append(ft.Text(translate("cpu_ram_test_running").format(current=1, total=3), size=16, weight="bold"))
        results_container.update()

        stop_event = multiprocessing.Event() 
        processes = []

        for test_num in range(1, 4):
            results_container.controls[1] = ft.Text(translate("cpu_ram_test_running").format(current=test_num, total=3), size=16, weight="bold")
            results_container.update()

            for _ in range(num_cores):
                p = multiprocessing.Process(target=cpu_stress, args=(stop_event,))
                processes.append(p)
                p.start()

            time.sleep(20) 
            stop_event.set() 
            for p in processes:
                p.join()  
            stop_event.clear()  

            for _ in range(num_cores):
                p = multiprocessing.Process(target=cpu_relax, args=(stop_event,))
                processes.append(p)
                p.start()

            time.sleep(5)  
            stop_event.set() 
            for p in processes:
                p.join() 
            stop_event.clear()  

            time.sleep(5) 

            mem_process = multiprocessing.Process(target=memory_stress, args=(stop_event,))
            processes.append(mem_process)
            mem_process.start()
            time.sleep(20) 
            stop_event.set() 
            for p in processes:
                p.join() 
            stop_event.clear()  

            mem_process = multiprocessing.Process(target=memory_release, args=(stop_event,))
            processes.append(mem_process)
            mem_process.start()

            time.sleep(5)  
            stop_event.set()  
            for p in processes:
                p.join()  
            stop_event.clear()  

            time.sleep(5)  

            results_container.controls.append(ft.Text(translate("instance_passed").format(current=test_num), size=16, weight="bold"))
            results_container.update()

        results_container.controls.append(ft.Text(translate("test_complete"), size=16, weight="bold"))
        results_container.update()

    except KeyboardInterrupt:
        stop_event.set()
        for p in processes:
            p.join() 

        results_container.update()

if __name__ == "__main__":
    multiprocessing.freeze_support()