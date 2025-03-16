from datetime import datetime
import flet as ft
import subprocess
import pythoncom
import platform
import psutil
import socket
import json
import wmi
from modules.translations import translate

def report_content(page: ft.Page):
    pythoncom.CoInitialize()
    c = wmi.WMI()

    def safe_get_property(func, default="N/A"):
        try:
            return func()
        except Exception:
            return default

    def data_to_text(data, indent=0):
        if isinstance(data, dict):
            lines = []
            for k, v in data.items():
                if isinstance(v, (dict, list)):
                    sub = data_to_text(v, indent + 2)
                    lines.append(f"{' ' * indent}{k}:\n{sub}")
                else:
                    lines.append(f"{' ' * indent}{k}: {v}")
            return "\n".join(lines)
        elif isinstance(data, list):
            lines = []
            for item in data:
                if isinstance(item, dict):
                    sub = data_to_text(item, indent + 2)
                    lines.append(f"{' ' * indent}- {sub}")
                else:
                    lines.append(f"{' ' * indent}- {item}")
            return "\n".join(lines)
        else:
            return f"{' ' * indent}{str(data)}"

    icons_map = {
        translate("operating_system"): ft.icons.WINDOW,
        translate("processor"): ft.icons.MEMORY,
        translate("ram"): ft.icons.SD_CARD,
        translate("drives"): ft.icons.STORAGE,
        translate("network_interfaces"): ft.icons.WIFI,
        translate("graphics_cards"): ft.icons.VIDEO_LABEL_OUTLINED,
        translate("bios"): ft.icons.INFO,
        translate("os_installation_date"): ft.icons.INSTALL_DESKTOP,
        translate("motherboard"): ft.icons.DASHBOARD, 
    }

    def create_label_value_row(label, value):
        return ft.Row(
            [
                ft.Text(f"{label}: ", color="#c5f7ff", weight=ft.FontWeight.BOLD),
                ft.Text(str(value), color="#c5f7ff"),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def copy_section_data(section_data):
        text = data_to_text(section_data)
        page.set_clipboard(text)
        page.snack_bar = ft.SnackBar(
            ft.Text(translate("copy_section_snackbar"), color="#ffffff"),
            bgcolor="#3e7498",
        )
        page.snack_bar.open = True
        page.update()

    def run_powershell(cmd):
        try:
            completed = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True,
                check=True
            )
            return completed.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error al ejecutar el comando: {cmd}\n{e}")
            return None

    def get_gpu_info_powershell():
        cmd = "Get-CimInstance -ClassName Win32_VideoController | Select-Object Name, AdapterRAM, DriverVersion, VideoProcessor, Status | ConvertTo-Json"
        output = run_powershell(cmd)
        if output:
            try:
                gpus = json.loads(output)
                if isinstance(gpus, dict):
                    gpus = [gpus] 
                gpu_list = []
                for gpu in gpus:
                    try:
                        gpu_list.append({
                            translate("video_processor"): gpu.get('VideoProcessor', 'N/A'),
                            translate("driver"): gpu.get('DriverVersion', 'N/A'),
                        })
                    except:
                        continue
                return gpu_list
            except json.JSONDecodeError as e:
                print(f"Error al decodificar JSON para GPU: {e}")
                return []
        return []

    def get_motherboard_info_powershell():
        cmd = "Get-CimInstance -ClassName Win32_BaseBoard | Select-Object Manufacturer, Product, SerialNumber | ConvertTo-Json"
        output = run_powershell(cmd)
        if output:
            try:
                mb = json.loads(output)
                if isinstance(mb, dict):
                    mb = [mb] 
                motherboard_info = []
                for board in mb:
                    motherboard_info.append({
                        translate("manufacturer"): board.get('Manufacturer', 'N/A'),
                        translate("product"): board.get('Product', 'N/A'),
                        translate("serial_number"): board.get('SerialNumber', 'N/A')
                    })
                return motherboard_info
            except json.JSONDecodeError as e:
                print(f"Error al decodificar JSON para Motherboard: {e}")
                return []
        return []

    os_system = safe_get_property(lambda: platform.system())
    os_release = safe_get_property(lambda: platform.release())
    os_version = safe_get_property(lambda: platform.version())
    architecture = safe_get_property(lambda: platform.architecture()[0])
    hostname = safe_get_property(lambda: platform.node())

    cpu_name = safe_get_property(lambda: c.Win32_Processor()[0].Name.strip())
    physical_cores = safe_get_property(lambda: psutil.cpu_count(logical=False))
    logical_cores = safe_get_property(lambda: psutil.cpu_count(logical=True))
    max_frequency = safe_get_property(lambda: psutil.cpu_freq().max)

    mem_total = safe_get_property(lambda: psutil.virtual_memory().total / (1024 ** 3))
    mem_total = int(round(mem_total))

    disks = []
    for disk in psutil.disk_partitions():
        try:
            total = psutil.disk_usage(disk.mountpoint).total / (1024 ** 3)
            used = psutil.disk_usage(disk.mountpoint).used / (1024 ** 3)
            free = psutil.disk_usage(disk.mountpoint).free / (1024 ** 3)
            total = int(round(total))
            used = int(round(used))
            free = int(round(free))
            disks.append({
                translate("total"): f"{total} GB",
                translate("used"): f"{used} GB",
                translate("free"): f"{free} GB",
            })
        except:
            pass

    interfaces = []
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                ip_address = addr.address
                netmask = addr.netmask
                interfaces.append({
                    translate("ip"): ip_address,
                    translate("mask"): netmask,
                })

    gpus = get_gpu_info_powershell()

    motherboard_info = get_motherboard_info_powershell()

    bios_info = []
    for bios in c.Win32_BIOS():
        bios_version = safe_get_property(lambda: bios.SMBIOSBIOSVersion)
        bios_manufacturer = safe_get_property(lambda: bios.Manufacturer)
        bios_release_date = safe_get_property(lambda: bios.ReleaseDate)
        serial_number = safe_get_property(lambda: bios.SerialNumber)
        bios_info.append({
            translate("bios_version"): bios_version,
            translate("bios_manufacturer"): bios_manufacturer,
            translate("bios_date"): bios_release_date,
            translate("serial_number"): serial_number,
        })

    install_date_list = []
    for os_obj in c.Win32_OperatingSystem():
        install_date_str = safe_get_property(lambda: os_obj.InstallDate.split('.')[0])
        install_date = "N/A"
        if install_date_str != "N/A":
            try:
                install_date_parsed = datetime.strptime(install_date_str, '%Y%m%d%H%M%S')
                install_date = str(install_date_parsed)
            except:
                install_date = "N/A"
        install_date_list.append({translate("installation_date"): install_date})

    system_data = {
        translate("operating_system"): {
            translate("hostname"): hostname,
            translate("architecture"): architecture,
            translate("system"): f"{os_system} {os_release}",
            translate("version"): os_version,
        },
        translate("processor"): {
            translate("model"): cpu_name,
            translate("physical_cores"): physical_cores,
            translate("logical_cores"): logical_cores,
            translate("max_frequency"): f"{max_frequency} MHz",
        },
        translate("ram"): {translate("total"): f"{mem_total} GB"},
        translate("drives"): disks,
        translate("network_interfaces"): interfaces,
        translate("graphics_cards"): gpus,
        translate("bios"): bios_info,
        translate("os_installation_date"): install_date_list,
    }

    if motherboard_info:
        system_data[translate("motherboard")] = motherboard_info

    def on_file_save_result(e: ft.FilePickerResultEvent):
        if e.path:
            if not e.path.lower().endswith(".txt"):
                e.path += ".txt"

            text = data_to_text(system_data)
            try:
                with open(e.path, "w", encoding="utf-8") as f:
                    f.write(text)
                page.snack_bar = ft.SnackBar(
                    ft.Text(translate("save_snackbar"), color="#ffffff"),
                    bgcolor="#3e7498"
                )
                page.snack_bar.open = True
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"Error: {ex}", color="#ffffff"), bgcolor="#b71c1c"
                )
                page.snack_bar.open = True
                page.update()

    file_picker = ft.FilePicker(on_result=on_file_save_result)
    page.overlay.append(file_picker)

    sections_widgets = []
    for section_name, section_data in system_data.items():
        icon = icons_map.get(section_name, ft.icons.INFO)

        copy_button = ft.IconButton(
            icon=ft.icons.COPY,
            tooltip=translate("copy_tooltip"),
            icon_color="#4c8ea6",
            on_click=lambda e, data=section_data: copy_section_data(data),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=6),
                bgcolor="#1D2024",
                padding=ft.padding.all(5),
            ),
        )

        title_row = ft.Row(
            [
                ft.Icon(icon, color="#4c8ea6", size=25),
                ft.Text(section_name, size=20, color="#c5f7ff", weight=ft.FontWeight.BOLD),
                copy_button,
            ],
            spacing=10,
        )

        content_items = []
        if isinstance(section_data, dict):
            for key, value in section_data.items():
                content_items.append(create_label_value_row(key, value))
        elif isinstance(section_data, list):
            for item in section_data:
                if isinstance(item, dict):
                    item_rows = []
                    for k, v in item.items():
                        item_rows.append(create_label_value_row(k, v))
                    content_items.append(
                        ft.Container(
                            content=ft.Column(item_rows, spacing=3),
                            bgcolor="#1D2024",
                            padding=10,
                            border_radius=8,
                        )
                    )
                else:
                    content_items.append(create_label_value_row("", item))
        else:
            content_items.append(create_label_value_row("", section_data))

        content_column = ft.Column(content_items, spacing=10)
        sections_widgets.append(ft.Column([title_row, content_column], spacing=10))

    single_card = ft.Card(
        content=ft.Container(
            content=ft.Column(sections_widgets, spacing=10),
            padding=10,
            border_radius=10,
            bgcolor="#1D2024",
        ),
        elevation=3,
    )

    def copy_to_clipboard(e):
        text = data_to_text(system_data)
        page.set_clipboard(text)
        page.snack_bar = ft.SnackBar(
            ft.Text(translate("copy_snackbar"), color="#ffffff"), bgcolor="#3e7498"
        )
        page.snack_bar.open = True
        page.update()

    def save_to_file(e):
        file_picker.save_file(allowed_extensions=["txt"])

    content = ft.Column(
        [
            ft.Container(
                content=single_card,
                expand=True,
                padding=10,
            )
        ],
        spacing=10,
    )

    footer = ft.Container(
        content=ft.Row(
            [
                ft.ElevatedButton(
                    translate("copy"),
                    icon=ft.icons.COPY,
                    on_click=copy_to_clipboard,
                    style=ft.ButtonStyle(
                        color="#c5f7ff",
                        bgcolor="#4c8ea6",
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
                ft.ElevatedButton(
                    translate("save"),
                    icon=ft.icons.SAVE,
                    on_click=save_to_file,
                    style=ft.ButtonStyle(
                        color="#c5f7ff",
                        bgcolor="#4c8ea6",
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor="#1D2024",
        padding=10,
    )

    return ft.Column([content, footer], expand=True, spacing=0)
