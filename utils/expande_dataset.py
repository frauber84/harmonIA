# -*- coding: utf-8 -*-

''' 
Expande o dataset para os 12 tons

transposer.py
Created by David Pärsson on 2011-08-13.  com modificações para enarmonias de tons menores
'''

import sys
import os
import re, getopt

key_list = [('A',), ('A#', 'Bb'), ('B',), ('C',), ('C#', 'Db', 'C#m',), ('D',),
            ('D#', 'Eb'), ('E',), ('F',), ('F#', 'Gb', 'F#m'), ('G',), ('G#', 'Ab', 'G#m')]

sharp_flat = ['#', 'b']
sharp_flat_preferences = {
	'A' : '#',
	'A#': 'b',
	'Bb': 'b',
	'B' : '#',
	'C' : 'b',
	'C#': 'b',
    'C#m': '#',
	'Db': 'b',
	'D' : '#',
	'D#': 'b',
	'Eb': 'b',
	'E' : '#',
	'F' : 'b',
	'F#': '#',
	'F#m': '#',
	'Gb': '#',
	'G' : '#',
	'G#': 'b',
    'G#m': '#',    
	'Ab': 'b',
	}

key_regex = re.compile(r"[ABCDEFG][#b]?")

def get_index_from_key(source_key):
    if source_key == 'Fm':
        source_key = 'F';
    for key_names in key_list:
        if source_key in key_names:
            return key_list.index(key_names)
    raise Exception("Invalid key: %s" % source_key)

def get_key_from_index(index, to_key):
	key_names = key_list[index % len(key_list)]
	if len(key_names) > 1:
		sharp_or_flat = sharp_flat.index(sharp_flat_preferences[to_key])
		return key_names[sharp_or_flat]
	return key_names[0]

def get_transponation_steps(source_key, target_key):
	source_index = get_index_from_key(source_key)
	target_index = get_index_from_key(target_key)
	return target_index - source_index

def transpose_string(string, from_key, to_key):
	direction = get_transponation_steps(from_key, to_key)
	result = ''	    
	for line in string:
		result += transpose_line(line, direction, to_key)
	return result

def transpose_line(source_line, direction, to_key):
	source_chords = key_regex.findall(source_line)
	return recursive_line_transpose(source_line, source_chords, direction, to_key)
	
def recursive_line_transpose(source_line, source_chords, direction, to_key):
	if not source_chords or not source_line:
		return source_line
	source_chord = source_chords.pop(0)
	chord_index = source_line.find(source_chord)
	after_chord_index = chord_index + len(source_chord)
	
	return source_line[:chord_index] + \
		   transpose(source_chord, direction, to_key) + \
		   recursive_line_transpose(source_line[after_chord_index:], source_chords, direction, to_key)

def transpose(source_chord, direction, to_key):
	source_index = get_index_from_key(source_chord)
	return get_key_from_index(source_index + direction, to_key)


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


f=open(sys.argv[1], 'r', encoding='utf-8')
arquivo = sys.argv[1]

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

f2=open("temp", "w", encoding="utf8")

tomMaior = [ 'C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B' ]
tomMenor = [ 'C', 'C#m', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'G#m', 'A', 'Bb', 'B']
excluiTom = [ 'C', 'Cm', 'C#', 'Db', 'C#', 'C#m', 'D', 'Dm', 'Eb', 'Ebm', 'E', 'Em', 'F', 'Fm', 'F#', 'F#m', 'G', 'Gm', 'G#', 'Ab', 'G#m', 'A', 'Am', 'Bb', 'Bbm', 'B', 'Bm', 'capo']        

for tom in TomC:
    musica = tom
    for excluir in excluiTom:
        string = "tom=" + excluir + " "
        musica = musica.replace(string, "")  # apaga tons        
    for tonalidade in tomMaior:      #tarnspõe 
        transposto = transpose_string(musica, 'C', tonalidade)    
        f2.write(transposto)
for tom in TomDb:
    musica = tom
    for excluir in excluiTom:
        string = "tom=" + excluir + " "
        musica = musica.replace(string, "")  # apaga tons        
    for tonalidade in tomMaior:      #tarnspõe 
        transposto = transpose_string(musica, 'Db', tonalidade)    
        f2.write(transposto)
