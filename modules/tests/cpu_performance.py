import time
import flet as ft
import multiprocessing
from modules.sensors_mapping import SENSOR_MAPPING
from math import sqrt, sin, cos, log, exp
from modules.translations import translate 
from modules.cache_map_sensors import get_cached_cpu_data

def identify_cpu_brand(cpu_name):
    if "Intel" in cpu_name:
        return "Intel"
    elif "AMD" in cpu_name:
        return "AMD"
    else:
        return None

def get_cpu_temperature():
    try:
        data = get_cached_cpu_data()
        if data and isinstance(data, list):
            cpu = data[0]
            if 'hardwareName' in cpu:
                cpu_brand = identify_cpu_brand(cpu['hardwareName'])
                if cpu_brand in SENSOR_MAPPING:
                    mapping = SENSOR_MAPPING[cpu_brand]
                    temperature_sensor = next(
                        (s['value'] for s in cpu['sensors'] 
                         if s['sensorType'] == 'Temperature' 
                         and any(keyword in s['sensorName'] for keyword in mapping['temperature'])), 
                        'N/A'
                    )
                    if temperature_sensor != 'N/A':
                        return float(temperature_sensor)
    except Exception as e:
        return 70.0

def worker(iterations, queue, progress_queue, process_id, update_steps=5):
    start_time = time.time()
    progress_interval = iterations // update_steps if update_steps > 0 else iterations

    for i in range(1, iterations + 1):
        val = float(i)
        sqrt_i = sqrt(val)
        sin_i = sin(val)
        cos_i = cos(val)
        log_i = log(val + 1)
        exp_val = exp(sin_i * cos_i)

        result = (exp_val * (sqrt_i + log_i) + cos_i * sin_i) * (sqrt(log_i + 1)) + cos(log_i + sqrt_i)
        result += (sqrt_i * sin_i + cos(log_i + exp_val)) * cos(log_i + sin_i)
        _ = result

        if update_steps > 0 and i % progress_interval == 0:
            progress_queue.put((process_id, i / iterations * 100))

    elapsed_time = time.time() - start_time
    progress_queue.put((process_id, 100))
    queue.put(elapsed_time)

def cpu_performance_test(results_container: ft.Column, iterations=3 * 10**7, num_processes=None):
    results_container.controls.clear()
    num_processes = num_processes or multiprocessing.cpu_count()
    
    progress_bar = ft.ProgressBar(width=400, value=0)
    icon = ft.Icon(name=ft.icons.SPEED, size=64, color="#4c8ea6")
    
    results_container.controls.append(
        ft.Text(translate("performance_test_running"), size=16, weight="bold")
    )
    results_container.controls.append(icon)

    results_container.controls.append(
        ft.Text(translate("max_score"), size=14, weight="bold", color='#4c8ea6')
    )

    results_container.controls.append(ft.Divider(color="#4c8ea6", thickness=1))
    
    results_container.controls.append(
        ft.Card(
            elevation=2,
            content=ft.Container(
                padding=10,
                bgcolor="#2C3136",
                border_radius=8,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(name=ft.icons.COMPUTER, color="#4c8ea6", size=20),
                                ft.Text(translate("cpu_reference"), size=14, weight="bold", color='#4c8ea6')
                            ],
                            alignment="start"
                        ),
                        ft.Divider(color="#4c8ea6", thickness=1),
                        ft.Row([
                            ft.Text(translate("model"), size=12, color="#cccccc"),
                            ft.Text("12th Gen Intel Core i7 12650H", size=12, color="#ffffff")
                        ], alignment="spaceBetween"),
                        ft.Row([
                            ft.Text(translate("score"), size=12, color="#cccccc"),
                            ft.Text("858 Pts", size=12, weight="bold", color="#ffffff")
                        ], alignment="spaceBetween"),
                        ft.Row([
                            ft.Text(translate("temperature"), size=12, color="#cccccc"),
                            ft.Text("72 °C", size=12, color="#ffffff")
                        ], alignment="spaceBetween"),
                        ft.Row([
                            ft.Text(translate("total_time"), size=12, color="#cccccc"),
                            ft.Text("601 sec", size=12, color="#ffffff")
                        ], alignment="spaceBetween"),
                        ft.Row([
                            ft.Text(translate("cores"), size=12, color="#cccccc"),
                            ft.Text("16", size=12, color="#ffffff")
                        ], alignment="spaceBetween"),
                    ],
                    spacing=5
                )
            )
        )
    )

    results_container.controls.append(progress_bar)
    results_container.update()

    queue = multiprocessing.Queue()
    progress_queue = multiprocessing.Queue()
    processes = []

    start_time = time.time()
    max_temp_20s = None
    measure_temp_period = 0.5  
    next_temp_measure = time.time() + measure_temp_period
    temp_measure_duration = 20  
    
    for process_id in range(num_processes):
        process = multiprocessing.Process(target=worker, args=(iterations, queue, progress_queue, process_id, 5))
        processes.append(process)
        process.start()

    progress_data = {i: 0 for i in range(num_processes)}
    total_progress = 0

    while total_progress < 100:
        current_time = time.time()
        elapsed = current_time - start_time

        try:
            process_id, progress = progress_queue.get(timeout=0.5)
            progress_data[process_id] = progress
            total_progress = sum(progress_data.values()) / num_processes
            progress_bar.value = total_progress / 100
            results_container.update()
        except:
            pass

        if elapsed <= temp_measure_duration and current_time >= next_temp_measure:
            current_temp = get_cpu_temperature()
            if max_temp_20s is None or current_temp > max_temp_20s:
                max_temp_20s = current_temp
            next_temp_measure = current_time + measure_temp_period

    for process in processes:
        process.join()

    elapsed_times = [queue.get() for _ in range(num_processes)]
    total_time = sum(elapsed_times)

    if max_temp_20s is None:
        max_temp_20s = get_cpu_temperature()

    raw_score = (iterations * num_processes) / (total_time * max_temp_20s)
    final_score = int(raw_score / 10)
    if final_score > 5000:
        final_score = 5000

    progress_bar.value = 1.0
    results_container.controls.append(ft.Text(translate("performance_test_completed"), size=16, weight="bold"))
    results_container.controls.append(ft.Text(translate("cpu_cores_used").format(cores=num_processes), size=12, weight="bold"))
    results_container.controls.append(ft.Text(translate("max_cpu_temp").format(temp=max_temp_20s), size=12, weight="bold"))
    results_container.controls.append(ft.Text(translate("total_time_elapsed").format(time=total_time), size=12, weight="bold"))
    results_container.controls.append(ft.Divider())
    results_container.controls.append(ft.Text(translate("final_score").format(score=final_score), size=20, weight="bold"))
    results_container.update()

if __name__ == "__main__":
    multiprocessing.freeze_support()