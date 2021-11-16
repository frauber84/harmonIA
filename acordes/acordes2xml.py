# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 16:26:34 2020

@author: Fernando
"""



# ACERTAR:
# HORIZONTAL
# Clave inicial

# com clave e sem clave?


import dic_acordes

inicio = """<?xml version="1.0" encoding="UTF-8"?>
<museScore version="3.01">
  <Score>
    <LayerTag id="0" tag="default"></LayerTag>
    <currentLayer>0</currentLayer>
    <Division>480</Division>
    <Style>
      <Spatium>1.76389</Spatium>
      </Style>
    <showInvisible>1</showInvisible>
    <showUnprintable>1</showUnprintable>
    <showFrames>1</showFrames>
    <showMargins>0</showMargins>
    <Part>
      <Staff id="1">
        <StaffType group="pitched">
          <name>stdNormal</name>
          </StaffType>
        </Staff>
      <trackName>Guitar</trackName>
      <Instrument>
        <longName>Guitar</longName>
        <trackName></trackName>
        <Channel>
          <program value="0"/>
          <controller ctrl="10" value="63"/>
          <synti>Fluid</synti>
          </Channel>
        </Instrument>
      </Part>
    <Staff id="1">
      <Measure>
        <voice>
          <Clef>
            <concertClefType>G8vb</concertClefType>
            <transposingClefType>G8vb</transposingClefType>
            <visible>0</visible>
            </Clef>
          <Chord>
            <durationType>whole</durationType>"""
            
fim = """\n            </Chord>
          <BarLine>
            <visible>0</visible>
            </BarLine>            
          </voice>
        </Measure>
      <HBox>
        <width>94.0</width>
        </HBox>
      </Staff>
    </Score>
  </museScore>
