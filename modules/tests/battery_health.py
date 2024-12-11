import requests
import flet as ft
from modules.translations import translate 

def battery_health_test(results_container: ft.Container):
    results_container.controls.clear()
    url = "http://localhost:5123/api/hardware/battery"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list):
            for idx, battery_info in enumerate(data):
                sensors = battery_info.get("sensors", [])

                designed_capacity = next((s["value"] for s in sensors if s["sensorName"] == "Designed Capacity"), None)
                fully_charged_capacity = next((s["value"] for s in sensors if s["sensorName"] == "Fully-Charged Capacity"), None)

                if designed_capacity and fully_charged_capacity:
                    health_percentage = int((fully_charged_capacity / designed_capacity) * 100)  

                    if health_percentage > 80:
                        status = translate("good_status")
                        icon = ft.Icon(name=ft.icons.BATTERY_FULL, size=32, color="#4caf50") 
                    elif health_percentage > 60:
                        status = translate("normal_status")
                        icon = ft.Icon(name=ft.icons.BATTERY_3_BAR_ROUNDED, size=32, color="#ffeb3b") 
                    else:
                        status = translate("bad_status")
                        icon = ft.Icon(name=ft.icons.BATTERY_0_BAR, size=32, color="#f44336")  

                    results_container.controls.append(
                        ft.Row(
                            controls=[
                                ft.Icon(name=ft.icons.BATTERY_CHARGING_FULL, size=64, color="#4c8ea6"),
                                ft.Column(
                                    controls=[
                                        ft.Text(translate("health_test_success"), size=16, weight="bold"),
                                        ft.Text(
                                            f"{translate('battery_condition').format(percentage=health_percentage)}\n"
                                            f"{translate('overall_status').format(status=status)}",
                                            size=16,
                                            weight="bold"
                                        ),
                                    ]
                                ),
                                icon
                            ]
                        )
                    )
                else:
                    results_container.controls.append(ft.Text(translate("insufficient_data"), size=16, weight="bold"))
        else:
            results_container.controls.append(ft.Text(translate("unexpected_format"), size=16, weight="bold"))
    except requests.RequestException as e:
        results_container.controls.append(ft.Text(translate("api_error").format(error=str(e)), size=16, weight="bold"))
    except Exception as e:
        results_container.controls.append(ft.Text(translate("unexpected_error").format(error=str(e)), size=16, weight="bold"))

    results_container.update()
