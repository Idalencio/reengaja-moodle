@echo off
cd /d "%~dp0"
docker compose run --build --rm testes
pause