"""

def Note(nota, acorde):
    tpc = [ "Cbb", "Gbb", "Dbb", "Abb", "Ebb", "Bbb", "Fb", "Cb", "Gb", "Db", "Ab", "Eb", "Bb", "F", "C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#", "E#", "B#", "F##", "C##", "G##", "D##", "A##", "E##", "B##" ] 
        
    #acorde = acorde[:3]
    #if "Cm7" in acorde:
        #print(acorde)
    
    
    if "/" in acorde:
        if acorde[1] == "/":   # C/B, etc
            acorde = acorde[:1]            
        elif acorde[2] == "/":   # C5/B, F#/C#
            acorde = acorde[:2]              

    NomeNotas = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
    
    #acordes para Testar:
    # Cm7 (porque faz com Ré#?)
    
    if "C#m" in acorde:
        NomeNotas = ['B#', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']    
    elif "F#m" in acorde:
        NomeNotas = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    elif "G#m" in acorde:
        NomeNotas = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    elif "Bbm" in acorde:
        NomeNotas = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
    elif "Abm" in acorde:
        NomeNotas = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'Cb']
    elif "Ebm" in acorde:
        NomeNotas = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
    elif "Cm" in acorde:
        NomeNotas = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']                     
    elif "Gm" in acorde:
        NomeNotas = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
    elif "Dm" in acorde:
        NomeNotas = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B']                     
    elif "Am" in acorde:
        NomeNotas = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B']                     
    elif "Em" in acorde:
        NomeNotas = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']                     
    elif "Bm" in acorde:
        NomeNotas = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']                     
    elif "Fm" in acorde:
        NomeNotas = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'Cb']                     
    elif "C#" in acorde:
        NomeNotas = ['B#', 'C#', 'D', 'D#', 'E', 'E#', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    elif "Ab" in acorde:
        NomeNotas = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
    elif "Db" in acorde:
        NomeNotas = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
    elif "Eb" in acorde:
        NomeNotas = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
    elif "Bb" in acorde:
        NomeNotas = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
    elif "F#" in acorde:
        NomeNotas = ['C', 'C#', 'D', 'D#', 'E', 'E#', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    elif "Gb" in acorde:
        NomeNotas = ['C', 'Db', 'D', 'Eb', 'Fb', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
    elif "C" in acorde:
        NomeNotas = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B']                     
    elif "G" in acorde:
        NomeNotas = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']                     
    elif "D" in acorde:
        NomeNotas = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']                     
    elif "A" in acorde:
        NomeNotas = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']                     
    elif "E" in acorde:
        NomeNotas = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']                     
    elif "B" in acorde:
        NomeNotas = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']                     
    elif "F" in acorde:
        NomeNotas = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']                     
    else:
        print("Acorde fora das regras de enarmonia :" + acorde)
        NomeNotas = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B']                 
        
    nome = NomeNotas[nota%12]    
    
    #if acorde=="Cm7":
        #print(nome)

    tpc = tpc.index(nome) # acha tpc das enarmonias        
    string= "\n            <Note>\n              <pitch>" + str(nota) + "</pitch>\n              <tpc>" + str(tpc) + "</tpc>\n              </Note>"    
    
    return string

# Listas de acordes por qtde. de notas
Ac3, Ac4, Ac5, Ac6 = ([] for _ in range(4))
NomeAc3, NomeAc4, NomeAc5, NomeAc6 = ([] for _ in range(4))

#Popula listas de acordes
for acorde in dic_acordes.Acordes:
    if len(dic_acordes.Acordes[acorde]) == 3:
        Ac3.append(dic_acordes.Acordes[acorde])
        NomeAc3.append(acorde)
    elif len(dic_acordes.Acordes[acorde]) == 4:
        Ac4.append(dic_acordes.Acordes[acorde])
        NomeAc4.append(acorde)
    elif len(dic_acordes.Acordes[acorde]) == 5:
        Ac5.append(dic_acordes.Acordes[acorde])
        NomeAc5.append(acorde)
    elif len(dic_acordes.Acordes[acorde]) == 6:
        Ac6.append(dic_acordes.Acordes[acorde])
        NomeAc6.append(acorde)

# acordes de 3 notas
for i in range(len(Ac3)):
    ac = NomeAc3[i] # nome do acorde e arquivo
    #print("Acorde: " + ac)
    mscx = inicio + Note(Ac3[i][0],ac) + Note(Ac3[i][1],ac) + Note(Ac3[i][2],ac) + fim
    ac = ac.replace("/", "_")            
    f = open(ac + ".mscx", "w", encoding="utf8")
    f.write(mscx)
    f.close

# acordes de 4 notas
for i in range(len(Ac4)):
    ac = NomeAc4[i] # nome do acorde e arquivo
    #print("Acorde: " + ac)
    mscx = inicio + Note(Ac4[i][0],ac) + Note(Ac4[i][1],ac) + Note(Ac4[i][2],ac) + Note(Ac4[i][3],ac) + fim
    ac = ac.replace("/", "_")
    f = open(ac + ".mscx", "w", encoding="utf8")
    f.write(mscx)
    f.close
    
# acordes de 5 notas
for i in range(len(Ac5)):
    ac = NomeAc5[i] # nome do acorde e arquivo
    #print("Acorde: " + ac)
    mscx = inicio + Note(Ac5[i][0],ac) + Note(Ac5[i][1],ac) + Note(Ac5[i][2],ac) + Note(Ac5[i][3],ac) + Note(Ac5[i][4],ac) + fim
    ac = ac.replace("/", "_")
    f = open(ac + ".mscx", "w", encoding="utf8")
    f.write(mscx)
    f.close

# acordes de 6 notas
for i in range(len(Ac6)):
    ac = NomeAc6[i] # nome do acorde e arquivo
    #print("Acorde: " + ac)
    mscx = inicio + Note(Ac6[i][0],ac) + Note(Ac6[i][1],ac) + Note(Ac6[i][2],ac) + Note(Ac6[i][3],ac) + Note(Ac6[i][4],ac) + Note(Ac6[i][5],ac) + fim
    ac = ac.replace("/", "_")
    f = open(ac + ".mscx", "w", encoding="utf8")
    f.write(mscx)
    f.close