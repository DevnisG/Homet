import flet as ft
import threading
import time
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def create_loading_component(page: ft.Page):
    big_chip = ft.Image(
        src=os.path.join(BASE_DIR,"../assets", "logo.png"),
        width=200,
        height=200,
        fit=ft.ImageFit.CONTAIN,
    )
    scanner_container = ft.Container(
        width=150,
        height=50,
        border_radius=10,
        bgcolor="#25292E",
    )
    circuit_image = ft.Image(
        src=os.path.join(BASE_DIR, "../assets", "sensor.png"),
        width=150,
        height=50,
        fit=ft.ImageFit.CONTAIN,
    )
    scanner = ft.Container(
        width=200,
        height=5,
        bgcolor="#4C8EA6",
        border_radius=0,
        opacity=1,
    )
    scanner_container.content = ft.Stack(
        [circuit_image, scanner]
    )
    loading_text = ft.Text(
        "Initializing H.O.M.E.T...",
        color="#C5F7FF",
        size=16,
        weight=ft.FontWeight.W_600,
        text_align=ft.TextAlign.CENTER,
    )

    loading_screen = ft.Container(
        width=480,
        height=560,
        bgcolor=None,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                big_chip,
                ft.Container(height=40),
                scanner_container,
                ft.Container(height=30),
                loading_text,
            ],
        ),
    )

    gradient_background = ft.Container(
        width=page.window.width,
        height=page.window.height,
        gradient=ft.LinearGradient(
            begin=ft.Alignment(0, -1),
            end=ft.Alignment(0, 1),
            colors=["#1D2024", "#2A3035"]
        ),
    )

    container = ft.Stack(
        [gradient_background, loading_screen],
        visible=True, 
    )

    def animate_scanner():
        while container.visible:
            for i in range(-5, 55, 2):
                scanner.top = i
                page.update()
                time.sleep(0.03)
            for i in range(55, -5, -2):
                scanner.top = i
                page.update()
                time.sleep(0.03)

    def update_messages():
        messages = [
            "Initializing API...",
            "Scanning Sensors...",
            "Analyzing Data...",
            "Reading Values...",
        ]
        
        index = 0
        while container.visible:
            loading_text.value = messages[index]
            index = (index + 1) % len(messages)
            page.update()
            time.sleep(1)

    threading.Thread(target=animate_scanner, daemon=True).start()
    threading.Thread(target=update_messages, daemon=True).start()

    return container
