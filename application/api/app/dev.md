Mac/Linux
```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install "fastapi[standard]"
fastapi dev main.py
```
Windows
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install "fastapi[standard]"
fastapi dev main.py
```
```cmd
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install "fastapi[standard]"
fastapi dev main.py
```