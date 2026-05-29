import subprocess
import time
import os
import sys

def main():
    print("Iniciando Motor de Arbitragem (ImMike API) na porta 8000...")
    bot_process = subprocess.Popen(
        [sys.executable, "run_with_dashboard.py", "--port", "8000"],
        cwd=r"c:\Users\99196\OneDrive\Documentos\SISTEMA DE ARBITRAGE\immike_bot"
    )
    
    print("Iniciando Black Dashboard Flask na porta 5000...")
    flask_process = subprocess.Popen(
        [sys.executable, "run.py"],
        cwd=r"c:\Users\99196\OneDrive\Documentos\SISTEMA DE ARBITRAGE\black_dashboard"
    )
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Encerrando sistemas...")
        bot_process.terminate()
        flask_process.terminate()

if __name__ == "__main__":
    main()
