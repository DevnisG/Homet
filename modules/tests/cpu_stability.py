import multiprocessing
import time
import flet as ft
from modules.translations import translate 

def calculate_pi(iterations):
    pi = 0.0
    for i in range(iterations):
        pi += (-1) ** i / (2 * i + 1)
    return pi * 4

def worker(iterations, queue):
    result = calculate_pi(iterations)
    queue.put(result)

def cpu_stability_test(results_container: ft.Column, iterations=10**6, tests=5):
    results_container.controls.clear()
    num_cores = multiprocessing.cpu_count()
    expected_pi = 3.141592653589793

    icon = ft.Icon(name=ft.icons.VIDEO_STABLE, size=64, color="#4c8ea6")
    results_container.controls.append(icon)

    test_message = ft.Text(translate("stability_test_start"), size=16, weight="bold")
    results_container.controls.append(test_message)
    results_container.update()

    for test_run in range(tests):
        test_message.value = translate("stability_test_running").format(current=test_run + 1, total=tests)
        results_container.update()

        queue = multiprocessing.Queue()
        processes = []

        for _ in range(num_cores):
            process = multiprocessing.Process(target=worker, args=(iterations, queue))
            processes.append(process)
            process.start()

        results = [queue.get() for _ in range(num_cores)]
        for process in processes:
            process.join()

        passed_instance = False
        for idx, result in enumerate(results):
            if abs(result - expected_pi) <= 0.0001:
                passed_instance = True

        if passed_instance:
            results_container.controls.append(
                ft.Text(translate("instance_passed").format(current=test_run + 1), size=16, weight="bold")
            )
            results_container.update()

        time.sleep(2)

    results_container.controls.append(ft.Text(translate("test_complete"), size=16, weight="bold"))
    results_container.update()

if __name__ == "__main__":
    multiprocessing.freeze_support()