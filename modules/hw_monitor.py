import asyncio
import flet as ft
import aiohttp
from modules.translations import translate  

COLOR_PRIMARY = "#c5f7ff"
COLOR_BACKGROUND = "#1D2024"
COLOR_TEXT = "#33667B"
COLOR_CARD = "#1D2024"
COLOR_CARD_BORDER = "#33667B"
COLOR_OK = "#00FF00"
COLOR_ERROR = "#FF0000"

SENSOR_ICONS = {
    "Temperature": (ft.Icon.DEVICE_THERMOSTAT, "temperatures"),
    "Load": (ft.Icon.LINE_WEIGHT, "loads"),
    "Clock": (ft.Icon.WATCH_LATER_OUTLINED, "clocks"),
    "Power": (ft.Icon.POWER, "power"),
    "Voltage": (ft.Icon.ELECTRIC_BOLT, "voltages"),
}

def hw_monitor_content():
    status_icon_ref = ft.Ref[ft.Icon]()
    cpu_list_ref = ft.Ref[ft.ListView]()

    container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icon.CIRCLE, color=COLOR_OK, size=16, ref=status_icon_ref),
                        ft.Text(translate("api_sensors_status"), color=COLOR_TEXT, size=14, weight=ft.FontWeight.W_100),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                    spacing=5,
                ),
                ft.ListView(expand=1, spacing=5, padding=10, ref=cpu_list_ref),
            ],
            expand=True,
        ),
        padding=20,
    )
    return container, status_icon_ref, cpu_list_ref

async def update_hw_monitor_ui(page, status_icon_ref, cpu_list_ref):
    api_url = "http://localhost:5123/api/hardware/cpu"
    data_controls = {}
    while True:
        data = await fetch_cpu_data(api_url)

        status_icon = status_icon_ref.current  
        cpu_list = cpu_list_ref.current  

        if status_icon is None or cpu_list is None:
            break

        if "error" in data:
            status_icon.color = COLOR_ERROR
            cpu_list.controls.clear()
        else:
            status_icon.color = COLOR_OK
            for cpu in data:
                cpu_key = f"cpu_{cpu['hardwareName']}"
                if cpu_key not in data_controls:
                    cpu_card = ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icon.MEMORY, color=COLOR_PRIMARY),
                                        ft.Text(translate("cpu"), size=18, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER, 
                                    spacing=5,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Text(
                                            cpu['hardwareName'],
                                            size=20,
                                            weight=ft.FontWeight.BOLD,
                                            color=COLOR_TEXT,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,  
                                ),
                            ],
                            spacing=10,
                            alignment=ft.MainAxisAlignment.CENTER, 
                        ),
                        bgcolor=COLOR_CARD,
                        border_radius=8,
                        padding=10,
                        border=ft.border.all(1, COLOR_CARD_BORDER),
                        key=cpu_key,
                    )
                    cpu_list.controls.append(cpu_card)
                    data_controls[cpu_key] = cpu_card

                cpu_card = data_controls[cpu_key]
                cpu_column = cpu_card.content

                for category, (icon, description_key) in SENSOR_ICONS.items():
                    matching_sensors = [s for s in cpu['sensors'] if s['sensorType'] == category]

                    if matching_sensors:
                        category_key = f"{cpu_key}_{category}"
                        if category_key not in data_controls:
                            category_card = ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(icon, color=COLOR_PRIMARY),
                                                ft.Text(translate(description_key), size=18, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            spacing=5,
                                        ),
                                    ],
                                    spacing=10,
                                ),
                                bgcolor=COLOR_CARD,
                                border_radius=8,
                                padding=10,
                                border=ft.border.all(1, COLOR_CARD_BORDER),
                                key=category_key,
                            )
                            cpu_column.controls.append(category_card)
                            data_controls[category_key] = category_card

                        category_card = data_controls[category_key]
                        category_column = category_card.content

                        for sensor in matching_sensors:
                            sensor_key = f"{category_key}_{sensor['sensorName']}"
                            if sensor_key not in data_controls:
                                sensor_text = ft.Text("", size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT)
                                category_column.controls.append(sensor_text)
                                data_controls[sensor_key] = sensor_text

                            sensor_value = sensor['value']
                            if category == "Clock":
                                sensor_value = f"{sensor_value / 1000:.2f} GHz"
                            elif category == "Temperature":
                                sensor_value = f"{sensor_value:.1f} °C"
                            elif category == "Load":
                                sensor_value = f"{sensor_value:.1f} %"
                            elif category == "Power":
                                sensor_value = f"{sensor_value:.1f} W"
                            elif category == "Voltage":
                                sensor_value = f"{sensor_value:.2f} V"

                            sensor_text = data_controls[sensor_key]
                            sensor_text.value = f"{sensor['sensorName']}: {sensor_value}"

        page.update()
        await asyncio.sleep(2)

async def fetch_cpu_data(api_url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        return data
                    else:
                        return {"error": translate("invalid_api_data")}
                else:
                    return {"error": translate("error_fetching_data").format(error=response.status)}
    except Exception as e:
        return {"error": translate("error_fetching_data").format(error=str(e))}
