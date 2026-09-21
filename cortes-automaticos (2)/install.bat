@echo off
title Instalando Cortes Automaticos
echo.
echo ==========================================
echo   Instalando Cortes Automaticos
echo ==========================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERRO] Python nao foi encontrado.
    echo Baixe e instale o Python 3.11 em: https://www.python.org/downloads/
    echo IMPORTANTE: marque a opcao "Add python.exe to PATH" durante a instalacao.
    pause
    exit /b 1
)

echo [1/4] Criando ambiente virtual...
python -m venv venv

echo [2/4] Instalando dependencias Python (isso pode demorar alguns minutos)...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo [3/4] Verificando ffmpeg...
where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo [AVISO] ffmpeg nao foi encontrado no seu PC.
    echo Baixe em: https://www.gyan.dev/ffmpeg/builds/ ^(versao "release essentials"^)
    echo Depois de baixar, extraia e adicione a pasta "bin" nas Variaveis de Ambiente ^(PATH^) do Windows.
    echo.
)

echo [4/4] Verificando Ollama ^(IA local^)...
where ollama >nul 2>nul
if %errorlevel% neq 0 (
    echo [AVISO] Ollama nao foi encontrado no seu PC.
    echo Baixe e instale em: https://ollama.com/download
    echo Depois de instalar, abra um terminal e rode: ollama pull llama3.2
    echo.
) else (
    echo Baixando o modelo de IA ^(llama3.2^), isso so acontece uma vez...
    ollama pull llama3.2
)

echo.
echo ==========================================
echo   Instalacao concluida!
echo   Rode o arquivo run.bat para abrir a ferramenta.
echo ==========================================
pause
