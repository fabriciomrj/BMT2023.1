import xml.etree.ElementTree as ET
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import csv
import logging
import time
stop_words = set(stopwords.words('english'))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('logs/gerador.log', encoding='utf-8')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
#gerador de lista invertida
def process_text(text):
    text = re.sub('[^a-zA-Z]', ' ', text)    
    word_tokens = word_tokenize(text)
    filtered_sentence = [w.upper() for w in word_tokens if not w.lower() in stop_words]
      
    return filtered_sentence 
# Leitura do arquivo de configuração

start_time = time.time()
def gerador():
    stem=False
    logger.info(f"Iniciando gerador.py ")
    read_files = []

    with open('configs/GLI.CFG', 'r') as f:
        logger.info(f"Lendo o arquivo de configuraçao")
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


            if line.startswith('LEIA='):
                read_files.append(line.strip()[5:])
            elif line.startswith('ESCREVA='):
                inverted_file = line.strip()[8:]



    # Dicionário para armazenar as listas invertidas
    inverted_lists = {}
   
    
    docs_read=0
    # Leitura dos arquivos XML
    for file in read_files:
        logger.info(f"Lendo o arquivo xml{file}")
        tree = ET.parse(file)
        root = tree.getroot()

        for record in root.iter('RECORD'):
            # Leitura dos campos RECORDNUM e ABSTRACT/EXTRACT
            doc_id = re.sub(' ', '', record.find('RECORDNUM').text) 
            docs_read+=1
            try:
                text = record.find('ABSTRACT').text        
            except:
                try:
                    text = record.find('EXTRACT').text
                except:
                    pass
            
            # Processamento do texto e criação da lista de palavras
            words = process_text(text)
            if stem:
                words=[stemmer.stem(w).upper() for w in words]
            # Criação das listas invertidas
            for word in words:
                if word not in inverted_lists:
                    inverted_lists[word] = []

                inverted_lists[word].append(doc_id)

    # Escrita do arquivo de saída
    row_write=0
    with open(inverted_file,'w') as file :
        logger.info(f"Abrindo o arquivo {inverted_file}")
        writer_inverted = csv.writer(file, delimiter=";")
        for word, docs in inverted_lists.items():
            row_write+=1
            writer_inverted.writerow([word,docs])
            
    logger.info(f"fechando o arquivo {inverted_file}")    
    end_time = time.time()
    total_time= end_time-start_time

    
    logger.info(f"documentos lidos: {docs_read}")
    logger.info(f"linhas escritas: {row_write}")
    logger.info(f"Tempo de execução: {total_time}")
    logger.info(f"Fim do gerador")

if __name__ == "__main__":
    gerador()
