import sqlite3
import base64
import os
from Cryptodome.Cipher import AES

# --- KONFIGURATION ---
MASTER_KEY_BASE64 = ">>>!!! YOUR MASTER KEY HERE !!!<<<"
DB_FILE = "Edge_Default_Logins.db" 

def decrypt_password(ciphertext, master_key):
    try:
        # IV (Initialisierungsvektor) sind die Bytes 3 bis 15
        iv = ciphertext[3:15]
        payload = ciphertext[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        # Entschlüsseln und Auth-Tag (letzte 16 Bytes) entfernen
        decrypted_pass = cipher.decrypt(payload)[:-16].decode('utf-8', errors='ignore')
        return decrypted_pass
    except Exception as e:
        return f"[Fehler: {e}]"

def main():
    if not os.path.exists(DB_FILE):
        print(f"[-] Datei nicht gefunden: {DB_FILE}")
        return

    # 1. Master Key von Base64 in Bytes umwandeln
    try:
        master_key = base64.b64decode(MASTER_KEY_BASE64)
    except Exception as e:
        print(f"[-] Fehler beim Dekodieren des Master-Keys: {e}")
        return

    # 2. Verbindung zur Datenbank herstellen
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print(f"\n{'URL':<50} | {'Nutzername':<30} | {'Passwort'}")
    print("-" * 110)

    try:
        # Abfrage der Logins aus der Chromium-Tabelle
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        
        for url, user, enc_pw in cursor.fetchall():
            if enc_pw:
                password = decrypt_password(enc_pw, master_key)
                print(f"{url[:50]:<50} | {user[:30]:<30} | {password}")
            else:
                print(f"{url[:50]:<50} | {user[:30]:<30} | [Kein Passwort]")

    except Exception as e:
        print(f"[-] Datenbankfehler: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()