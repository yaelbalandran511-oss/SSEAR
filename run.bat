@echo off
REM Ejecutar la aplicación SSEAR usando el Python del virtualenv (Windows)
SETLOCAL
SET BASEDIR=%~dp0
nIF EXIST "%BASEDIR%venv\Scripts\python.exe" (
  "%BASEDIR%venv\Scripts\python.exe" "%BASEDIR%app.py"
) ELSE (
  echo No se encontro el virtualenv en "%BASEDIR%venv\Scripts\python.exe"
  echo Activa tu entorno virtual o ejecuta: python app.py
)
pause
ENDLOCAL
