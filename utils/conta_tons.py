# -*- coding: utf-8 -*-

''' 
agrupa arquivos totais por proximidade de tom para melhorar contextualização harmônica 
 '''
import sys

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

print(sys.argv[1])
f=open(sys.argv[1], 'r', encoding='utf-8')

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
            
# abre arquivo INFO escreve numero de tons:

info = "\ntomC:" + str(len(TomC)) + "\n"
info += "tomCm:" + str(len(TomCm)) + "\n"
info += "tomDb:" + str(len(TomDb)) + "\n"
info += "tomC#m:" + str(len(TomCsm)) + "\n"
info += "tomD:" + str(len(TomD)) + "\n"
info += "tomDm:" + str(len(TomDm)) + "\n"
info += "tomEb:" + str(len(TomEb)) + "\n"
info += "tomEbm:" + str(len(TomEbm)) + "\n"
info += "tomE:" + str(len(TomE)) + "\n"
info += "tomEm:" + str(len(TomEm)) + "\n"
info += "tomF:" + str(len(TomF)) + "\n"
info += "tomFm:" + str(len(TomFm)) + "\n"
info += "tomF#:" + str(len(TomFs)) + "\n"
info += "tomF#m:" + str(len(TomFsm)) + "\n"
info += "tomG:" + str(len(TomG)) + "\n"
info += "tomGm:" + str(len(TomGm)) + "\n"
info += "tomAb:" + str(len(TomAb)) + "\n"
info += "tomG#m:" + str(len(TomGsm)) + "\n"
info += "tomA:" + str(len(TomA)) + "\n"
info += "tomAm:" + str(len(TomAm)) + "\n"
info += "tomBb:" + str(len(TomBb)) + "\n"
info += "tomBbm:" + str(len(TomBbm)) + "\n"
info += "tomB:" + str(len(TomB)) + "\n"
info += "tomBm:" + str(len(TomBm))

f=open("info", "a", encoding="utf8")
f.write(info)
f.close()