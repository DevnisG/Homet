import flet as ft
from modules.translations import translate
from modules.tunner.disable_homet import disable_homet
from modules.tunner.enable_homet import enable_homet
from modules.sensors_mapping import SENSOR_MAPPING

def start_optimization_bt(label_ref, on_click):
    return ft.ElevatedButton(
        ref=label_ref,
        text=translate("start_optimization"),
        icon=ft.icons.SPEED,
        on_click=on_click,
        width=220,
        height=60,
        color="#c5f7ff",
        bgcolor="#1D2024",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=20),
            side=ft.BorderSide(color="#c5f7ff", width=1)
        ),
    )

def reset_default_values_bt(label_ref, on_click):
    return ft.ElevatedButton(
        ref=label_ref,
        text=translate("reset_default_values"),
        icon=ft.icons.SETTINGS_BACKUP_RESTORE_OUTLINED,
        on_click=on_click,
        width=220,
        height=60,
        color="#c5f7ff",
        bgcolor="#1D2024",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=20),
            side=ft.BorderSide(color="#c5f7ff", width=1)
        ),
    )

def homet_content(add_console_message, start_bt_ref, reset_bt_ref):
    return ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                content=start_optimization_bt(
                                    start_bt_ref,
                                    lambda e: run_optimization(add_console_message)
                                ),
                                margin=ft.margin.only(right=5)
                            ),
                            ft.Container(
                                content=reset_default_values_bt(
                                    reset_bt_ref,
                                    lambda e: restore_defaults(add_console_message)
                                ),
                                margin=ft.margin.only(left=5)
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    ),
                ),
            ]
        ),
        padding=10,
    )

def run_optimization(add_console_message):
    try:
        add_console_message(translate("starting_optimization"))
        enable_homet()
        add_console_message(translate("optimization_complete"))
    except Exception as e:
        add_console_message(translate("error_during_optimization").format(error=e))

def restore_defaults(add_console_message):
    try:
        add_console_message(translate("restoring_default_values"))
        disable_homet()
        add_console_message(translate("defaults_restored"))
    except Exception as e:
        add_console_message(translate("error_restoring_defaults").format(error=e))
