import os
import clr
import signal
import sys
import ctypes
from fastapi import FastAPI
from contextlib import asynccontextmanager

def get_executable_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

run_as_admin()

ROOT_DIR = get_executable_dir()
SENSOR_READER_PATH = os.path.join(ROOT_DIR, "core", "SensorReader.dll")

if os.path.exists(SENSOR_READER_PATH):
    clr.AddReference(SENSOR_READER_PATH)
else:
    raise FileNotFoundError(f"No se encontró SensorReader.dll en: {SENSOR_READER_PATH}")

from LibreHardwareMonitor.Hardware import Computer, HardwareType

@asynccontextmanager
async def lifespan(app: FastAPI):
    computer = Computer()
    computer.IsCpuEnabled = True
    computer.IsBatteryEnabled = True
    computer.Open()
    app.state.computer = computer
    yield
    if hasattr(app.state, "computer"):
        computer = app.state.computer
        computer.Close()

app = FastAPI(lifespan=lifespan)

def get_hardware_data(target_type):
    result = []
    computer = app.state.computer if hasattr(app.state, "computer") else None
    if computer is None:
        return result
    for hardware in computer.Hardware:
        if hardware.HardwareType == target_type:
            hardware.Update()
            sensors = []
            for sensor in hardware.Sensors:
                sensors.append({
                    "sensorName": sensor.Name,
                    "value": sensor.Value,
                    "sensorType": str(sensor.SensorType) if sensor.SensorType else None
                })
            result.append({
                "hardwareName": hardware.Name,
                "sensors": sensors
            })
    return result

@app.get("/api/hardware/cpu")
async def cpu_endpoint():
    return get_hardware_data(HardwareType.Cpu)

@app.get("/api/hardware/battery")
async def battery_endpoint():
    return get_hardware_data(HardwareType.Battery)

@app.get("/api/hardware/off")
async def off_endpoint():
    computer = app.state.computer if hasattr(app.state, "computer") else None
    if computer is not None:
        computer.Close()
    os.kill(os.getpid(), signal.SIGINT)
    return {"message": "Cerrando la API de forma controlada..."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5123)
