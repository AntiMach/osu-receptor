@echo off
python -m pip install pillow > nul 2>&1
python -m osu_receptor
echo Press any key to exit.
pause > nul