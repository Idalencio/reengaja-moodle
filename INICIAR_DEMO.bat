@echo off
cd /d "%~dp0"
docker compose up -d --build --wait --wait-timeout 180
if errorlevel 1 (
  echo Verifique se o Docker Desktop esta instalado e iniciado.
  pause
  exit /b 1
)
start http://localhost:8025
echo A primeira inicializacao pode levar alguns minutos.
echo Veja o estado com: docker compose ps
pause
