import flet as ft
from modules.tests.battery_health import battery_health_test
from modules.tests.cpu_and_ram import cpu_ram_load_test
from modules.tests.cpu_performance import cpu_performance_test
from modules.tests.cpu_stability import cpu_stability_test
from modules.tests.cpu_stress import toggle_cpu_stress_test
from modules.translations import translate  

def hw_tests_content():
    results_container = ft.Column(scroll=ft.ScrollMode.AUTO)

    def add_test_heading(test_name_key):
        results_container.controls.append(
            ft.Text(translate(test_name_key), size=18, weight=ft.FontWeight.BOLD, color="#c5f7ff")
        )
        results_container.update()

    def create_dynamic_button(test_name_key, test_function):
        button = ft.ElevatedButton(
            translate("run_test"),
            on_click=lambda _: toggle_cpu_stress_test(_, results_container, button),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(width=1, color="#4c8ea6"),
                overlay_color="#3e7498",
                padding=10,
            ),
            bgcolor="#3e7498",
            color="#c5f7ff",
            elevation=2,
        )
        return button

    def create_static_button(test_name_key, test_function):
        return ft.ElevatedButton(
            translate("run_test"),
            on_click=lambda _: [add_test_heading(test_name_key), test_function(results_container)],
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(width=1, color="#4c8ea6"),
                overlay_color="#3e7498",
                padding=10,
            ),
            bgcolor="#3e7498",
            color="#c5f7ff",
            elevation=2,
        )

    def create_test_row(icon, test_name_key, test_description_key, test_function):
        is_stress_test = test_function == toggle_cpu_stress_test
        button = create_dynamic_button(test_name_key, test_function) if is_stress_test else create_static_button(
            test_name_key, test_function
        )
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, size=30, color="#4c8ea6"),
                    ft.Column([
                        ft.Text(translate(test_name_key), color="#c5f7ff", weight=ft.FontWeight.BOLD, size=16),
                        ft.Text(translate(test_description_key), color="#c5f7ff", size=12),
                    ], expand=True),
                    button,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Divider(color="#4c8ea6", thickness=1),
            ]),
            padding=20,
        )

    tests = [
        (ft.icons.LOCAL_FIRE_DEPARTMENT, "cpu_stress_test_name", "cpu_stress_test_desc", toggle_cpu_stress_test),
        (ft.icons.FRONT_LOADER, "cpu_ram_load_test_name", "cpu_ram_load_test_desc", cpu_ram_load_test),
        (ft.icons.VIDEO_STABLE, "cpu_stability_test_name", "cpu_stability_test_desc", cpu_stability_test),
        (ft.icons.SPEED, "cpu_performance_test_name", "cpu_performance_test_desc", cpu_performance_test),
        (ft.icons.BATTERY_CHARGING_FULL, "battery_health_test_name", "battery_health_test_desc", battery_health_test),
    ]

    return ft.Container(
        content=ft.Column([
            *[create_test_row(*test) for test in tests],
            ft.Text(translate("test_results"), size=16, weight=ft.FontWeight.BOLD, color="#c5f7ff"),
            results_container,
        ], spacing=20),
        padding=20,
        bgcolor="#1D2024",
        border_radius=10,
        shadow=ft.BoxShadow(blur_radius=10, spread_radius=2, color="#000000", offset=ft.Offset(2, 2)),
    )
