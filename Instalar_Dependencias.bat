@echo off
color 0A
echo =======================================================
echo    INSTALADOR AUTOMATICO - SISTEMA DE ARBITRAGEM
echo =======================================================
echo.
echo [1/2] Instalando as bibliotecas visuais do Painel...
pip install -r black_dashboard\requirements.txt

echo.
echo [2/2] Instalando o motor de Inteligencia do Robo...
pip install -r immike_bot\requirements.txt

echo.
echo =======================================================
echo INSTALACAO CONCLUIDA COM SUCESSO!
echo =======================================================
echo.
echo Voce ja pode fechar esta tela e dar dois cliques 
echo no arquivo "start_all.py" para iniciar o sistema!
echo.
pause