for tom in TomD:
    musica = tom
    for excluir in excluiTom:
        string = "tom=" + excluir + " "
        musica = musica.replace(string, "")  # apaga tons        
    for tonalidade in tomMaior:      #tarnspõe 
        transposto = transpose_string(musica, 'D', tonalidade)    
        f2.write(transposto)
for tom in TomEb:
    musica = tom
    for excluir in excluiTom:
        string = "tom=" + excluir + " "
        musica = musica.replace(string, "")  # apaga tons        
    for tonalidade in tomMaior:      #tarnspõe 
        transposto = transpose_string(musica, 'Eb', tonalidade)    
        f2.write(transposto)
for tom in TomE:
    musica = tom
    for excluir in excluiTom:
        string = "tom=" + excluir + " "
        musica = musica.replace(string, "")  # apaga tons        
    for tonalidade in tomMaior:      #tarnspõe 
        transposto = transpose_string(musica, 'E', tonalidade)    
        f2.write(transposto)
for tom in TomF:
    musica = tom
    for excluir in excluiTom:
        string = "tom=" + excluir + " "
        musica = musica.replace(string, "")  # apaga tons        
    for tonalidade in tomMaior:      #tarnspõe 
        transposto = transpose_string(musica, 'F', tonalidade)    
        f2.write(transposto)
for tom in TomFs:
    musica = tom
    for excluir in excluiTom:
        string = "tom=" + excluir + " "
        musica = musica.replace(string, "")  # apaga tons        
    for tonalidade in tomMaior:      #tarnspõe 
        transposto = transpose_string(musica, 'F#', tonalidade)    
        f2.write(transposto)
for tom in TomG:
    musica = tom
    for excluir in excluiTom:
        string = "tom=" + excluir + " "
        musica = musica.replace(string, "")  # apaga tons        
    for tonalidade in tomMaior:      #tarnspõe 
        transposto = transpose_string(musica, 'G', tonalidade)    
        f2.write(transposto)
for tom in TomAb:
    musica = tom
    for excluir in excluiTom:
        string = "tom=" + excluir + " "
        musica = musica.replace(string, "")  # apaga tons        
    for tonalidade in tomMaior:      #tarnspõe 
        transposto = transpose_string(musica, 'Ab', tonalidade)    
        f2.write(transposto)
for tom in TomA:
    musica = tom
    for excluir in excluiTom:
        string = "tom=" + excluir + " "
        musica = musica.replace(string, "")  # apaga tons        
    for tonalidade in tomMaior:      #tarnspõe 
        transposto = transpose_string(musica, 'A', tonalidade)    
        f2.write(transposto)
for tom in TomBb:
    musica = tom
    for excluir in excluiTom:
        string = "tom=" + excluir + " "
        musica = musica.replace(string, "")  # apaga tons        
    for tonalidade in tomMaior:      #tarnspõe 
        transposto = transpose_string(musica, 'Bb', tonalidade)    
        f2.write(transposto)
for tom in TomB:
    musica = tom
    for excluir in excluiTom:
        string = "tom=" + excluir + " "
        musica = musica.replace(string, "")  # apaga tons        
    for tonalidade in tomMaior:      #tarnspõe 
        transposto = transpose_string(musica, 'B', tonalidade)    
        f2.write(transposto)


for tom in TomCm:
    musica = tom
    for excluir in excluiTom:
        string = "tom=" + excluir + " "
        musica = musica.replace(string, "")  # apaga tons        
    for tonalidade in tomMenor:      #tarnspõe 
        transposto = transpose_string(musica, 'C', tonalidade)    
        f2.write(transposto)
for tom in TomCsm:
    musica = tom
    for excluir in excluiTom:
        string = "tom=" + excluir + " "
        musica = musica.replace(string, "")  # apaga tons        
    for tonalidade in tomMenor:      #tarnspõe 
        transposto = transpose_string(musica, 'C#m', tonalidade)    
        f2.write(transposto)
for tom in TomDm:
    musica = tom
    for excluir in excluiTom:
        string = "tom=" + excluir + " "
        musica = musica.replace(string, "")  # apaga tons        
    for tonalidade in tomMenor:      #tarnspõe 
        transposto = transpose_string(musica, 'D', tonalidade)    
        f2.write(transposto)
