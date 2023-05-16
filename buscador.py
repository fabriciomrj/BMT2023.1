import csv
import ast
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter,defaultdict
import numpy as np
import logging
import time

stop_words = set(stopwords.words('english'))
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('logs/buscador.log', encoding='utf-8')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

start_time = time.time()
def buscador():
    logger.info(f'Executando o buscador.py')
    with open('configs/BUSCA.CFG', 'r') as file :
        logger.info(f'Abrindo o arquivo de configuração')
        for line in file:
            if line.startswith("MODELO="):
                model_file_name = line.strip()[7:]
            elif line.startswith('CONSULTAS='):
                consult_file_name = line.strip()[10:]
            elif line.startswith('RESULTADOS='):
                result_file_name = line.strip()[11:]  
    logger.info(f'fechando o arquivo de configuração') 
    matrix_dict={}            
    rows_read_model=0
    with open(model_file_name) as model_file:
        logger.info(f'Abrindo o arquivo de {model_file_name}')    
        model_reader = csv.DictReader(model_file, delimiter=";",fieldnames=['word','doc','weight'])
        #pulando a linha do cabeçalho
        next(model_reader)
        #montando o dicionario de palavras :{documentos:pesos}
        for line in model_reader:
            rows_read_model+=1
            if line['word'] not in matrix_dict.keys():
                matrix_dict[line['word']] = {line['doc']: float(line['weight'])}
            else:
                matrix_dict[line['word']][line['doc']] = float(line['weight'])
    logger.info(f'Fechando o arquivo de {model_file_name}')  
    logger.info(f'linhas lidas {rows_read_model}')  

    rows_write=0
    rows_read=0
    with open(consult_file_name) as consult_file, open(result_file_name, "w") as result_file:
        logger.info(f'Abrindo o arquivo  {consult_file_name} e {result_file_name}')    
        writer = csv.writer(result_file, delimiter=";")
        writer.writerow(["QueryNumber", "DocRanking", "DocNumber", "Similarity"])
        consult_reader = csv.DictReader(consult_file, delimiter=";",fieldnames=['query_number','query'])
        next(consult_reader)
        debu=0
        for row in consult_reader:
            rows_read+=1   
            debu+=1
            words=ast.literal_eval(row['query'])
            
            word= [word for word in words if len(word) >1]
            
            query=Counter(word)
            query_vec=[]
            
            
            doc_vec={}
            doc_similarity={}
            #fazendo uma matrix documento{ palavra: peso}
            for w in word:
                query_vec.append(query[w])
                if w in matrix_dict:                
                    for doc in matrix_dict[w].keys():
                        
                        if doc not in doc_vec:
                            doc_vec[doc]={w:matrix_dict[w][doc]}
                            
                        else:
                            doc_vec[doc][w]=matrix_dict[w][doc]  
            #calculo do coseno
            for i in doc_vec:
                d=[]
                q=[]
                produto=0
                cos=0
                for j in query:
                    q.append(query[j])
                    
                    if j in doc_vec[i].keys():
                        produto+=query[j]*doc_vec[i][j]
                        d.append(doc_vec[i][j])
                cos=produto/(np.linalg.norm(d)*np.linalg.norm(q))                
                doc_similarity[str(i)]=cos
            count=0
            
            doc_similarity=sorted(doc_similarity.items(), key= lambda x:x[1], reverse =True)
            for i in doc_similarity:
                count+=1
                writer.writerow([row['query_number'],count,i[0],i[1]])
                rows_write+=1
    logger.info(f'Fechando o arquivo  {consult_file_name} e {result_file_name}')    
    end_time = time.time()
    total_time= end_time-start_time
    logger.info(f'linhas lidas {rows_read}')
    logger.info(f'linhas escritas {rows_write}')
    logger.info(f"Tempo de execução: {total_time}")
    logger.info(f'Fim do Buscador')            

if __name__ == "__main__":
    buscador()              