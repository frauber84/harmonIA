# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------- #
# harmonIA - por Fernando Rauber  [ fernandorauber.com.br ]
# Funções MIDI


import rtmidi
import time

# inicializa MIDI
midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()
if available_ports:
    midiout.open_port(0)
else:
    midiout.open_virtual_port("My virtual output")

def TocarAcorde(notas=[],vel_strum = 0.026, transp=0, strum=True, instrumento=25):
    
    # muda instrumento (violao por default)
    # lista: https://en.wikipedia.org/wiki/General_MIDI
    program_change = [192, instrumento]
    midiout.send_message(program_change)
    strum_t=0.075     
    for nota in notas:
        midiout.send_message([0x90, nota+transp, 95])
        if strum:
            time.sleep(strum_t+vel_strum)
        vel_strum -= 0.009
                
def PararAcorde():
    for i in range(127):
        midiout.send_message([0x80, i, 0])    

def NotasDoAcorde(acorde):  # recebe lista de notas MIDI e transforma em alturas
    alturas = [ 'C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B' ]
    notas = []    
    for nota in acorde:
        altura = alturas[nota%12] 
        oitava = nota/12
        altura += str( int(oitava) )
        notas.append( altura )
    return notas