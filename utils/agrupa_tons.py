# -*- coding: utf-8 -*-

''' 
hipótese: agrupar cifras por proximidade de tom para melhorar contextualização harmônica 
 '''
import os
from pathlib import Path
 
#diretório com mirror do CifraClub.com.br
path = r"C:\Partituras\wget\bin\t2"
os.chdir(path)

for file_path in Path(path).glob('**/*.txt2'):
    
    # ciclo de quintas com acordes maiores
    TomEb = []
    TomBb = []
    TomF = []    
    TomC = []
    TomG = []
    TomD = []
    TomA = []
    TomE = []
    TomB = []
    TomFs = []
    TomDb = []
    TomAb = []

    # ciclo de quintas com acordes menores
    TomEbm = []
    TomBbm = []
    TomFm = []    
    TomCm = []
    TomGm = []
    TomDm = []
    TomAm = []
    TomEm = []
    TomBm = []
    TomFsm = []
    TomCsm = []
    TomGsm = []
    
    TomCapo = []    # último
    
    arquivo = str(file_path)
    f=open(arquivo, "r", encoding="utf8")
    linhas=f.readlines()

    for linha in linhas:
        if 'tom=Cm' in linha:
            TomCm.append(linha)
        elif 'tom=C ' in linha:
            TomC.append(linha)            
        elif 'tom=Db' in linha:
            TomDb.append(linha)
        elif 'tom=C#m' in linha:
            TomCsm.append(linha)
        elif 'tom=D ' in linha:
            TomD.append(linha)
        elif 'tom=Dm' in linha:
            TomDm.append(linha)
        elif 'tom=Eb ' in linha:
            TomEb.append(linha)
        elif 'tom=Ebm' in linha:
            TomEbm.append(linha)
        elif 'tom=E ' in linha:
            TomE.append(linha)
        elif 'tom=Em' in linha:
            TomEm.append(linha)
        elif 'tom=F ' in linha:
            TomF.append(linha)
        elif 'tom=Fm' in linha:
            TomFm.append(linha)
        elif 'tom=F# ' in linha:
            TomFs.append(linha)
        elif 'tom=F#m' in linha:
            TomFsm.append(linha)
        elif 'tom=G ' in linha:
            TomG.append(linha)
        elif 'tom=Gm' in linha:
            TomGm.append(linha)
        elif 'tom=Ab ' in linha:
            TomAb.append(linha)
        elif 'tom=G#m' in linha:
            TomGsm.append(linha)
        elif 'tom=A ' in linha:
            TomA.append(linha)
        elif 'tom=Am' in linha:
            TomAm.append(linha)
        elif 'tom=Bb ' in linha:
            TomBb.append(linha)
        elif 'tom=Bbm' in linha:
            TomBbm.append(linha)
        elif 'tom=B ' in linha:
            TomB.append(linha)
        elif 'tom=Bm' in linha:
            TomBm.append(linha)            
        elif 'tom=capo' in linha:
            TomCapo.append(linha)            
                
    f2 = open(arquivo[:-1]+"3", "w", encoding="utf8")
        
    # ciclo de quintas com acordes maiores
    for tom in TomEb:
        f2.write(str(tom))
    for tom in TomBb:
        f2.write(str(tom))
    for tom in TomF:
        f2.write(str(tom))
    for tom in TomC:
        f2.write(str(tom))
    for tom in TomG:
        f2.write(str(tom))
    for tom in TomD:
        f2.write(str(tom))
    for tom in TomA:
        f2.write(str(tom))
    for tom in TomE:
        f2.write(str(tom))
    for tom in TomB:
        f2.write(str(tom))
    for tom in TomFs:
        f2.write(str(tom))
    for tom in TomDb:
        f2.write(str(tom))
    for tom in TomAb:
        f2.write(str(tom))

    # ciclo de quintas com acordes menores
    for tom in TomEbm:
        f2.write(str(tom))
    for tom in TomBbm:
        f2.write(str(tom))
    for tom in TomFm:
        f2.write(str(tom))
    for tom in TomCm:
        f2.write(str(tom))
    for tom in TomGm:
        f2.write(str(tom))
    for tom in TomDm:
        f2.write(str(tom))
    for tom in TomAm:
        f2.write(str(tom))
    for tom in TomEm:
        f2.write(str(tom))
    for tom in TomBm:
        f2.write(str(tom))
    for tom in TomFsm:
        f2.write(str(tom))
    for tom in TomCsm:
        f2.write(str(tom))
    for tom in TomGsm:
        f2.write(str(tom))

    for tom in TomCapo:
        f2.write(str(tom))    

    f2.close()
    
    
    # organizaçao alternativa:
    
    f2 = open(arquivo[:-1]+"4", "w", encoding="utf8")
        
    # agrupa maiores e menores
    for tom in TomEb:
        f2.write(str(tom))
    for tom in TomEbm:
        f2.write(str(tom))
    for tom in TomBb:
        f2.write(str(tom))
    for tom in TomBbm:
        f2.write(str(tom))
    for tom in TomF:
        f2.write(str(tom))
    for tom in TomFm:
        f2.write(str(tom))
    for tom in TomC:
        f2.write(str(tom))
    for tom in TomCm:
        f2.write(str(tom))
    for tom in TomG:
        f2.write(str(tom))
    for tom in TomGm:
        f2.write(str(tom))
    for tom in TomD:
        f2.write(str(tom))
    for tom in TomDm:
        f2.write(str(tom))
    for tom in TomA:
        f2.write(str(tom))
    for tom in TomAm:
        f2.write(str(tom))
    for tom in TomE:
        f2.write(str(tom))
    for tom in TomEm:
        f2.write(str(tom))
    for tom in TomB:
        f2.write(str(tom))
    for tom in TomBm:
        f2.write(str(tom))
    for tom in TomFs:
        f2.write(str(tom))
    for tom in TomFsm:
        f2.write(str(tom))
    for tom in TomDb:
        f2.write(str(tom))
    for tom in TomCsm:
        f2.write(str(tom))
    for tom in TomAb:
        f2.write(str(tom))
    for tom in TomGsm:
        f2.write(str(tom))

    for tom in TomCapo:
        f2.write(str(tom))    

    f2.close()
    
# experimentar aqui com normalização e expansão do dataset