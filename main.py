from modules.cache_map_sensors import get_cached_cpu_data, start_cache_updater
from modules.hw_monitor import hw_monitor_content, update_hw_monitor_ui
from modules.translations import translate, change_language
from modules.homet import homet_content
from modules.sensors_mapping import SENSOR_MAPPING
from modules.loading import create_loading_component
from modules.hw_tests import hw_tests_content
from modules.report import report_content
from modules.tweaks import tweaks_content
import multiprocessing
import flet as ft
import threading
import requests
import asyncio
import ctypes
import time
import sys
import os
import atexit

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_async_task(coroutine):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(coroutine)
    finally:
        loop.close()

def ui(page: ft.Page):
    page.title = translate("title")
    page.window.icon = os.path.join(BASE_DIR, "assets","icon.ico")
    page.bgcolor = "#1D2024"
    page.padding = 0
    page.window.width = 500
    page.window.height = 650
    page.window.resizable = False
    page.window.maximizable = False
    page.window.center()

    loading_component = create_loading_component(page)

    page.add(
        ft.Stack([
            loading_component,  
        ]),
    )

    current_page = ft.Ref[ft.Column]()
    console_container = ft.Ref[ft.Container]()
    banner_container = ft.Ref[ft.Container]()
    cpu_info_container = ft.Ref[ft.Container]()

    start_bt_ref = ft.Ref[ft.ElevatedButton]()
    reset_bt_ref = ft.Ref[ft.ElevatedButton]()

    console_output = ft.ListView(
        spacing=5,
        auto_scroll=True,
        controls=[
            ft.Text(translate("welcome"), color="#c5f7ff"),
            ft.Text(translate("checking_integrity"), color="#c5f7ff"),
            ft.Text(translate("preparing_scripts"), color="#c5f7ff"),
            ft.Text(translate("initializing_tweaks"), color="#c5f7ff"),
            ft.Text(translate("loading_tests"), color="#c5f7ff"),
            ft.Text(translate("active"), color="#3e7498"),
        ],
        height=100,
    )

    console_header = ft.Row([
        ft.Icon(ft.Icons.TERMINAL, color="#4c8ea6"),
        ft.Text(translate("console_output"), color="#4c8ea6", weight=ft.FontWeight.BOLD)
    ])

    cpu_info_output = ft.ListView(
        spacing=5,
        auto_scroll=True,
        controls=[
            ft.Text(translate("cpu_temp"), color="#c5f7ff"),
            ft.Text(translate("cpu_voltage"), color="#c5f7ff"),
            ft.Text(translate("cpu_clock"), color="#c5f7ff"),
            ft.Text(translate("cpu_load"), color="#c5f7ff"),
        ],
        height=100,
    )

    cpu_info_header = ft.Row([
        ft.Icon(ft.Icons.MEMORY, color="#4c8ea6"),
        ft.Text(translate("cpu_info"), color="#4c8ea6", weight=ft.FontWeight.BOLD)
    ])

    def add_console_message(new_message: str):
        console_output.controls.append(ft.Text(new_message, color="#c5f7ff"))
        console_output.update()

    hw_monitor_layout, status_icon_ref, cpu_list_ref = hw_monitor_content()

    pages = {
        "H.O.M.E.T": homet_content(add_console_message, start_bt_ref, reset_bt_ref),
        "TWEAKS": tweaks_content(add_console_message),
        "HW MONITOR": hw_monitor_layout,
        "HW TESTS": hw_tests_content(),
        "REPORTS": report_content(page),
    }

    def _refresh_texts():
        page.title = translate("title")
        start_bt_ref.current.text = translate("start_optimization")
        reset_bt_ref.current.text = translate("reset_default_values")
        start_bt_ref.current.update()
        reset_bt_ref.current.update()

        console_output.controls[0].value = translate("welcome")
        console_output.controls[1].value = translate("checking_integrity")
        console_output.controls[2].value = translate("preparing_scripts")
        console_output.controls[3].value = translate("initializing_tweaks")
        console_output.controls[4].value = translate("loading_tests")
        console_output.controls[5].value = translate("active")

        console_header.controls[1].value = translate("console_output")

        cpu_info_output.controls[0].value = translate("cpu_temp")
        cpu_info_output.controls[1].value = translate("cpu_voltage")
        cpu_info_output.controls[2].value = translate("cpu_clock")
        cpu_info_output.controls[3].value = translate("cpu_load")

        cpu_info_header.controls[1].value = translate("cpu_info")

        footer_column.controls[0].value = translate("license")
        footer_column.controls[1].value = translate("license_details")

        pages["TWEAKS"] = tweaks_content(add_console_message)

        if nav.selected_index == 2: 
            current_page.current.controls = [pages["TWEAKS"]]

        pages["HW TESTS"] = hw_tests_content()

        pages["REPORTS"] = report_content(page)

        page.update()

    def change_page(index):
        page_names = ["H.O.M.E.T", "HW MONITOR", "TWEAKS", "HW TESTS", "REPORTS"]
        current_page.current.controls = [pages[page_names[index]]]
        if index == 0:
            console_container.current.visible = True
            banner_container.current.visible = True
            cpu_info_container.current.visible = True
        else:
            console_container.current.visible = False
            banner_container.current.visible = False
            cpu_info_container.current.visible = False

        language_menu.visible = index == 0

        if page_names[index] == "HW MONITOR":
            cpu_list_ref.current.controls.clear() 
            threading.Thread(target=run_async_task, args=(update_hw_monitor_ui(page, status_icon_ref, cpu_list_ref),), daemon=True).start()

        page.update()

    nav = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.DEVELOPER_BOARD, label="H.O.M.E.T"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.MONITOR_HEART_OUTLINED, label="HW MONITOR"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.DISPLAY_SETTINGS_OUTLINED, label="TWEAKS"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.FACT_CHECK_OUTLINED, label="HW TESTS"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.ASSIGNMENT_ROUNDED, label="REPORTS"
            ),
        ],
        selected_index=0,
        animation_duration=300,
        on_change=lambda e: change_page(e.control.selected_index),
        shadow_color=ft.Colors.BLACK
    )
    language_menu = ft.PopupMenuButton(
        icon=ft.Icons.LANGUAGE,
        items=[
            ft.PopupMenuItem(text="English", on_click=lambda _: (change_language("en"), _refresh_texts())),
            ft.PopupMenuItem(text="Español", on_click=lambda _: (change_language("es"), _refresh_texts())),
        ]
    )

    footer_column = ft.Column(
        [
            ft.Text(
                translate("license"),
                color="#c5f7ff",
                size=11,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Text(
                translate("license_details"),
                color="#c5f7ff",
                size=8,
                text_align=ft.TextAlign.CENTER
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    footer = ft.Container(
        content=ft.Row(
            [
                footer_column,
                language_menu
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=ft.padding.symmetric(horizontal=10),
        bgcolor="#191C20",
        height=40,
        alignment=ft.alignment.center,
    )

    page.add(
        ft.Column([
            nav,
            ft.Container(
                ref=banner_container,
                content=ft.Image(
                    src=os.path.join(BASE_DIR, "assets","banner.png"),
                    fit=ft.ImageFit.COVER,
                    expand=True,
                ),
                padding=0,
                margin=0,
                width=page.window.width,
                border=ft.Border(
                    left=ft.BorderSide(color="#c5f7ff", width=1),
                    right=ft.BorderSide(color="#c5f7ff", width=1),
                    top=ft.BorderSide(color="#c5f7ff", width=1),
                    bottom=ft.BorderSide(color="#c5f7ff", width=1)
                ),
            ),

            ft.Container(
                content=ft.Column(
                    ref=current_page,
                    scroll="adaptive",  
                ),
                width=500,
                expand=True,
            ),

            ft.Row([
                ft.Container(
                    ref=console_container,
                    content=ft.Column([
                        console_header, 
                        console_output
                    ]),
                    bgcolor="#1D2024",
                    border_radius=20,
                    padding=5,
                    margin=ft.margin.only(left=20, right=5, bottom=5),
                    height=160,
                    width=210,
                    border=ft.Border(
                        left=ft.BorderSide(color="#c5f7ff", width=1),
                        right=ft.BorderSide(color="#c5f7ff", width=1),
                        top=ft.BorderSide(color="#c5f7ff", width=1),
                        bottom=ft.BorderSide(color="#c5f7ff", width=1)
                    ),
                ),

                ft.Container(
                    ref=cpu_info_container,
                    content=ft.Column([
                        cpu_info_header,  
                        cpu_info_output
                    ]),
                    bgcolor="#1D2024",
                    border_radius=20,
                    padding=5,
                    margin=ft.margin.only(left=5, right=20, bottom=5),
                    height=160,
                    width=210,
                    border=ft.Border(
                        left=ft.BorderSide(color="#c5f7ff", width=1),
                        right=ft.BorderSide(color="#c5f7ff", width=1),
                        top=ft.BorderSide(color="#c5f7ff", width=1),
                        bottom=ft.BorderSide(color="#c5f7ff", width=1)
                    ),
                ),
            ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
        ], expand=True, spacing=10),

        footer
    )

    change_page(0)
    console_container.current.visible = True
    banner_container.current.visible = True
    cpu_info_container.current.visible = True

    start_cache_updater()

    def identify_cpu_brand(cpu_name):
        if "Intel" in cpu_name:
            return "Intel"
        elif "AMD" in cpu_name:
            return "AMD"
        else:
            return None

    def update_cpu_info_output():
        while True:
            try:
                data = get_cached_cpu_data()
                if data is None:
                    time.sleep(0.5)
                    continue

                if isinstance(data, dict) and "error" in data:
                    time.sleep(10)
                    continue

                if isinstance(data, list) and len(data) > 0:
                    cpu = data[0]
                    if 'hardwareName' in cpu:
                        cpu_brand = identify_cpu_brand(cpu['hardwareName'])
                        if cpu_brand in SENSOR_MAPPING:
                            mapping = SENSOR_MAPPING[cpu_brand]
                            temperature_sensor = next(
                                (s['value'] for s in cpu['sensors']
                                 if s['sensorType'] == 'Temperature' and 
                                    any(keyword in s['sensorName'] for keyword in mapping['temperature'])),
                                'N/A'
                            )
                            if temperature_sensor != 'N/A':
                                try:
                                    temperature_sensor = float(temperature_sensor)
                                    cpu_info_output.controls[0].value = f"{translate('cpu_temp').split(':')[0]}: {temperature_sensor:.1f} °C"
                                except Exception as ex:
                                    cpu_info_output.controls[0].value = f"{translate('cpu_temp').split(':')[0]}: N/A"
                            else:
                                cpu_info_output.controls[0].value = f"{translate('cpu_temp').split(':')[0]}: N/A"
                            voltage_sensor = next(
                                (s['value'] for s in cpu['sensors']
                                 if s['sensorType'] == 'Voltage' and 
                                    any(keyword in s['sensorName'] for keyword in mapping['voltage'])),
                                'N/A'
                            )
                            if voltage_sensor != 'N/A':
                                try:
                                    voltage_sensor = float(voltage_sensor)
                                    cpu_info_output.controls[1].value = f"{translate('cpu_voltage').split(':')[0]}: {voltage_sensor:.2f} V"
                                except Exception as ex:
                                    cpu_info_output.controls[1].value = f"{translate('cpu_voltage').split(':')[0]}: N/A"
                            else:
                                cpu_info_output.controls[1].value = f"{translate('cpu_voltage').split(':')[0]}: N/A"
                            clock_sensor = next(
                                (s['value'] for s in cpu['sensors']
                                 if s['sensorType'] == 'Clock' and 
                                    any(keyword in s['sensorName'] for keyword in mapping['clock'])),
                                'N/A'
                            )
                            if clock_sensor != 'N/A':
                                try:
                                    clock_sensor = float(clock_sensor) / 1000
                                    cpu_info_output.controls[2].value = f"{translate('cpu_clock').split(':')[0]}: {clock_sensor:.2f} GHz"
                                except Exception as ex:
                                    cpu_info_output.controls[2].value = f"{translate('cpu_clock').split(':')[0]}: N/A"
                            else:
                                cpu_info_output.controls[2].value = f"{translate('cpu_clock').split(':')[0]}: N/A"
                            load_sensor = next(
                                (s['value'] for s in cpu['sensors']
                                 if s['sensorType'] == 'Load' and 
                                    any(keyword in s['sensorName'] for keyword in mapping['load'])),
                                'N/A'
                            )
                            if load_sensor != 'N/A':
                                try:
                                    load_sensor = float(load_sensor)
                                    cpu_info_output.controls[3].value = f"{translate('cpu_load').split(':')[0]}: {load_sensor:.1f} %"
                                except Exception as ex:
                                    cpu_info_output.controls[3].value = f"{translate('cpu_load').split(':')[0]}: N/A"
                            else:
                                cpu_info_output.controls[3].value = f"{translate('cpu_load').split(':')[0]}: N/A"

                        page.update()
            except Exception as e:
                print(f"Error updating CPU info: {e}")
                time.sleep(5)

    threading.Thread(target=update_cpu_info_output, daemon=True).start()

    def initialize_app():
        time.sleep(5)  
        loading_component.visible = False  
        page.update()

    threading.Thread(target=initialize_app, daemon=True).start()

def hide_console():
    if sys.platform == 'win32': 
        kernel32 = ctypes.windll.kernel32
        hwnd = kernel32.GetConsoleWindow()
        if hwnd != 0:
            ctypes.windll.user32.ShowWindow(hwnd, 0) 

def shutdown_api():
    try:
        requests.get("http://localhost:5123/api/hardware/off", timeout=3)
    except requests.exceptions.RequestException as e:
        print(f"Error al apagar la API: {e}")

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)
    multiprocessing.freeze_support()
    hide_console()
    atexit.register(shutdown_api)
    ft.app(target=ui)