import os
from pathlib import Path
import subprocess
import time

path = r'C:\fernando\2018\python\CIFRACLUB\utils'
os.chdir(path)

# agrupa_tons por agora está desabilitado

# expansão e normalização: passou para expande_normaliza_batch.py
'''
for file_path in Path(path).glob('**/*.txt2'):
    arquivo = str(file_path)
    # normaliza e expande
    #p = subprocess.Popen(r'python expande_dataset.py ' + arquivo)
#    p.wait()

    # normliza para Dó Maior
    p = subprocess.Popen(r'python normaliza_dataset.py ' + arquivo)
    p.wait()
'''

for file_path in Path(path).glob('**/*.txt2'):
    arquivo = str(file_path)
    path2 = arquivo + '\dummy.txt'
    directory = os.path.dirname(path2)[:-5]    
    save_dir = directory.split('utils\\')[1]
    
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    #tira os toms do arquivo
    arquivo2 = arquivo + "p" # processado
    f=open(arquivo, "r", encoding='utf-8')
    f2=open(arquivo2, 'w', encoding='utf-8')
    com_metadados = f.read()    #process arquivo para tirar meta-informação do tom
    toms = [ 'C', 'Cm', 'C#', 'Db', 'C#', 'C#m', 'D', 'Dm', 'Eb', 'Ebm', 'E', 'Em', 'F', 'Fm', 'F#', 'F#m', 'G', 'Gm', 'G#', 'Ab', 'G#m', 'A', 'Am', 'Bb', 'Bbm', 'B', 'Bm', 'capo']    
    
    for tom in toms:
        string = "tom=" + tom + " "
        com_metadados = com_metadados.replace(string, "")  # apaga tons    

    f2.write(com_metadados)
    
    f.close()    
    f2.close    

    #treina modelo
    print("Treinando modelo " + save_dir)
    p = subprocess.Popen(r'python train.py --data_dir ' + directory + " --save_dir " + save_dir + " --seq_length 8 --input_file " + arquivo2)
    p.wait()
        
    #processa mais estatísticas para arquivo 'info'
    os.chdir(directory)
    p = subprocess.Popen(r'python ..\wordsworth.py --filename ' + arquivo2)
    p.wait()

    #cria WordCloud
    os.chdir(directory)
    p = subprocess.Popen(r'python ..\wcloud.py ' + arquivo2)
    p.wait()

    # faz trim do arquivo com image magick
    p = subprocess.Popen(r'magick convert cloud.png -trim cloud.png')
    p.wait()
    
    # contar tonalidades
    p = subprocess.Popen(r'python ..\conta_tons.py ' + arquivo)
    p.wait()
    
    
    #limpa arquivos não essenciais
    try:
        os.remove('data.npy')
        os.remove('vocab.pkl')        
        #os.remove('metadata.tsv')   # vocabulário e índices
    except:
        pass
    
    #deleta checkpoints parciais exceto o último
    try:
        checkpoints = []    
        f = open ('checkpoint', 'r')
        for line in f.readlines():
            if 'all_model_checkpoint_paths:' in line:            
                checkpoints.append(line.split('all_model_checkpoint_paths: ')[1] )
        
        for i in range(len(checkpoints)-1 ):
            chk = checkpoints[i].replace('"', '')
            chk = chk.replace('\n', '')
            try:
                os.remove(chk + '.index')
                os.remove(chk + '.meta')
                os.remove(chk + '.data-00000-of-00001')
            except:
                pass
    except:
        print("sem checkpoints para deletar?")
 
    f.close()    
    os.chdir(path)    
    try:
        os.remove(arquivo2)
    except:
        try:    
            time.sleep(2)
            os.remove(arquivo2)
        except:
            pass
    