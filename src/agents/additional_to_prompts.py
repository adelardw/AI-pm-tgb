import subprocess

def get_installed_apps_macos():
    cmd = "system_profiler SPApplicationsDataType | grep 'Location:' | awk -F'/' '{print $NF}'"
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return [app.strip().replace('.app','') for app in proc.stdout.splitlines()]

APP_LIST = get_installed_apps_macos()
