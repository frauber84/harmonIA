'''
Compila dicionário de acordes

TODO 2020: pegar posições alternativas

guitar e keyboard...
cavaco ignorar
'''
 
import os
import json
import codecs
from pathlib import Path

def strs_between(s, before, after):
    return (i.split(after)[0] for i in s.split(before)[1:] if after in i)


def RemoveDuplicados(duplicate): 
    final_list = [] 
    for num in duplicate: 
        if num not in final_list: 
            final_list.append(num) 
    return final_list 

# pasta com mirror do cifraclub
path = r"C:\Partituras\wget\bin\t"
os.chdir(path)
dic_acordes = open("dic_acordes.py", "w", encoding="utf8")
dic_acordes.write("# -*- coding: utf-8 -*- \n")
dic_acordes.write("Acordes = { ")
numfiles = 0
ListaAcordes= []

for file_path in Path(path).glob('**/*.html'):        
            
    Ignorar = True
    Capo = True
    with codecs.open(str(file_path), "r", encoding="utf8", errors="ignore") as f:
        #print(file_path) 
        Acordes = []
               
        for line in f:   
            
            if 'Capotraste na' in line:
                Capo = True
            if 'Capo en ' in line:
                Capo = True
            if "tuning: 'E A D G B E'" in line: # IMPORTANTE: afinação correta, ignorar outras alternativas
                Ignorar = False
            if 'capo: 0,' in line:
                Capo = False
            if 'chords: [{"chord' in line:
                #print(line)
            
                if not Ignorar and not Capo:  # sem transposições e capotraste                        
                    Chords = strs_between(line, 'chord":"', '],')    
                    for chord in Chords:
                        acorde = '{"chord":"' + chord + '] }'
                        #print(acorde)    
                        data = json.loads(acorde)    
                        nome_acorde = acorde.split('"')
                    
                        Posicoes = []    
                        for p in data['guitar']:
                            fretes = p.split()
                            ListaFretes = []
                            ListaMIDI = []
                            ListaFretes.append(fretes)
                            CordasSoltas = [ 40, 45, 50, 55, 59, 64 ] # E, A, D, G, B, E
                            #print(fretes)
                            notas = []
                            try:                
                                idx = 0  # coda Mi
                                for fret in fretes:
                                    if fret != 'X':                
                                        nota = int(CordasSoltas[idx]) + int(fret)
                                        notas.append(nota)            
                                    idx += 1                            
                            except:
                                pass
                                #print("erro")
                    
                            notas = RemoveDuplicados(notas) # limpa duplicados
                            
                            if notas not in Posicoes and notas != []:
                                Posicoes.append(notas)
                                #print(nome_acorde[3] + '=' + str(notas) )          
                            #print(nome_acorde[3] + '=' + str(p.split()) )
                                    
                        if not nome_acorde[3] in ListaAcordes: # evita duplicados
                            ListaAcordes.append(nome_acorde[3])  
                            descarte = 0                              
                            for _ in range(len(Posicoes)):                            
                                if _ == 0:
                                    acordestr = "'" + nome_acorde[3] +"' : " + str(Posicoes[_]) + ','
                                    if acordestr not in Acordes:
                                        Acordes.append(acordestr)
                                        dic_acordes.write(acordestr + '\n')
    
                                elif _ > 0 and _ < 5:   # não pegar TODAS alternativas
                                    if Posicoes[0][0]%12 != Posicoes[_][0]%12:
                                        descarte +=1                                        
                                    else:
                                        acordestr = "'" + nome_acorde[3] + "alt" + str(_ - descarte) + "' : " + str(Posicoes[_]) + ','
                                        if acordestr not in Acordes:
                                            Acordes.append(acordestr)
                                            dic_acordes.write(acordestr + '\n')
                                                    
    if not Ignorar and not Capo:
        numfiles = numfiles + 1
        if numfiles%100==0: # a cada 100 arquivos
            print(numfiles)
#finaliza arquivo                
dic_acordes.write("}")
dic_acordes.write("\n# Arquivos processados = " + str(numfiles))
dic_acordes.close()