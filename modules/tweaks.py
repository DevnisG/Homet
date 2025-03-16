import flet as ft
import subprocess
from modules.translations import translate

def tweaks_content(add_console_message):
    command_console_output = ft.Text(
        "",
        selectable=True,
        color="#C5F7FF",
        size=14,
        expand=True,
    )

    def add_command_output(msg):
        command_console_output.value += msg + "\n"
        command_console_output.update()

    def add_console_message(msg):
        add_command_output(translate(msg))

    def run_powershell_script(script):
        try:
            subprocess.run(
                ["powershell", "-Command", script],
                capture_output=True,
                text=True
            )
        except Exception as e:
            add_console_message(f"ERROR: {str(e)}")

    def tweak_1(action):
        if action == "apply":
            add_console_message("show_file_extensions")
            script = (
                'reg add "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" '
                '/v HideFileExt /t REG_DWORD /d 0 /f'
            )
            run_powershell_script(script)
        elif action == "undo":
            add_console_message("undo show_file_extensions")
            script = (
                'reg add "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" '
                '/v HideFileExt /t REG_DWORD /d 1 /f'
            )
            run_powershell_script(script)

    def tweak_2(action):
        if action == "apply":
            add_console_message("remove_preinstalled_apps")
            script = "Get-AppxPackage | Remove-AppxPackage"
            run_powershell_script(script)
        elif action == "undo":
            add_console_message("undo remove_preinstalled_apps")
            script = (
                'Get-AppxPackage -AllUsers | ForEach {'
                'Add-AppxPackage -DisableDevelopmentMode -Register "$($_.InstallLocation)\\AppXManifest.xml"'
                '}'
            )
            run_powershell_script(script)

    def tweak_3(action):
        if action == "apply":
            add_console_message("clean_temporary_files")
            script = 'del /q /s %temp%\\*'
            run_powershell_script(script)

    def tweak_4(action):
        if action == "apply":
            add_console_message("disable_start_menu_suggestions")
            script = (
                'reg add "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager" '
                '/v SystemPaneSuggestionsEnabled /t REG_DWORD /d 0 /f'
            )
            run_powershell_script(script)
        elif action == "undo":
            add_console_message("undo disable_start_menu_suggestions")
            script = (
                'reg add "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager" '
                '/v SystemPaneSuggestionsEnabled /t REG_DWORD /d 1 /f'
            )
            run_powershell_script(script)

    def tweak_5(action):
        if action == "apply":
            add_console_message("disable_search_indexing")
            script = 'sc config WSearch start= disabled && net stop WSearch'
            run_powershell_script(script)
        elif action == "undo":
            add_console_message("undo disable_search_indexing")
            script = 'sc config WSearch start= auto && net start WSearch'
            run_powershell_script(script)

    def tweak_6(action):
        if action == "apply":
            add_console_message("enable_fast_startup")
            script = 'powercfg /hibernate on'
            run_powershell_script(script)
        elif action == "undo":
            add_console_message("undo enable_fast_startup")
            script = 'powercfg /hibernate off'
            run_powershell_script(script)

    def tweak_7(action):
        if action == "apply":
            add_console_message("remove_sleep_mode")
            script = 'powercfg -change -standby-timeout-dc 0 && powercfg -change -standby-timeout-ac 0'
            run_powershell_script(script)
        elif action == "undo":
            add_console_message("undo remove_sleep_mode")
            script = 'powercfg -change -standby-timeout-dc 10 && powercfg -change -standby-timeout-ac 10'
            run_powershell_script(script)

    def tweak_8(action):
        if action == "apply":
            add_console_message("open_startup_settings")
            script = "start ms-settings:startupapps"
            run_powershell_script(script)

    def tweak_9(action):
        if action == "apply":
            add_console_message("optimize_appearance")
            script = 'SystemPropertiesPerformance.exe'
            run_powershell_script(script)

    def tweak_10(action):
        if action == "apply":
            add_console_message("empty_recycle_bin")
            script = 'Get-PSDrive -PSProvider FileSystem | ForEach-Object { Clear-RecycleBin -Force -Drive $_.Name }'
            run_powershell_script(script)

    def create_button(text_key, on_click):
        return ft.ElevatedButton(
            translate(text_key),
            on_click=on_click,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=6),
                padding=10,
            ),
            bgcolor="#3e7498",
            color="#C5F7FF",
            width=80,
            height=30,
        )

    def create_tweak_row(icon, name_key, description_key, func, undo=True):
        buttons = [create_button("apply", lambda _: func("apply"))]
        if undo:
            buttons.append(create_button("undo", lambda _: func("undo")))

        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, color="#3e7498"),
                    ft.Column([
                        ft.Text(translate(name_key), color="#c5f7ff", size=14, weight="bold"),
                        ft.Text(translate(description_key), color="#3e7498", size=12)
                    ], expand=True),
                    ft.Row(buttons, spacing=5)
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                expand=True,
            ),
            padding=10,
            border_radius=10,
            bgcolor="#1D2024",
        )

    tweaks = [
        create_tweak_row(
            ft.Icons.VISIBILITY,
            "show_file_extensions",
            "show_file_extensions_desc",
            tweak_1
        ),
        create_tweak_row(
            ft.Icons.DELETE,
            "remove_preinstalled_apps",
            "remove_preinstalled_apps_desc",
            tweak_2
        ),
        create_tweak_row(
            ft.Icons.SNOOZE,
            "remove_sleep_mode",
            "remove_sleep_mode_desc",
            tweak_7
        ),
        create_tweak_row(
            ft.Icons.LIGHTBULB,
            "disable_start_menu_suggestions",
            "disable_start_menu_suggestions_desc",
            tweak_4
        ),
        create_tweak_row(
            ft.Icons.SEARCH,
            "disable_search_indexing",
            "disable_search_indexing_desc",
            tweak_5
        ),
        create_tweak_row(
            ft.Icons.FLASH_ON,
            "enable_fast_startup",
            "enable_fast_startup_desc",
            tweak_6
        ),
        create_tweak_row(
            ft.Icons.DELETE_SWEEP,
            "clean_temporary_files",
            "clean_temporary_files_desc",
            tweak_7,
            undo=False
        ),
         create_tweak_row(
            ft.Icons.SETTINGS_POWER, 
            "open_startup_settings", 
            "open_startup_settings_desc", 
            tweak_8,
            undo=False,
        ),
        create_tweak_row(
            ft.Icons.TUNE,
            "optimize_appearance",
            "optimize_appearance_desc",
            tweak_9,
            undo=False,
        ),
        create_tweak_row(
            ft.Icons.DELETE_FOREVER,
            "empty_recycle_bin",
            "empty_recycle_bin_desc",
            tweak_10,
            undo=False,
        ),
    ]

    console = ft.Container(
        content=ft.Column(
            [
                ft.Text(translate("command_output_console"), color="#4c8ea6", weight="bold", size=16),
                ft.Container(
                    content=command_console_output,
                    width=500,
                    bgcolor="#2C3136",
                    border_radius=8,
                    padding=10,
                    expand=True,
                ),
            ],
            spacing=10,
        ),
        height=200,
        width=500,
        border_radius=8,
        bgcolor="#212429",
        padding=10,
    )

    return ft.Container(
        content=ft.Column(
            [
                ft.Column(tweaks, spacing=10),
                console
            ],
            spacing=20,
            alignment=ft.MainAxisAlignment.START,
        ),
        padding=30,
        bgcolor="#1D2024",
        border_radius=12,
    )