for tom in TomEbm:
    musica = tom
    for excluir in excluiTom:
        string = "tom=" + excluir + " "
        musica = musica.replace(string, "")  # apaga tons        
    for tonalidade in tomMenor:      #tarnspõe 
        transposto = transpose_string(musica, 'Eb', tonalidade)    
        f2.write(transposto)
for tom in TomEm:
    musica = tom
    for excluir in excluiTom:
        string = "tom=" + excluir + " "
        musica = musica.replace(string, "")  # apaga tons        
    for tonalidade in tomMenor:      #tarnspõe 
        transposto = transpose_string(musica, 'E', tonalidade)    
        f2.write(transposto)
for tom in TomFm:
    musica = tom
    for excluir in excluiTom:
        string = "tom=" + excluir + " "
        musica = musica.replace(string, "")  # apaga tons        
    for tonalidade in tomMenor:      #tarnspõe 
        transposto = transpose_string(musica, 'Fm', tonalidade)    
        f2.write(transposto)
for tom in TomFsm:
    musica = tom
    for excluir in excluiTom:
        string = "tom=" + excluir + " "
        musica = musica.replace(string, "")  # apaga tons        
    for tonalidade in tomMenor:      #tarnspõe 
        transposto = transpose_string(musica, 'F#m', tonalidade)    
        f2.write(transposto)
for tom in TomGm:
    musica = tom
    for excluir in excluiTom:
        string = "tom=" + excluir + " "
        musica = musica.replace(string, "")  # apaga tons        
    for tonalidade in tomMenor:      #tarnspõe 
        transposto = transpose_string(musica, 'G', tonalidade)    
        f2.write(transposto)
for tom in TomGsm:
    musica = tom
    for excluir in excluiTom:
        string = "tom=" + excluir + " "
        musica = musica.replace(string, "")  # apaga tons        
    for tonalidade in tomMenor:      #tarnspõe 
        transposto = transpose_string(musica, 'G#m', tonalidade)    
        f2.write(transposto)
for tom in TomAm:
    musica = tom
    for excluir in excluiTom:
        string = "tom=" + excluir + " "
        musica = musica.replace(string, "")  # apaga tons        
    for tonalidade in tomMenor:      #tarnspõe 
        transposto = transpose_string(musica, 'A', tonalidade)    
        f2.write(transposto)
for tom in TomBbm:
    musica = tom
    for excluir in excluiTom:
        string = "tom=" + excluir + " "
        musica = musica.replace(string, "")  # apaga tons        
    for tonalidade in tomMenor:      #tarnspõe 
        transposto = transpose_string(musica, 'Bb', tonalidade)    
        f2.write(transposto)
for tom in TomBm:
    musica = tom
    for excluir in excluiTom:
        string = "tom=" + excluir + " "
        musica = musica.replace(string, "")  # apaga tons        
    for tonalidade in tomMenor:      #tarnspõe 
        transposto = transpose_string(musica, 'B', tonalidade)    
        f2.write(transposto)
    
f.close
f2.close()

def CorrigeEnarmonias(x):

    '''
    # aqui tem problemas com Db#11 por exemplo...
    chaves = {'Cb#'     : 'C' ,              
              'Db#,'    : 'D' ,
              'Eb#'     : 'E' ,
              'Fb#'     : 'F' ,
              'Gb#'     : 'G' ,
              'Ab#'     : 'A' ,
              'Bb#'     : 'B' ,
              'C#b,'    : 'C' ,
              'D#b,'    : 'D' ,
              'E#b'     : 'E' ,
              'F#b'     : 'F' ,
              'G#b'     : 'G' ,
              'A#b'     : 'A' ,
              'B#b'     : 'B' ,
              }     
    '''
    
    chaves = {'C##'     : 'D' ,              
              'D##'     : 'E' ,
              'E##'     : 'F' ,
              'F##'     : 'G' ,
              'G##'     : 'A' ,
              'A##'     : 'B' ,
              'Bbb'     : 'A' ,
              }     
    

    for key in sorted(chaves, key=len, reverse=True):
        x = x.replace(key, chaves[key])
    return x

# escreve arquivo final com enarmonias corrigidas
temp=open("temp", "r", encoding="utf8")

cifra = temp.read() 
temp.close()
cifra = CorrigeEnarmonias(cifra)
out = open(arquivo + "_expandido12tons", "w", encoding="utf8")
out.write(cifra)
out.close()