from processador import processador
from gerador import gerador
from indexador import indexador
from buscador import buscador
import logging
import time

logging.basicConfig(level=logging.INFO, filename='logs/main.log', format='%(asctime)s - %(levelname)s - %(message)s')
start_time = time.time()
def main():
    logging.info(f'Iniciando o Programa')
    try:
        processador()
    except Exception as error:
        logging.erro(f'Error ao executar o processador {error}')
        exit()

    try:
        gerador()
    except Exception as error:
        logging.erro(f'Error ao executar o gerador {error}')

    try:
        indexador()
    except Exception as error:
        logging.erro(f'Error ao executar o indexador {error}')  
    
    try:
        buscador()
    except Exception as error:
        logging.erro(f'Error ao executar o buscador {error}')  

         
    end_time = time.time()
    total_time= end_time-start_time
    logging.info(f"Tempo de execução: {total_time}")
    logging.info(f'Fim do Programa') 
if __name__ == "__main__":
    main()    