import multiprocessing
import flet as ft
from modules.translations import translate 

is_stress_running = False
processes = []

def cpu_stress_test():
    while True:
        _ = sum(i * i for i in range(10000))

def toggle_cpu_stress_test(_, results_container: ft.Column, button: ft.ElevatedButton):
    results_container.controls.clear()
    global is_stress_running, processes

    if is_stress_running:
        for process in processes:
            process.terminate()
        processes = []
        results_container.controls.append(
            ft.Text(translate("test_completed"), size=16, weight="bold")
        )
        button.text = translate("run_test")
        is_stress_running = False
    else:
        icon = ft.Icon(name=ft.icons.LOCAL_FIRE_DEPARTMENT, size=64, color="#4c8ea6")
        results_container.controls.append(icon)
        results_container.controls.append(
            ft.Text(translate("test_initiated"), size=16, weight="bold")
        )
        results_container.update()

        num_cores = multiprocessing.cpu_count()
        for _ in range(num_cores):
            process = multiprocessing.Process(target=cpu_stress_test)
            processes.append(process)
            process.start()

        button.text = translate("stop_test")
        is_stress_running = True

    results_container.update()
    button.update()

if __name__ == "__main__":
    multiprocessing.freeze_support()    