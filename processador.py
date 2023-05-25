import csv
import re
import xml.etree.ElementTree as ET
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import logging
import os
import time

#os.makedirs('logs', exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('logs/processador.log', encoding='utf-8')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

stop_words = set(stopwords.words('english'))

#funçao para limpar, tirar as stowords dos textos e deixar com letra maiusculas
def process_text(text):
    text = re.sub('[^a-zA-Z]', ' ', text)    
    word_tokens = word_tokenize(text)
    filtered_sentence = [w.upper() for w in word_tokens if not w.lower() in stop_words]   

    return filtered_sentence

start_time = time.time()
def processador():
    stem = False
    cfg_file="PC.CFG"
    logger.info(f"Executando o processador.py ")
    # lê o arquivo de configuração
    with open("configs/PC.CFG", "r") as f:
        logger.info(f"Abrindo o aquirvo de configuração {cfg_file}")
        for line in f:
            line = line.rstrip()

            if line == "STEMMER":
                logger.info("Escolhida a configuração de fazer stemming das consultas")                
                stemmer = PorterStemmer()
                stem = True
                continue
            elif line == "NOSTEMMER":
                logger.info("Escolhida a configuração de não fazer stemming das consultas")
                
                continue
            
            if line.startswith("LEIA="):
                xml_file = line.strip()[5:]
            elif line.startswith("CONSULTAS="):
                consultas_file = line.strip()[10:]
            elif line.startswith("ESPERADOS="):
                esperados_file = line.strip()[10:]
            else:
                logger.error(f"Erro ao ler {cfg_file}")
    

    # cria a lista de cabeçalhos para o arquivo de consultas
    consultas_headers = ["QueryNumber", "QueryText"]

    # cria a lista de cabeçalhos para o arquivo de esperados
    esperados_headers = ["QueryNumber", "DocNumber", "DocVotes"]
    
    # processa as consultas e gera os arquivos de saída
    with open(consultas_file, "w", newline="") as f1, open(esperados_file, "w", newline="") as f2:
        logger.info(f'Abrindo o aquivo xml {xml_file}, consultas {consultas_file}  e esperados {esperados_file}')

        # lê o arquivo XML com as consultas
        tree = ET.parse(xml_file)
        root = tree.getroot()
        #variaveis para o log
        row_read_xml=0
        row_written_consultas=0
        row_written_esperados=0
        #configurando os escritores
        writer_consultas = csv.writer(f1, delimiter=";")
        writer_esperados = csv.writer(f2, delimiter=";")

        #colocando os cabeçalhos dos arquivos
        writer_consultas.writerow(consultas_headers)
        writer_esperados.writerow(esperados_headers)
        
        logger.info(f'Processando os arquivos')
        for query in root.iter("QUERY"):
            
            query_number = query.find("QueryNumber").text
            query_text = query.find("QueryText").text
            query_text = process_text(query_text) # remove caracteres especiais
            if stem:
                query_text= [stemmer.stem(word).upper() for word in query_text]
            writer_consultas.writerow([query_number, query_text])
            row_written_consultas+=1
            esperados_rows = []
            record=query.find("Records")
            row_read_xml+=1
            
            
            for item in record.iter("Item"):
                row_written_esperados+=1
                doc_number = item.text
                x=0
                doc_votes = [x:=x+1 for i in item.attrib["score"] if i!="0"][-1]
                esperados_rows.append([query_number, doc_number, doc_votes])
                 
            writer_esperados.writerows(esperados_rows)
    logger.info(f'Fechando o arquivo xml {xml_file}, consultas {consultas_file} e esperados {esperados_file}') 
    end_time = time.time()
    total_time= end_time-start_time
    logger.info(f"Tempo de execução: {total_time}")
    logger.info(f"{row_read_xml} dados lidos do arquivo {xml_file}")
    logger.info(f"{row_written_consultas} linhas escritas em {consultas_file}")
    logger.info(f"{row_written_esperados} linhas escritas em {esperados_file}")
    logger.info(f"Fim do processador")
    
            

if __name__ == "__main__":
    processador()