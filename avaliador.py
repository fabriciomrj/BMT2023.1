import csv
from collections import defaultdict
import pandas as pd
import math
import matplotlib.pyplot as plt


def avaliador(result_arquive):
    with open("results/esperados.csv") as esperados_csv:
            reader = csv.DictReader(esperados_csv, delimiter=';', lineterminator='\n', fieldnames=['QueryNumber','DocNumber','DocVotes'])
            esperado_dic = defaultdict(dict)
            next(reader)
            for line in reader:
            
                esperado_dic[line['QueryNumber']].update({int(line['DocNumber']):line['DocVotes']})

    result_dic = defaultdict(dict)

    with open(f'results/{result_arquive}') as result_csv:
        next(result_csv)
        
        reader = csv.DictReader(result_csv, delimiter=';', lineterminator='\n', fieldnames=['QueryNumber','DocRanking','DocNumber','Similarity'])
        next(reader)
        count=0
        for line in reader:        
            
            query_num = line['QueryNumber']
            doc_rank = line['DocRanking']
            doc_num=int(line['DocNumber'])
            doc_sim=line['Similarity']
            
            result_dic[query_num].update({doc_num:doc_sim})



    
    R_precision = []
    precision_table = pd.DataFrame(0.0, index=range(1,101) ,columns=["precision@5","precision@10"])
    precision_mean = 0
    mean_of_mean_precision = 0
    DCG = [0]*10
    media_dcg = [0]*10
    rr = 0
    media_rr = 0

    eleven_recall_total = [0]*11
    eleven_recall_consulta = [0]*11

    from sklearn.metrics import f1_score

    f1_scores = []

    for query,relevant in  result_dic.items():

        precision_mean = 0
        dic_consulta = esperado_dic[query]
        num_recover = 0.0
        num_recover_relevance = 0.0
        num_relevances = len(dic_consulta)

        y_true = []
        y_pred = []
        for doc in relevant:

            num_recover += 1      
            if doc in dic_consulta.keys(): 
                num_recover_relevance += 1
                y_true.append(1)
            else:
                y_true.append(0)

            y_pred.append(1)

            if num_recover == num_relevances:
                # Calcular F1 Score para essa consulta
                f1 = f1_score(y_true, y_pred)
                f1_scores.append(f1) 

            precision = 100*(num_recover_relevance/num_recover)
            recall = math.floor(100*(num_recover_relevance/num_relevances))  / 10
            recall = int(recall)
            eleven_recall_consulta[recall] = max(eleven_recall_consulta[recall],precision)

            if num_recover == 5:
                query = int(query)
                precision_table.loc[query]['precision@5'] = precision/100

            if num_recover == 10:
                query = int(query)
                precision_table.loc[query]['precision@10'] = precision/100
            
            if num_recover == num_relevances:
                R_precision.append(num_recover_relevance/num_relevances)

            if num_recover <= num_relevances:
                precision_mean += (num_recover_relevance/num_recover)/num_relevances

            if num_recover_relevance == 1:
                rr = 1/num_recover

            if int(num_recover) <= 10:
                if int(num_recover) == 1: 
                    DCG[int(num_recover)-1] = (2**num_recover_relevance - 1)/(math.log(1+num_recover))
                    continue
                DCG[int(num_recover-1)] = DCG[int(num_recover-2)] + (2**num_recover_relevance - 1)/(math.log(1+num_recover))
        
        mean_of_mean_precision += precision_mean/100
        media_rr += rr/100
        for i in range(len(DCG)):
            media_dcg[i] += DCG[i]/100
        

        for i in range(len(eleven_recall_total)):
            eleven_recall_total[i] = max(eleven_recall_consulta[i],eleven_recall_total[i])

    maior_ate_p = 0
    lista_x = []
    for i in range(len(eleven_recall_total)):
        eleven_recall_total[i] = int( max(eleven_recall_total[i:]) )
        lista_x.append(10*i)



    tabela_map_mrr = pd.DataFrame(data=[[mean_of_mean_precision,media_rr]], index=["valores"] ,columns=["map","mrr"])

    return lista_x, eleven_recall_total, R_precision, precision_table,f1_scores


if __name__ == "__main__":
    steam='results-stemmer.csv'
    nosteam='results-nostemmer.csv'
    x1,y1,R_precision1 ,precision_table1,f1_scores1= avaliador(steam)
    x2,y2,R_precision2 ,precision_table2,f1_scores2= avaliador(nosteam)


    plt.plot( x1,y1, color='blue', label='Stemmer',linestyle='solid', linewidth = 3, marker='o', markerfacecolor='black', markersize=6)
    plt.plot( x2,y2, color='orange',label='NoStemmer', linestyle='solid', linewidth = 3, marker='o', markerfacecolor='black', markersize=6)
    
    plt.ylim(0,100)
    plt.xlim(0,100)
    plt.xlabel('recall')
    plt.ylabel('precision')  
    plt.title('Grafic 11 points precision recall')
    plt.legend()
    plt.savefig("avalia/11_points.pdf" )




    plt.hist(R_precision1,  alpha=0.5, label='Stemmer')
    plt.hist(R_precision2, alpha=0.5, label='NoStemmer')
    plt.xlabel('Precision')
    plt.ylabel('Frequency')
    plt.title('Histograma Comparativo')
    plt.legend()

    plt.savefig("avalia/histograma.pdf" )


    plt.figure(figsize=(10,5))
    plt.plot(range(1, len(f1_scores1) + 1), f1_scores1, marker='o', linestyle='-',label='Stemmer')
    plt.plot(range(1, len(f1_scores2) + 1), f1_scores2, marker='o', linestyle='-',label='NoStemmer')
    plt.title('F1 Score for each Query')
    plt.xlabel('Query Number')
    plt.ylabel('F1 Score')
    plt.legend()
    plt.savefig("avalia/f1_score.pdf" )