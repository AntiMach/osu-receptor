@echo off
python -m pip install pyinstaller pillow > nul 2>&1
pyinstaller --distpath . -y --clean --icon=osu_receptor.ico -F osu_receptor.py
pause