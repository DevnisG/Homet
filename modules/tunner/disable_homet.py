import winreg as reg
import subprocess
import ctypes
import sys

def run_command(command_args):
    try:
        result = subprocess.run(command_args, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"Error : {' '.join(command_args)}\n{result.stderr}")
    except Exception as e:
        print(f"Excep: {' '.join(command_args)}\n{e}")
    return None
 
def modify_registry(path, name, value):
    try:
        with reg.OpenKey(reg.HKEY_LOCAL_MACHINE, path, 0, reg.KEY_SET_VALUE) as key:
            reg.SetValueEx(key, name, 0, reg.REG_DWORD, value)
            print(f"HKLM\\{path}\\{name} = {value}")
    except FileNotFoundError:
        try:
            with reg.CreateKey(reg.HKEY_LOCAL_MACHINE, path) as key:
                reg.SetValueEx(key, name, 0, reg.REG_DWORD, value)
                print(f"HKLM\\{path}\\{name} = {value}")
        except Exception as e:
            print(f"HKLM\\{path}\\{name}\n{e}")
            
    except Exception as e:
        print(f"Error HKLM\\{path}\\{name}\n{e}")

def disable_homet():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        sys.exit(1)

    run_command(["powercfg", "-restoredefaultschemes"])

    balanced_guid = "381b4222-f694-41f0-9685-ff5bb260df2e"

    run_command(["powercfg", "-setactive", balanced_guid])

    reg_path_advanced = r"SYSTEM\CurrentControlSet\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\be337238-0d82-4146-a960-4f3749d470c7"
    modify_registry(reg_path_advanced, "Attributes", 1)

    reg_path_fastboot = r"SYSTEM\CurrentControlSet\Control\Session Manager\Power"
    modify_registry(reg_path_fastboot, "HiberbootEnabled", 1)

if __name__ == "__main__":
    disable_homet()