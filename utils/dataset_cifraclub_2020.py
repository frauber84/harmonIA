import os
import codecs
from pathlib import Path
from bs4 import BeautifulSoup

#diretório com mirror do CifraClub.com.br
#path = r"D:\Partituras\wget\bin\t"

# HD Externo antigo...  RIP !
path = r"D:\cifraclub-dataset\t\www.cifraclub.com.br"

log = open("log.txt", "w", encoding="utf8")

numf = 0
descartado = 0
descartado_l = []
lmusicas = []
invalido = 0
capo = 0
ciclo_quintas = ['E', 'A',  'D', 'G', 'C',  'F', 'Bb', 'Eb', 'Ab', 'Db', 'F#', ' B'  ]

            
#log                 
def printl(x):
    log.write(str(x))

def RemoveDuplicados(duplicate): 
    final_list = [] 
    for num in duplicate: 
        if num not in final_list: 
            final_list.append(num) 
    return final_list 
    
for file_path in Path(path).glob('**/index.html'): #ignorar os imprimir.html 
    
    f_est = ""
    f_art = ""
    f_tom = ""
    f_mus = ""
    numf += 1
    arquivo = str(file_path)
    printl(arquivo + "\n")
    capotr=False
    extensoes = False
    descartar = False

    musicapobre3 = False  # música com somente 3 acordes (para voculbário rico)
    musicapobre4 = False  # música com somente 4 acordes (para voculbário rico)
    musicapobre5 = False  # música com somente 5 acordes (para voculbário rico)
    musicapobre7 = False  # música com somente 4 acordes (para voculbário rico)
    musicapobre13 = False  # música com somente 5 acordes (para voculbário rico)    
    muitosE = False    
    
    try:
        
        with codecs.open(arquivo, "r", encoding="utf8", errors="ignore") as f:
                    
            filtrado = ""
            inicio=False
            
            #ler arquivo
            for line in f:   
                if '<a class="js-modal-trigger"'in line:
                    inicio=True
                    
                    #tonalidade
                    try:                    
                        string=line
                        token="cifra"
                        
                        if ('canción' in string):
                            token='canción'                    
                        
                        tom=string.split(token)[1]
                        tom=tom.replace('"', "")
                        tom=tom.replace('>', "")    
                        try:
                            tom= tom.split("<")[0]
                            f_tom = tom
                            
                            if "do" in f_tom:
                                f_tom = f_tom.replace("do","")                            
                            
                            if len(f_tom) > 4:
                                f_tom = ""
                        except:
                            dummy = 0
                    except:
                        dummy = 0
                    
                if '</div>' in line:
                    inicio=False
                    
                if inicio==True:
                    filtrado+=line
                if 'Capotraste na' in line:
                    capotr=True
                if 'Capo en ' in line:
                    capotr=True                
                if  'window.__segArgs = {' in line:                            
                    string=line
                    
                    # genero 
                    string.replace(r'"', '')
                    string.replace(r':', '')
                    string2= string.split("}")[0]
                    try:
                        genero=string2.split('genero')[1]
                        genero=genero.replace('"', '')
                        genero=genero.replace(':', '')
                        
                        genero=genero.replace(',idiomaes', '')
                        genero=genero.replace(',idiomapt', '')
                        genero=genero.replace(',idiomaen', '')
                        # lidar com ,idiomaes
                        
                        printl("gênero:" + genero + "\n")                    
                        f_est = genero
                            
                        artista=string2.split('artista')[1]
                        artista=artista.replace('"', '')
                        artista=artista.replace(':', '')
                        artista=artista.split(",")[0]
                        printl("artista: " + artista + "\n")
                        
                        f_art = artista
    #                    if artista != "":
    #                        f_art = artista
    #                    else:
    #                        f_art = ""
                        
                        musica=string2.split('musica')[1]
                        musica=musica.replace('"', '')
                        musica=musica.replace(':', '')
                        musica=musica.split(",")[0]                    
                        musica = musica.replace("-", " ")
                        printl("musica: " + musica + "\n")                    
                        f_mus = musica
                        
                    except:
                        printl("!cifra")
                        invalido += 1;
                        
            #processar arquivo
                    
    #        if not f_mus == "":            
    #            if not f_mus in lmusicas:
    #                lmusicas.append(musica)
    #                os.chdir(r"D:\Partituras\wget\bin\t2")
    #                if os.path.exists("musicas.txt") == False:                
    #                    f3 = open("musicas.txt", "w", encoding="utf8")
    #                elif os.path.exists("musicas.txt") == True :
    #                    f3 = open("musicas.txt", "a", encoding="utf8")                    
                        
    #                f3.write(f_mus + "\n")
    #                f3.close()
            
            try:
                soup = BeautifulSoup(filtrado, 'html.parser')
                acordes = str(soup.find_all('b'))
                acordes_descartados = ''
                
                # limpeza prévia de acordes
                ## agora filtro muitosE vão funcionar
                chaves = {'<b>'   : '' ,              
                  '</b>,' : '' ,
                  '</b>'  : '' ,
                  '[<b "="">'  : '' ,              
                  '*'     : '' ,
                  '['     : '' ,
                  ']'     : '' ,              
                  }     
    
                for key in sorted(chaves, key=len, reverse=True): # Through keys sorted by length
                    acordes = acordes.replace(key, chaves[key])
                
                #enarmonia
                if (capotr):
                    f_tom = "capo"
    
                # OBS: cifras_helper.py corrige enarmonias depois
                if f_tom == "A#":
                    f_tom = "Bb"   
                if f_tom == "D#":
                    f_tom = "Eb"   
                if f_tom == "G#":
                    f_tom = "Ab"     
    
                if f_tom != "":
                    printl("Tonalidade: " + f_tom + "\n")
                                            
                # música com extensões (métodos diferentes para filtrar)
                if ('11' and '13' in acordes):
                    extensoes = True
    
                if ('\n' in acordes): # esse foi o método mais efetivo de descartar problemas
                    printl("newline\n")
                    acordes_descartados = acordes
                    acordes = ""
                    descartado += 1
                    descartado_l.append(str(file_path))                
                    descartar = True                            
                if ('--' in acordes or '<u>' in acordes):  #tablaturas
                    acordes_descartados = acordes
                    acordes = ""
                    descartado += 1
                    descartado_l.append(str(file_path))                
                    descartar = True
                    printl("tablatura <u>\n")
                if ('J' in acordes or 'X' in acordes or 'Q' in acordes or 'v' in acordes or 'ç' in acordes or 'ã' in acordes or 'é' in acordes or 'k' in acordes or 'sou' in acordes):
                    printl("letra J X Q etc\n")
                    acordes_descartados = acordes
                    acordes = ""
                    descartado += 1
                    descartado_l.append(str(file_path))                
                    descartar = True                
                if ('E E E E') in acordes:
                    
                    # problema é o [B]
                    muitosE = True
                    acordes_descartados = acordes
                    acordes = ""
                    descartado += 1
                    descartado_l.append(str(file_path))                
                    printl("\nmuitosE\n")
                if ('E E E E E') in acordes:
                    printl("\nguitarrista unicelular\n")
                    acordes_descartados = acordes
                    acordes = ""
                    descartado += 1
                    descartado_l.append(str(file_path))                
                    descartar = True
                    
                if len(acordes) <= 40:  # threshold para acordes
                    printl("\nthreshold não atingido = \n" + len(acordes))
                    acordes = ""
                    descartar = True
                elif len(acordes) > 40:
                    
                    NumeroAcordes=len ( RemoveDuplicados( acordes.split() ) )
                    
                    if NumeroAcordes > 3:
                        musicapobre3=True
                    if NumeroAcordes > 4:
                        musicapobre4=True
                    if NumeroAcordes > 5:
                        musicapobre5=True
                    if NumeroAcordes > 7:
                        musicapobre7=True
                    if NumeroAcordes > 13:
                        musicapobre13=True
    
                    # _END_ não é mais necessário após reagrupamento de tons, ACREDITO
                    #acordes += ' _END_ '
                    acordes = 'tom=' + f_tom + " " + acordes
    
                    musicaunica = f_mus + f_art  # evita repetições
                    printl("lmusica: " + musicaunica + "\n")
                    if musicaunica in lmusicas:
                        acordes_descartados = acordes
                        acordes = ""
                        descartado += 1
                        descartado_l.append(str(file_path))                
                        descartar = True
                        printl("\nrepetida\n")                 
                    elif (musicaunica not in lmusicas) and (acordes != "") and (descartar==False) :
                        lmusicas.append(musicaunica)
    
                if (acordes==""):
                    numf -= 1
                else:
                    # hack para evitar problemas depois nas correções posteriores com finais de linhas
                    # só roda quando não é um arquivo vazio
                    acordes += " " 
                    
                #muitosE = vai só para artista específico, para pegar punk rock ou metal por exemplo
                #salva arquivo geral  
                if not acordes=="" and not muitosE==True:
                    os.chdir(r"D:\Partituras\wget\bin\t2")
                    if os.path.exists("acordes.txt") == False:                
                        f2 = open("acordes.txt", "w", encoding="utf8")
                    elif os.path.exists("acordes.txt") == True :
                        f2 = open("acordes.txt", "a", encoding="utf8")                
                    f2.write(acordes + "\n")
                    f2.close()
    
                #salva arquivo geral sem músicas "pobres"
                if not acordes=="" and musicapobre3==True and not muitosE==True:
                    os.chdir(r"D:\Partituras\wget\bin\t2")
                    if os.path.exists("acordes_rico3.txt") == False:                
                        f2 = open("acordes_rico3.txt", "w", encoding="utf8")
                    elif os.path.exists("acordes_rico3.txt") == True :
                        f2 = open("acordes_rico3.txt", "a", encoding="utf8")                
                    f2.write(acordes + "\n")
                    f2.close()
    
                #salva arquivo geral sem músicas "pobres"
                if not acordes=="" and musicapobre4==True and not muitosE==True:
                    os.chdir(r"D:\Partituras\wget\bin\t2")
                    if os.path.exists("acordes_rico4.txt") == False:                
                        f2 = open("acordes_rico4.txt", "w", encoding="utf8")
                    elif os.path.exists("acordes_rico4.txt") == True :
                        f2 = open("acordes_rico4.txt", "a", encoding="utf8")                
                    f2.write(acordes + "\n")
                    f2.close()
    
                #salva arquivo geral sem músicas "pobres"
                if not acordes=="" and musicapobre5==True and not muitosE==True:
                    os.chdir(r"D:\Partituras\wget\bin\t2")
                    if os.path.exists("acordes_rico5.txt") == False:                
                        f2 = open("acordes_rico5.txt", "w", encoding="utf8")
                    elif os.path.exists("acordes_rico5.txt") == True :
                        f2 = open("acordes_rico5.txt", "a", encoding="utf8")                
                    f2.write(acordes + "\n")
                    f2.close()
    
                #salva arquivo geral sem músicas "pobres"
                if not acordes=="" and musicapobre7==True and not muitosE==True:
                    os.chdir(r"D:\Partituras\wget\bin\t2")
                    if os.path.exists("acordes_rico7.txt") == False:                
                        f2 = open("acordes_rico7.txt", "w", encoding="utf8")
                    elif os.path.exists("acordes_rico7.txt") == True :
                        f2 = open("acordes_rico7.txt", "a", encoding="utf8")                
                    f2.write(acordes + "\n")
                    f2.close()
    
                #salva arquivo geral sem músicas "pobres"
                if not acordes=="" and musicapobre13==True and not muitosE==True:
                    os.chdir(r"D:\Partituras\wget\bin\t2")
                    if os.path.exists("acordes_rico7.txt") == False:                
                        f2 = open("acordes_rico13.txt", "w", encoding="utf8")
                    elif os.path.exists("acordes_rico7.txt") == True :
                        f2 = open("acordes_rico13.txt", "a", encoding="utf8")                
                    f2.write(acordes + "\n")
                    f2.close()
                
                #salva por artista
                if not f_art == "" and not acordes=="":  # aqui MuitosE == OK
                    os.chdir(r"D:\Partituras\wget\bin\t2\artista")                
                    if os.path.exists(f_art + ".txt") == False:                
                        f2 = open(f_art + ".txt", "w", encoding="utf8")
                    elif os.path.exists(f_art + ".txt") == True :
                        f2 = open(f_art + ".txt", "a", encoding="utf8")                    
                    f2.write(acordes + "\n")
                    f2.close()
                                    
                '''
                # salva artista por tom (não é mais necessario por conta do tom=XX)
                
                if not f_art == "" and not acordes=="" and not f_tom == "":    
                        path2=r'D:\Partituras\wget\bin\t2\artista\\'
                        path2 += f_art + "\dummy.txt"
                        directory = os.path.dirname(path2)
                        try:
                            if not os.path.exists(directory):
                                os.makedirs(directory)
                            else:
                                pass
                        except:
                            pass
                            
                        os.chdir(directory)
                        if os.path.exists(f_art + "_" + f_tom + ".txt") == True:
                            f3 = open(f_art + "_" + f_tom + ".txt", "a", encoding="utf8")    
                        if os.path.exists(f_art + "_" + f_tom + ".txt") == False:
                            f3 = open(f_art + "_" + f_tom + ".txt", "w", encoding="utf8")
                        f3.write(acordes + "\n")
                        f3.close()
                '''
                        
                #salva por estilo
                if not f_est == "" and not acordes=="":
                    os.chdir(r"D:\Partituras\wget\bin\t2\estilo")                
                    if os.path.exists(f_est + ".txt") == False:                
                        f2 = open(f_est + ".txt", "w", encoding="utf8")
                    elif os.path.exists(f_est + ".txt") == True :
                        f2 = open(f_est + ".txt", "a", encoding="utf8")    
                    f2.write(acordes + "\n")
                    f2.close()            
                    
                #salva extensoes
                if extensoes == True and not acordes=="" and not muitosE==True:
                    os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                    if os.path.exists("extensoes.txt") == False:                
                        f2 = open("extensoes.txt", "w", encoding="utf8")
                    elif os.path.exists("extensoes.txt") == True :
                        f2 = open("extensoes.txt", "a", encoding="utf8")    
                    f2.write(acordes + "\n")
                    f2.close()            
                    
                if descartar == True and not acordes_descartados =="":
                    os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                    if os.path.exists("descartados.txt") == False:                
                        f2 = open("descartados.txt", "w", encoding="utf8")
                    elif os.path.exists("descartados.txt") == True :
                        f2 = open("descartados.txt", "a", encoding="utf8")    
                    f2.write(arquivo)
                    f2.write('tom=' + f_tom + " ")
                    f2.write("\n" + acordes_descartados + "\n")
                    f2.close()
                
                #salva extensoes por tom
                if not f_tom == "" and extensoes == True and not acordes=="" and not muitosE==True:
                    os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                    if os.path.exists(f_tom + "_ext.txt") == False:                
                        f2 = open(f_tom + "_ext.txt", "w", encoding="utf8")
                    elif os.path.exists(f_tom + "_ext.txt") == True :
                        f2 = open(f_tom + "_ext.txt", "a", encoding="utf8")    
                    f2.write(acordes + "\n")
                    f2.close()            
    
                #salva por tom                
                
                #filtra arquivos que provavelmente não estão no tom indicado [ENARMONIAS]
                if f_tom == "Bb" and not acordes=="" and not muitosE==True:
                    if ("Bb6(9) " in acordes) or ("Bb6/9 " in acordes) or ("Bb(add9) " in acordes) or ("Bbadd9 " in acordes) or ("Bb9 " in acordes) or ("Bb " in acordes) or ("BbMaj7 " in acordes) or ("Bbmaj7 " in acordes) or ("Bb7+ " in acordes) or ("Bb7M(9) " in acordes) or ("Bb7M " in acordes) or ("Bb5 " in acordes) or ("Bbm " in acordes) or ("A#6(9) " in acordes) or ("A#6/9 " in acordes) or ("A#(add9) " in acordes) or ("A#add9 " in acordes) or ("A#9 " in acordes) or ("A# " in acordes) or ("A#Maj7 " in acordes) or ("A#maj7 " in acordes) or ("A#7+ " in acordes) or ("A#7M(9) " in acordes) or ("A#7M " in acordes) or ("A#5 " in acordes) or ("A#m " in acordes):
                        os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                        if os.path.exists(f_tom + ".txt") == False:                
                            f2 = open(f_tom + ".txt", "w", encoding="utf8")
                        elif os.path.exists(f_tom + ".txt") == True :
                            f2 = open(f_tom + ".txt", "a", encoding="utf8")                        
                        f2.write(acordes + "\n")
                        f2.close()
                        # começa FILTRO para limitar músicas com poucos acordes                    
                        if musicapobre3==True:
                            os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                            f3 = open(f_tom + "_rico3.txt", "a", encoding="utf8")
                            f3.write(acordes + "\n")
                            f3.close()
                        if musicapobre4==True:
                            os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                            f4 = open(f_tom + "_rico4.txt", "a", encoding="utf8")
                            f4.write(acordes + "\n")
                            f4.close()
                        if musicapobre5==True:
                            os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                            f5 = open(f_tom + "_rico5.txt", "a", encoding="utf8")
                            f5.write(acordes + "\n")
                            f5.close()
                        if musicapobre7==True:
                            os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                            f7 = open(f_tom + "_rico7.txt", "a", encoding="utf8")
                            f7.write(acordes + "\n")
                            f7.close()
                        if musicapobre13==True:
                            os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                            f13 = open(f_tom + "_rico13.txt", "a", encoding="utf8")
                            f13.write(acordes + "\n")
                            f13.close()                        
                        #termina filtro
                    else:
                        os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                        if os.path.exists(f_tom + "_errado.txt") == False:                
                            f2 = open(f_tom + "_errado.txt", "w", encoding="utf8")
                        elif os.path.exists(f_tom + "_errado.txt") == True :
                            f2 = open(f_tom + "_errado.txt", "a", encoding="utf8")    
                        f2.write(acordes + "\n")
                        f2.close()
                elif f_tom == "Eb" and not acordes=="" and not muitosE==True:
                    if ("Eb6(9) " in acordes) or ("Eb6/9 " in acordes) or ("Eb(add9) " in acordes) or ("Ebadd9 " in acordes) or ("Eb9 " in acordes) or ("Eb " in acordes) or ("EbMaj7 " in acordes) or ("Ebmaj7 " in acordes)or ("Eb7+ " in acordes) or ("Eb7M(9) " in acordes) or ("Eb7M " in acordes) or ("Eb5 " in acordes) or ("Ebm " in acordes) or ("D#6(9) " in acordes) or ("D#6/9 " in acordes) or ("D#(add9) " in acordes) or ("D#add9 " in acordes) or ("D#9 " in acordes) or ("D# " in acordes) or ("D#Maj7 " in acordes) or ("D#maj7 " in acordes)or ("D#7+ " in acordes) or ("D#7M(9) " in acordes) or ("D#7M " in acordes) or ("D#5 " in acordes) or ("D#m " in acordes):
                        os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                        if os.path.exists(f_tom + ".txt") == False:                
                            f2 = open(f_tom + ".txt", "w", encoding="utf8")
                        elif os.path.exists(f_tom + ".txt") == True :
                            f2 = open(f_tom + ".txt", "a", encoding="utf8")    
                        #termina filtro
                        f2.write(acordes + "\n")
                        f2.close()
                        # começa FILTRO para limitar músicas com poucos acordes
                        if musicapobre3==True:
                            os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                            f3 = open(f_tom + "_rico3.txt", "a", encoding="utf8")
                            f3.write(acordes + "\n")
                            f3.close()
                        if musicapobre4==True:
                            os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                            f4 = open(f_tom + "_rico4.txt", "a", encoding="utf8")
                            f4.write(acordes + "\n")
                            f4.close()
                        if musicapobre5==True:
                            os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                            f5 = open(f_tom + "_rico5.txt", "a", encoding="utf8")
                            f5.write(acordes + "\n")
                            f5.close()
                        if musicapobre7==True:
                            os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                            f7 = open(f_tom + "_rico7.txt", "a", encoding="utf8")
                            f7.write(acordes + "\n")
                            f7.close()
                        if musicapobre13==True:
                            os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                            f13 = open(f_tom + "_rico13.txt", "a", encoding="utf8")
                            f13.write(acordes + "\n")
                            f13.close()                        
                    else:
                        os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                        if os.path.exists(f_tom + "_errado.txt") == False:                
                            f2 = open(f_tom + "_errado.txt", "w", encoding="utf8")
                        elif os.path.exists(f_tom + "_errado.txt") == True :
                            f2 = open(f_tom + "_errado.txt", "a", encoding="utf8")    
                        f2.write(acordes + "\n")
                        f2.close()
                elif f_tom == "Ab" and not acordes=="" and not muitosE==True:
                    if ("Ab6(9) " in acordes) or ("Ab6/9 " in acordes) or ("Ab(add9) " in acordes) or ("Abadd9 " in acordes) or ("Ab9 " in acordes) or ("Ab " in acordes) or ("AbMaj7 " in acordes) or ("Abmaj7 " in acordes)or ("Ab7+ " in acordes) or ("Ab7M(9) " in acordes) or ("Ab7M " in acordes) or ("Ab5 " in acordes) or ("Abm " in acordes) or ("G#6(9) " in acordes) or ("G#6/9 " in acordes) or ("G#(add9) " in acordes) or ("G#add9 " in acordes) or ("G#9 " in acordes) or ("G# " in acordes) or ("G#Maj7 " in acordes) or ("G#maj7 " in acordes)or ("G#7+ " in acordes) or ("G#7M(9) " in acordes) or ("G#7M " in acordes) or ("G#5 " in acordes) or ("G#m " in acordes) :
                        os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                        if os.path.exists(f_tom + ".txt") == False:                
                            f2 = open(f_tom + ".txt", "w", encoding="utf8")
                        elif os.path.exists(f_tom + ".txt") == True :
                            f2 = open(f_tom + ".txt", "a", encoding="utf8")
                        f2.write(acordes + "\n")
                        f2.close()                        
                        # começa FILTRO para limitar músicas com poucos acordes
                        if musicapobre3==True:
                            os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                            f3 = open(f_tom + "_rico3.txt", "a", encoding="utf8")
                            f3.write(acordes + "\n")
                            f3.close()
                        if musicapobre4==True:
                            os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                            f4 = open(f_tom + "_rico4.txt", "a", encoding="utf8")
                            f4.write(acordes + "\n")
                            f4.close()
                        if musicapobre5==True:
                            os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                            f5 = open(f_tom + "_rico5.txt", "a", encoding="utf8")
                            f5.write(acordes + "\n")
                            f5.close()
                        if musicapobre7==True:
                            os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                            f7 = open(f_tom + "_rico7.txt", "a", encoding="utf8")
                            f7.write(acordes + "\n")
                            f7.close()
                        if musicapobre13==True:
                            os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                            f13 = open(f_tom + "_rico13.txt", "a", encoding="utf8")
                            f13.write(acordes + "\n")
                            f13.close()                        
                        #termina filtro                    
                    else:
                        os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                        if os.path.exists(f_tom + "_errado.txt") == False:                
                            f2 = open(f_tom + "_errado.txt", "w", encoding="utf8")
                        elif os.path.exists(f_tom + "_errado.txt") == True :
                            f2 = open(f_tom + "_errado.txt", "a", encoding="utf8")    
                        f2.write(acordes + "\n")
                        f2.close()
                elif not f_tom == "" and not acordes=="" and not muitosE==True:
                    #filtra arquivos que provavelmente não estão no tom indicado [SEM ENARMONIAS]
                    if "m" in f_tom: #tom menor
                        if (f_tom + "6(9) " in acordes) or (f_tom + "6/9 " in acordes) or (f_tom + "(add9) " in acordes) or (f_tom + "add9 " in acordes) or (f_tom + "9 " in acordes) or (f_tom + " " in acordes) or (f_tom + "7 " in acordes) or (f_tom + "7(9) " in acordes) or (f_tom + "m7M " in acordes) or (f_tom + "7(9/11) " in acordes) or (f_tom + "9 " in acordes) or (f_tom + "6 " in acordes):
                            os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                            if os.path.exists(f_tom + ".txt") == False:                
                                f2 = open(f_tom + ".txt", "w", encoding="utf8")
                            elif os.path.exists(f_tom + ".txt") == True :
                                f2 = open(f_tom + ".txt", "a", encoding="utf8")                                                                            
                            f2.write(acordes + "\n")
                            f2.close()
                            # começa FILTRO para limitar músicas com poucos acordes
                            if musicapobre3==True:
                                os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                                f3 = open(f_tom + "_rico3.txt", "a", encoding="utf8")
                                f3.write(acordes + "\n")
                                f3.close()
                            if musicapobre4==True:
                                os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                                f4 = open(f_tom + "_rico4.txt", "a", encoding="utf8")
                                f4.write(acordes + "\n")
                                f4.close()
                            if musicapobre5==True:
                                os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                                f5 = open(f_tom + "_rico5.txt", "a", encoding="utf8")
                                f5.write(acordes + "\n")
                                f5.close()
                            if musicapobre7==True:
                                os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                                f7 = open(f_tom + "_rico7.txt", "a", encoding="utf8")
                                f7.write(acordes + "\n")
                                f7.close()
                            if musicapobre13==True:
                                os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                                f13 = open(f_tom + "_rico13.txt", "a", encoding="utf8")
                                f13.write(acordes + "\n")
                                f13.close()                        
                                #termina filtro
                        else:
                            os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                            if os.path.exists(f_tom + "_errado.txt") == False:                
                                f2 = open(f_tom + "_errado.txt", "w", encoding="utf8")
                            elif os.path.exists(f_tom + "_errado.txt") == True :
                                f2 = open(f_tom + "_errado.txt", "a", encoding="utf8")    
                            f2.write(acordes + "\n")
                            f2.close()                    
                    else:  # tom maior                  
                        if (f_tom + "6(9) " in acordes) or (f_tom + "6/9 " in acordes) or (f_tom + "(add9) " in acordes) or (f_tom + "add9 " in acordes) or (f_tom + "6 " in acordes) or (f_tom + "9 " in acordes) or (f_tom + " " in acordes) or (f_tom + "Maj7 " in acordes) or (f_tom + "maj7 " in acordes) or (f_tom + "7+ " in acordes) or (f_tom + "7M(9) " in acordes) or (f_tom + "7M " in acordes) or (f_tom + "5 " in acordes) or (f_tom + "m " in acordes) or (f_tom + "m7 " in acordes) or (f_tom + "m7(9) " in acordes):
                            os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                            if os.path.exists(f_tom + ".txt") == False:                
                                f2 = open(f_tom + ".txt", "w", encoding="utf8")
                            elif os.path.exists(f_tom + ".txt") == True :
                                f2 = open(f_tom + ".txt", "a", encoding="utf8")    
                            f2.write(acordes + "\n")
                            f2.close()
                            # começa FILTRO para limitar músicas com poucos acordes
                            if musicapobre3==True:
                                os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                                f3 = open(f_tom + "_rico3.txt", "a", encoding="utf8")
                                f3.write(acordes + "\n")
                                f3.close()
                            if musicapobre4==True:
                                os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                                f4 = open(f_tom + "_rico4.txt", "a", encoding="utf8")
                                f4.write(acordes + "\n")
                                f4.close()
                            if musicapobre5==True:
                                os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                                f5 = open(f_tom + "_rico5.txt", "a", encoding="utf8")
                                f5.write(acordes + "\n")
                                f5.close()
                            if musicapobre7==True:
                                os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                                f7 = open(f_tom + "_rico7.txt", "a", encoding="utf8")
                                f7.write(acordes + "\n")
                                f7.close()
                            if musicapobre13==True:
                                os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                                f13 = open(f_tom + "_rico13.txt", "a", encoding="utf8")
                                f13.write(acordes + "\n")
                                f13.close()                        
                            #termina filtro
                        else:
                            os.chdir(r"D:\Partituras\wget\bin\t2\tom")
                            if os.path.exists(f_tom + "_errado.txt") == False:                
                                f2 = open(f_tom + "_errado.txt", "w", encoding="utf8")
                            elif os.path.exists(f_tom + "_errado.txt") == True :
                                f2 = open(f_tom + "_errado.txt", "a", encoding="utf8")    
                            f2.write(acordes + "\n")
                            f2.close()
                    
                    #salva por estilo dentro do tom
                    if not f_est == "" and not acordes=="":    
                        path2=r'D:\Partituras\wget\bin\t2\estilo\\'
                        path2 += f_est + "\dummy.txt"
                        directory = os.path.dirname(path2)
                        try:
                            if not os.path.exists(directory):
                                os.makedirs(directory)
                            else:
                                pass
                        except:
                            pass
                            
                        os.chdir(directory)
                        if os.path.exists(f_est + "_" + f_tom + ".txt") == True:
                            f3 = open(f_est + "_" + f_tom + ".txt", "a", encoding="utf8")    
                        if os.path.exists(f_est + "_" + f_tom + ".txt") == False:
                            f3 = open(f_est + "_" + f_tom + ".txt", "w", encoding="utf8")
                        f3.write(acordes + "\n")
                        f3.close()
    
            except:
                printl("\n Erro lendo cifra --> " + str(file_path) )    # erro genérico
                pass
            
            if numf%200==0:
                print(numf)
                
            f.close()

    except:
        print("Erro lendo arquivo (corrompido): " + arquivo)
        pass

#escreve e corrige cifras

printl ("Arquivos processados: " + str(numf) + "\n")
printl ("Arquivos invalidos (!cifra): " + str(invalido) + "\n")
printl ("Arquivos descartadoss : " + str(descartado) + "\n")
for file in descartado_l:
    printl(file + "\n")
log.close()