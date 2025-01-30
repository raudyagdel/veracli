# veracli
VeraCode CLI Tools

Step 1 - Install Dependencies
pip install -r requirements.txt
wine pip install -r requirements.txt

Step 2: Convert the Script to an Executable (VeraCli)
pyinstaller --onefile --icon=veracli.ico veracli.py
wine pyinstaller --onefile --icon=veracli.ico veracli.py


Step 3: Convert the Script to an Executable (VeraReport)
pyinstaller --onefile --icon=veracli.ico license.py -n verareport
wine pyinstaller --onefile --icon=veracli.ico license.py -n verareport

#How To Use
veracli.exe --type archive --source arhive-file.[zip, rar, tar, gzip and others]