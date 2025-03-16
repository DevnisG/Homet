import winreg as reg
import subprocess
import ctypes
import sys
import re

def run_command(command_args):
    try:
        result = subprocess.run(command_args, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"Error: {' '.join(command_args)}\n{result.stderr}")
    except Exception as e:
        print(f"Error: {' '.join(command_args)}\n{e}")
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
            print(f"Error: HKLM\\{path}\\{name}\n{e}")
    except Exception as e:
        print(f"Error: HKLM\\{path}\\{name}\n{e}")


def extract_guid(output):
    if not output:
        return None
    match = re.search(r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}", output)
    return match.group(0) if match else None


def scheme_exists(guid):
    output = run_command(["powercfg", "-list"])
    return (output and guid.lower() in output.lower())


def ensure_base_scheme():
    HIGH_PERF_GUID = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
    BALANCED_GUID = "381b4222-f694-41f0-9685-ff5bb260df2e"

    if scheme_exists(HIGH_PERF_GUID):
        return HIGH_PERF_GUID

    run_command(["powercfg", "-restoredefaultschemes"])

    if scheme_exists(HIGH_PERF_GUID):
        return HIGH_PERF_GUID

    dup_output = run_command(["powercfg", "-duplicatescheme", BALANCED_GUID])
    new_guid = extract_guid(dup_output)
    if not new_guid:
        return None

    run_command(["powercfg", "-changename", new_guid, "HOMET_BASE_PLAN"])
    return new_guid


def setting_exists_in_plan(plan_guid, subgroup_guid, setting_guid):
    output = run_command(["powercfg", "-q", plan_guid])
    if output:
        if subgroup_guid.lower() in output.lower() and setting_guid.lower() in output.lower():
            return True
    return False

def enable_homet():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        sys.exit(1)

    base_scheme_guid = ensure_base_scheme()
    if not base_scheme_guid:
        return

    reg_path_advanced = r"SYSTEM\CurrentControlSet\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\be337238-0d82-4146-a960-4f3749d470c7"
    modify_registry(reg_path_advanced, "Attributes", 2)

    output = run_command(["powercfg", "-duplicatescheme", base_scheme_guid])
    plan_guid = extract_guid(output)
    if plan_guid:
        run_command(["powercfg", "-changename", plan_guid, "HOMET_POWER_PLAN"])
    else:
        return

    processor_subgroup = "54533251-82be-4824-96c1-47b60b740d00"
    core_parking_guid = "0cc5b647-c1df-4637-891a-dec35c318583"
    max_cpu_guid = "bc5038f7-23e0-4960-96da-33abaf5935ec"
    boost_mode_guid = "be337238-0d82-4146-a960-4f3749d470c7"
    lid_subgroup_guid = "4f971e89-eebd-4455-a8de-9e59040e7347" 
    lid_action_guid = "5ca83367-6e45-459f-a27b-476b1d01c936"   

    run_command(["powercfg", "-setacvalueindex", plan_guid, processor_subgroup, core_parking_guid, "100"])
    run_command(["powercfg", "-setdcvalueindex", plan_guid, processor_subgroup, core_parking_guid, "100"])

    run_command(["powercfg", "-setacvalueindex", plan_guid, processor_subgroup, max_cpu_guid, "98"])
    run_command(["powercfg", "-setdcvalueindex", plan_guid, processor_subgroup, max_cpu_guid, "98"])

    run_command(["powercfg", "-setacvalueindex", plan_guid, processor_subgroup, boost_mode_guid, "0"])
    run_command(["powercfg", "-setdcvalueindex", plan_guid, processor_subgroup, boost_mode_guid, "0"])

    reg_path_fastboot = r"SYSTEM\CurrentControlSet\Control\Session Manager\Power"
    modify_registry(reg_path_fastboot, "HiberbootEnabled", 0)

    if setting_exists_in_plan(plan_guid, lid_subgroup_guid, lid_action_guid):
        run_command(["powercfg", "-setacvalueindex", plan_guid, lid_subgroup_guid, lid_action_guid, "0"])
        run_command(["powercfg", "-setdcvalueindex", plan_guid, lid_subgroup_guid, lid_action_guid, "0"])
    else:
        pass

    run_command(["powercfg", "-setactive", plan_guid])

if __name__ == "__main__":
    enable_homet()
