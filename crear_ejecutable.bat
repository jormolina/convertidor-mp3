@echo off
echo ========================================
echo    Instalando dependencias...
echo ========================================
pip install -r requirements.txt

echo.
echo ========================================
echo    Creando ejecutable...
echo ========================================
pyinstaller --onefile --windowed convertidor.py

echo.
echo ========================================
echo    ¡Listo! El ejecutable esta en la carpeta "dist"
echo ========================================
pause
