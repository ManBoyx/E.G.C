@echo off
echo ============================================
echo    EGC Suite - Installation Windows
echo ============================================
echo.
echo Installation des dependances...
echo.

pip install PyQt5 PyQtWebEngine Pillow numpy sounddevice

echo.
echo ============================================
echo    Installation terminee !
echo ============================================
echo.
echo Pour lancer EGC Suite:
echo    python launcher.py
echo.
echo Ou lancez directement une application:
echo    python antivirus_scanner.py
echo    python photo_editor.py
echo    python web_browser.py
echo    python audio_amplifier.py
echo.
pause
