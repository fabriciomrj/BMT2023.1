import ast
import numpy as np
import csv
from collections import  defaultdict
import logging
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('logs/indexador.log', encoding='utf-8')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)



start_time = time.time()
def indexador():
    logger.info(f'Executando o indexador.py')
    tf_idf_cfg='maximo'
    with open('configs/INDEX.CFG', 'r') as file :
        logger.info(f'Abrindo o arquivo de configuração')
        for line in file:
            if line.startswith("LEIA="):
                read_files = line.strip()[5:]
            elif line.startswith('ESCREVA='):
                write_file = line.strip()[8:]
            elif line.startswith('TFIDF='):
                tf_idf_cfg = line.strip()[6:]    
    logger.info(f'tf-idf {tf_idf_cfg}') 
    logger.info(f'fechando o arquivo de configuração')            

    
    words_frequency={}
    max_freq_per_doc={}

    rows_read=0
    words_read=0
    words_write=0
    with open(read_files, 'r') as csv_file:
        logger.info(f'Abrindo o arquivo de {read_files}')
        #configurando reader
        reader = csv.DictReader(csv_file, delimiter=';', lineterminator='\n', fieldnames=['word','documents'])
        
        
        for line in reader:
            rows_read+=1
            word = line['word']
            freq=defaultdict(int)
            #pegas as palavras maiores que 1
            if len(word) > 2:
                words_read+=1
                line_documents = ast.literal_eval(line['documents'])
                
                #calcula a frenquencia da palavra em cada documento
                for doc in line_documents:
                    freq[doc]+=1
                words_frequency[word]=  freq

        #calcula a palavra mais frequente em um documento
        for word, doc_freq in words_frequency.items():
            for doc, freq in doc_freq.items():
                if doc in max_freq_per_doc:
                    if freq > max_freq_per_doc[doc]:
                        max_freq_per_doc[doc] = freq
                else:
                    max_freq_per_doc[doc] = freq             
    logger.info(f'fechando o arquivo de {read_files}')                
    logger.info(f'linhas lidas {rows_read}')
    logger.info(f'palavras lidas {words_read}')               
                
    with open(write_file,'w') as csv_file:
        logger.info(f'Abrindo o arquivo de {read_files}')
        #configurando writer
        writer = csv.writer(csv_file, delimiter=";")

        #escrevendo o cabeçalho da tabela
        writer.writerow(["Word", "DocNumber", "Weight"])

        #calculando tf-idf
        for word in words_frequency:
            for doc in words_frequency[word]:
                words_write+=1
                if tf_idf_cfg=='maximo':            
                    tf= words_frequency[word][doc]/max_freq_per_doc[doc]
                    idf=np.log(len(max_freq_per_doc)/len(words_frequency[word]) )
                weight=tf*idf
                writer.writerow([word,doc,weight])
    end_time = time.time()
    total_time= end_time-start_time
    logger.info(f'Fechando o arquivo de {read_files}')
    logger.info(f'Palavras escritas {words_write}')
    logger.info(f"Tempo de execução: {total_time}")
    logger.info(f'Fim do inbdexador')  

if __name__ == "__main__":
    indexador()              