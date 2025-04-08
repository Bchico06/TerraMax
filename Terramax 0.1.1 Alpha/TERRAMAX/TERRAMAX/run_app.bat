@echo off
echo Iniciando TERRAMAX - Sistema de Gestión Veterinaria...
echo.
echo Este script verificará las dependencias necesarias e iniciará el sistema.
echo.

REM Verificar si Python está instalado
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no está instalado o no se encuentra en el PATH.
    echo Por favor, instale Python desde https://www.python.org/downloads/
    echo Asegúrese de marcar la opción "Add Python to PATH" durante la instalación.
    pause
    exit /b 1
)

REM Verificar e instalar dependencias si es necesario
echo Verificando dependencias...
python -c "import tkcalendar" > nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando dependencia requerida: tkcalendar
    pip install tkcalendar
    if %errorlevel% neq 0 (
        echo ERROR: No se pudo instalar tkcalendar.
        echo Intente ejecutar manualmente: pip install tkcalendar
        pause
        exit /b 1
    )
    echo Dependencia instalada correctamente.
)

echo Todas las dependencias están instaladas.
echo.
echo Iniciando sistema TERRAMAX...
echo.

REM Ejecutar el sistema
python LOGIN.PY

pause 