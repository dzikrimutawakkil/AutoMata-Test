@echo off
echo [*] Cleaning previous build...
rmdir /s /q build
rmdir /s /q dist
del /q MainView.spec

echo [*] Building AutoMata-Test.exe...
pyinstaller --onefile ^
  --name "AutoMata-Test" ^
  --icon=logo.ico ^
  --add-data "logo.ico;." ^
  MainView.py

echo [*] Done. Find AutoMata-Test.exe in the /dist folder.
pause
