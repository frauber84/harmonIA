# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------- #
# PAINEL DE ESTATÍSTICAS  

import wx
import os
import wx.lib.scrolledpanel
#import wx.lib.agw.hyperlink as hl
import hyperlink_light as hl
import MIDI
import dic_acordes 
import time

def ScaleBitmap(img, width, height):        
    bmp = wx.Bitmap(img, wx.BITMAP_TYPE_ANY)        
    image = wx.Bitmap.ConvertToImage(bmp)
    resized = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
    bmp = wx.Bitmap(resized, wx.BITMAP_TYPE_ANY)        
    return bmp

def arePermutation4(str1, str2):  # somente para 4 acordes,falta generalizar isso
      
    # tamanho diferente = não é permutação
    n1 = len(str1) 
    n2 = len(str2) 
    if (n1 != n2): 
        return False
    
    try:
        s1 = str1.split(" ")
        s2 = str2.split(" ")
        
        # forma burra, depois sistematizar isso em algoritmo  com  mod4 --> %4
        if s1[0] == s2[0] and s1[1] == s2[1] and s1[2] == s2[2] and s1[3] == s2[3]:
            return True  # são idênticas
        elif s1[0] == s2[3] and s1[1] == s2[0] and s1[2] == s2[1] and s1[3] == s2[2]:
            return True  # são idênticas
        elif s1[0] == s2[1] and s1[1] == s2[2] and s1[2] == s2[3] and s1[3] == s2[0]:
            return True  # são idênticas
        elif s1[0] == s2[2] and s1[1] == s2[3] and s1[2] == s2[0] and s1[3] == s2[1]:
            return True  # são idênticas
        else:
            return False  
    except:
        return False 

def arePermutation8(str1, str2):  # somente para 4 acordes,falta generalizar isso
      
    # tamanho diferente = não é permutação
    n1 = len(str1) 
    n2 = len(str2) 
    if (n1 != n2): 
        return False
    
    try:
        s1 = str1.split(" ")
        s2 = str2.split(" ")
        
        for i in range (0,8):          
            if s1[0] == s2[(0+i)%8] and s1[1] == s2[(1+i)%8] and s1[2] == s2[(2+i)%8] and s1[3] == s2[(3+i)%8] and s1[4] == s2[(4+i)%8] and s1[5] == s2[(5+i)%8] and s1[6] == s2[(6+i)%8] and s1[7] == s2[(7+i)%8]:
                return True  # são idênticas
    except:
        pass
    
    return False


def log(log):
    #os.chdir(r"C:\fernando\2018\python\CIFRACLUB")
    if os.path.exists("log_stats.txt") == False:                
        f = open("log_stats.txt", "w", encoding="utf8")
        f.write(log)        
    elif os.path.exists("log_stats.txt") == True :
        f = open("log_stats.txt", "a", encoding="utf8")    
        f.write(log)
    f.close()

class PainelStats(wx.Dialog):
    
    def MostraCloud(self,event):
        dlg = self.PainelCloud(self)
        dlg.ShowModal()
        dlg.Destroy()
        
    class PainelCloud(wx.Dialog):
        def __init__(self, parent):
            title = 'Nuvem de Acordes '        
            wx.Dialog.__init__(self, parent, -1, title,
                               style=wx.DEFAULT_DIALOG_STYLE | wx.CAPTION | wx.RESIZE_BORDER )
            
            # resize da núvem
            self.SetSize ( (924/1.1 + 20,   739/1.1 + 40) )
            self.SetMinSize( (924/1.1 + 20, 739/1.1 + 40) )
            self.Centre()
            
            #png = wx.Image(os.path.join(parent.savedir, 'cloud.png'), wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            
            png= ScaleBitmap(os.path.join(parent.savedir, 'cloud.png'),924/1.1, 739/1.1)
            self.sbm = wx.StaticBitmap(self, bitmap=png, pos=(0,0))
            
            
            

    def TocarAcorde(self, event):        
        try:
            ac = event.GetEventObject()      
            acorde = ac.GetLabel()              
            acMIDI = dic_acordes.Acordes.get(acorde) 
            
            if not acMIDI == None:                
                MIDI.TocarAcorde(dic_acordes.Acordes[ac.GetLabel()], 0.026)
            else:        
                print("acorde não encontrado em dic_acordes.py: " + acorde)
        except:
            print("acorde não encontrado em dic_acordes.py: " + acorde)
        
    def CriaPainel(self, label, nb, ac):  
        # Cria abas do notebook com scroll vertical
        painel = wx.lib.scrolledpanel.ScrolledPanel(nb,-1, size=(645,330), pos=(0,28), style=wx.NO_BORDER)
        painel.SetupScrolling()            
        return painel
    
    def __init__(self, parent, savedir, nome):
        title = 'Informações do modelo "' + str(nome) + '"'        
        wx.Dialog.__init__(self, parent, -1, title,
                           style=wx.DEFAULT_DIALOG_STYLE | wx.CAPTION | wx.RESIZE_BORDER)
        self.SetSize ( (645, 330) )
        self.SetMinSize( (645,330) )
        self.savedir = savedir
        self.Centre()
        self.info = {
                  'nome': '',
                  'descricao': '',
                  'musicas': 0,
                  'rnn-size': 0,
                  'acordes': 0,                                    
                  'layers': 2,
                  'seq_length': 6,
                  'tempo': 0.0,
                  'grad_clip': 0.0,
                  'learning_rate': 0.0,
                  'train_loss': 0.0,
                  'total_acordes':0,
                  'total_musicas':0,
                  'diversidade_harmonica': 0,
                  'tomC': 0,
                  'tomCm': 0,
                  'tomDb': 0,
                  'tomC#m': 0,
                  'tomD': 0,
                  'tomDm': 0,
                  'tomEb': 0,
                  'tomEbm': 0,
                  'tomE': 0,
                  'tomEm': 0,
                  'tomF': 0,
                  'tomFm': 0,
                  'tomF#': 0,
                  'tomF#m': 0,
                  'tomG': 0,
                  'tomGm': 0,
                  'tomAb': 0,
                  'tomG#m': 0,
                  'tomA': 0,
                  'tomAm': 0,
                  'tomBb': 0,
                  'tomBbm': 0,
                  'tomB': 0,
                  'tomBm': 0,
                  }
        
        # listas com frequências de progressões
        self.ac_1, self.ac_4, self.temp_4, self.ac_8, self.temp_8 = ( [] for _ in range(5) ) 
        self.noInfo = False        
        p1_ac, p4_ac, p8_ac = ( '' for _ in range(3) )
        
        # carrega arquivo Info no diretório do modelo        
        
        self.Estatisticas = self.CarregaEstatisticas(savedir)  
        
        # Cria notebook e página inicial
        notebook = wx.Notebook(self, -1, size=(525,300))                
        p0 = wx.Panel(notebook)
        notebook.AddPage(p0, "Informações ")
        
        tom_p = wx.Panel(notebook)
        notebook.AddPage(tom_p, "Tonalidades")
        
        
        if self.noInfo == False:
            #Nuvem de acordes
            #butaoNuvem = wx.(p0, label="Nuvem de Acordes", pos=(200,40) )                        
            
            nuvem = ScaleBitmap(os.path.join(savedir, 'cloud.png'),924/4, 739/4)
            botao= wx.BitmapButton(p0, bitmap=nuvem, pos=(350,40), size=(924/4,739/4) )
            
            botao.Bind(wx.EVT_BUTTON, lambda event: self.MostraCloud(event))

            nuvemtxt = wx.StaticText(p0, label= "Nuvem de acordes (clique para ampliar)", pos=(350,20) )
            
            p0txt = wx.StaticText(p0, label=
                                "Descrição:  " + str(self.info['descricao']) + 
                                "\nMúsicas processadas: " + str(self.info['total_musicas']) + 
                                "\nAcordes processados: " + str(self.info['total_acordes']) + 
                                "\nAcordes distintos: " + str(self.info['acordes']) + 
                                "\nDiversidade harmônica: " + str(self.info['diversidade_harmonica']) + 
                                "\nAcorde mais utilizado: " + str(self.ac_1[0]) +
                                "\n\nClique nas abas para visualizar as progressões mais comuns", pos=(20, 20))
            
            tomMaior = wx.StaticText(tom_p, label=
                                "C Maior:  " + str(self.info['tomC']) + 
                                "\nDb Maior: " + str(self.info['tomDb']) +
                                "\nD Maior: " + str(self.info['tomD']) + 
                                "\nEb Maior: " + str(self.info['tomEb']) + 
                                "\nE Maior: " + str(self.info['tomE']) + 
                                "\nF Maior: " + str(self.info['tomF']) + 
                                "\nF# Maior: " + str(self.info['tomF#']) + 
                                "\nG Maior: " + str(self.info['tomG']) + 
                                "\nAb Maior: " + str(self.info['tomAb']) + 
                                "\nA Maior: " + str(self.info['tomA']) + 
                                "\nBb Maior: " + str(self.info['tomBb']) + 
                                "\nB Maior: " + str(self.info['tomB']), pos=(20, 20))

            tomMenor = wx.StaticText(tom_p, label=
                                "C Menor:  " + str(self.info['tomCm']) + 
                                "\nC# Menor: " + str(self.info['tomC#m']) +
                                "\nD Menor: " + str(self.info['tomDm']) + 
                                "\nEb Menor: " + str(self.info['tomEbm']) + 
                                "\nE Menor: " + str(self.info['tomEm']) + 
                                "\nF Menor: " + str(self.info['tomFm']) + 
                                "\nF# Menor: " + str(self.info['tomF#m']) + 
                                "\nG Menor: " + str(self.info['tomGm']) + 
                                "\nG# Menor: " + str(self.info['tomG#m']) + 
                                "\nA Menor: " + str(self.info['tomAm']) + 
                                "\nBb Menor: " + str(self.info['tomBbm']) + 
                                "\nB Menor: " + str(self.info['tomBm']), pos=(150, 20))            
            
            #  Formata texto  e cria abas do notebook
            def separa(acordes):
                f = str(i+1) + ') ' + acordes
                f2 = '(' + f.split(' (')[1]
                return f2
            
            for i in range(0,len(self.ac_1)-1 ):             
                p1_ac += separa(self.ac_1[i])
            for i in range(0,len(self.ac_4)-1 ):
                p4_ac += separa(self.ac_4[i])
            for i in range(0,len(self.ac_8)-1 ):
                p8_ac += separa(self.ac_8[i])

            self.p1 = self.CriaPainel(p1_ac, notebook, self.ac_1)
            self.p4 = self.CriaPainel(p4_ac, notebook, self.ac_4)  
            self.p8 = self.CriaPainel(p8_ac, notebook, self.ac_8)
            
            #self.pcloud = self.CriaPainel(p8_ac, notebook, self.ac_8)
                            
            neural = wx.Panel(notebook)
            notebook.AddPage(self.p1, "Acordes")
                                        
            def CriaAcordes(painel, acordes, contagem):
                hbox = wx.BoxSizer(wx.HORIZONTAL)
                fgs = wx.FlexGridSizer(500, contagem+2, 8,5) # vertical, horizontal, espaçamento vertical, espaçamento horizontal		
                ac_lista = []

                print(contagem)
                t1 = time.time()
      
                numAcordes = len(acordes)-1            
                if numAcordes > 50 and (contagem==4 or contagem==8):
                    numAcordes = 50
                    
                
                for i in range(0,numAcordes ):
                    indice = wx.StaticText(painel, label=str(i+1) + ') ' )
                    ac_lista.append(indice)                    
                    acorde = (acordes[i])[:-1]                
                    acorde = acorde.split(' (')[0]
                    acordes_separados = acorde.split()
                    
                    if contagem==4:
                        for ac in acordes_separados:
                            acd = hl.HyperLinkCtrl(painel, -1, ac, URL="")
                            acd.AutoBrowse(False)
                            acd.SetColours("BLUE", "BLUE", "BLUE")
                            acd.EnableRollover(True)
                            acd.SetUnderlines(False, False, True)
                            acd.SetBold(False)
                            acd.OpenInSameWindow(True)
                            acd.UpdateLink()
                            acd.SetBackgroundColour( (255,255,255) )
                            acd.Bind(hl.EVT_HYPERLINK_LEFT, lambda event: self.TocarAcorde(event) )
                            ac_lista.append(acd)                        
                    
                    elif contagem ==8:
                        for ac in acordes_separados:
                            acd = hl.HyperLinkCtrl(painel, -1, ac, URL="")
                            acd.AutoBrowse(False)
                            acd.SetColours("BLUE", "BLUE", "BLUE")
                            acd.EnableRollover(True)
                            acd.SetUnderlines(False, False, True)
                            acd.SetBold(False)
                            acd.OpenInSameWindow(True)
                            acd.UpdateLink()
                            acd.SetBackgroundColour( (255,255,255) )
                            acd.Bind(hl.EVT_HYPERLINK_LEFT, lambda event: self.TocarAcorde(event) )
                            ac_lista.append(acd)                        
                    else:                        
                        # outras contagens (temporária)
                        for ac in acordes_separados:
                            acd = hl.HyperLinkCtrl(painel, -1, ac, URL="")
                            acd.AutoBrowse(False)
                            acd.SetColours("BLUE", "BLUE", "BLUE")
                            acd.EnableRollover(True)
                            acd.SetUnderlines(False, False, True)
                            acd.SetBold(False)
                            acd.OpenInSameWindow(True)
                            acd.UpdateLink()
                            acd.SetBackgroundColour( (255,255,255) )
                            acd.Bind(hl.EVT_HYPERLINK_LEFT, lambda event: self.TocarAcorde(event) )
                            ac_lista.append(acd)    
                            
                    frequencia = wx.StaticText(painel, label='(' + (acordes[i].split(' (')[1])[:-1] )
                    ac_lista.append(frequencia)
                t2 = time.time() - t1 
                print("Tempo(segundos): " )
                print(t2)

                
                fgs.AddMany( ac_lista )
                t1 = time.time()                                
                hbox.Add(fgs, proportion = 2, flag = wx.LEFT | wx.TOP, border = 20) 
                painel.SetSizer(hbox) 
                t2 = time.time() - t1 
                print("Tempo(segundos): " )
                print(t2)


            CriaAcordes(self.p1, self.ac_1, 1)
            CriaAcordes(self.p4, self.ac_4, 4)
            CriaAcordes(self.p8, self.ac_8, 8)
            
            notebook.AddPage(self.p4, "4 acordes")
            notebook.AddPage(self.p8, "8 acordes")

            '''
            # antigo, foi substitudo pela novo modal
            
            def CriaCloud(painel):
                #bmp = wx.StaticBitmap(painel, -1, png, (0, 0), (png.GetWidth(), png.GetHeight()))
                painel.img_sizer = wx.BoxSizer(wx.VERTICAL)

                try:
                    png = wx.Image(os.path.join(savedir, 'cloud.png'), wx.BITMAP_TYPE_ANY).ConvertToBitmap()                        
                    painel.sbm = wx.StaticBitmap(painel, bitmap=png)                
                    painel.img_sizer.Add(painel.sbm, 1, wx.EXPAND)
                except:
                    pass                
                painel.SetSizer(painel.img_sizer)
                
            CriaCloud(self.pcloud)
            notebook.AddPage(self.pcloud, "Nuvem de Acordes")                        
            '''
            
            notebook.AddPage(neural, "Rede neural ")
            
            neuraltxt = wx.StaticText(neural, label=
                                "Hiperparâmetros da rede neural:\n  " +                                
                                "\nTamanho da rede: " + str(self.info['rnn_size']) + " células" +
                                "\nLayers: " + str(self.info['layers']) + 
                                "\nMemória LTSM: " + str(self.info['seq_length']) + " acordes" +
                                "\nTempo de treinamento: " + str( int(int(self.info['tempo'])/60) ) + " minutos "
                                "\nÉpocas de treinamento: " + str(self.info['epocas']) +
                                "\nTrain_loss: " + str(self.info['train_loss']) +
                                "\nClipagem de gradientes: " + str(self.info['grad_clip']) + 
                                "\nTaxa de aprendizado: " + str(self.info['learning_rate']), pos=(20, 20))
        else:
            p0txt = wx.StaticText(p0, label="Sem informações do modelo")
        
    def CarregaEstatisticas(self, diretorio):        
        # Lê arquivo Info criado durante treinamento
        ''' to DO: criar MÉDIA GLOBAL de diversidade harmônica '''
        try:
            f = open(os.path.join(diretorio, 'info'), 'r', encoding='utf-8')
            for line in f.readlines():
                if 'rnn-size:' in line:
                    self.info['rnn_size'] = int ( line.split('rnn-size:')[1] )
                elif 'descricao:' in line:
                    self.info['descricao'] = str ( line.split('descricao:')[1] )
                elif 'nome:' in line:
                    self.info['nome'] = str ( line.split('nome:')[1] )
                elif 'total_acordes:' in line:
                    self.info['total_acordes'] = int ( line.split('total_acordes:')[1] )
                elif 'acordes:' in line:
                    self.info['acordes'] = int ( line.split('acordes:')[1] )
                elif 'epocas:' in line:
                    self.info['epocas'] = int ( line.split('epocas:')[1] )
                elif 'learning_rate:' in line:
                    self.info['learning_rate'] = float ( line.split('learning_rate:')[1] )
                elif 'seq_length:' in line:
                    self.info['seq_length'] = int ( line.split('seq_length:')[1] )
                elif 'grad_clip:' in line:
                    self.info['grad_clip'] = float ( line.split('grad_clip:')[1] )
                elif 'tempo:' in line:
                    self.info['tempo'] = float( line.split('tempo:')[1] )
                elif 'train_loss:' in line:
                    self.info['train_loss'] = float( line.split('train_loss:')[1] )
                elif 'total_musicas:' in line:
                    self.info['total_musicas'] = int ( line.split('total_musicas:')[1] )
                elif 'diversidade_harmonica:' in line:
                    self.info['diversidade_harmonica'] = float ( line.split('diversidade_harmonica:')[1] )            
                elif 'tomC:' in line:
                    self.info['tomC'] = int ( line.split('tomC:')[1] )
                elif 'tomCm:' in line:
                    self.info['tomCm'] = int ( line.split('tomCm:')[1] )
                elif 'tomDb:' in line:
                    self.info['tomDb'] = int ( line.split('tomDb:')[1] )
                elif 'tomC#m:' in line:
                    self.info['tomC#m'] = int ( line.split('tomC#m:')[1] )
                elif 'tomD:' in line:
                    self.info['tomD'] = int ( line.split('tomD:')[1] )
                elif 'tomDm:' in line:
                    self.info['tomDm'] = int ( line.split('tomDm:')[1] )
                elif 'tomEb:' in line:
                    self.info['tomEb'] = int ( line.split('tomEb:')[1] )
                elif 'tomEbm:' in line:
                    self.info['tomEbm'] = int ( line.split('tomEbm:')[1] )
                elif 'tomE:' in line:
                    self.info['tomE'] = int ( line.split('tomE:')[1] )
                elif 'tomEm:' in line:
                    self.info['tomEm'] = int ( line.split('tomEm:')[1] )
                elif 'tomF:' in line:
                    self.info['tomF'] = int ( line.split('tomF:')[1] )
                elif 'tomFm:' in line:
                    self.info['tomFm'] = int ( line.split('tomFm:')[1] )
                elif 'tomF#:' in line:
                    self.info['tomF#'] = int ( line.split('tomF#:')[1] )
                elif 'tomF#m:' in line:
                    self.info['tomF#m'] = int ( line.split('tomF#m:')[1] )
                elif 'tomG:' in line:
                    self.info['tomG'] = int ( line.split('tomG:')[1] )
                elif 'tomGm:' in line:
                    self.info['tomGm'] = int ( line.split('tomGm:')[1] )
                elif 'tomAb:' in line:
                    self.info['tomAb'] = int ( line.split('tomAb:')[1] )
                elif 'tomG#m:' in line:
                    self.info['tomG#m'] = int ( line.split('tomG#m:')[1] )
                elif 'tomA:' in line:
                    self.info['tomA'] = int ( line.split('tomA:')[1] )
                elif 'tomAm:' in line:
                    self.info['tomAm'] = int ( line.split('tomAm:')[1] )
                elif 'tomBb:' in line:
                    self.info['tomBb'] = int ( line.split('tomBb:')[1] )
                elif 'tomBbm:' in line:
                    self.info['tomBbm'] = int ( line.split('tomBbm:')[1] )
                elif 'tomB:' in line:
                    self.info['tomB'] = int ( line.split('tomB:')[1] )
                elif 'tomBm:' in line:
                    self.info['tomBm'] = int ( line.split('tomBm:')[1] )
        except:
            self.noInfo = True
            log("noinfo")

        f.close()
        
        # frequências de acordes e progressões
        try:    
            f = open(os.path.join(diretorio, 'info'), 'r', encoding='utf-8')
            for line in f.readlines():                    
                
                def formata(linha,frequencia):
                    acorde = str ( linha.split(frequencia)[1] )
                    acorde = acorde.split(':')[0] + ' ('                        
                    freq = str( line.split(':')[2] )
                    freq = freq.split(':')[0] + ' ocorrências, '
                    perc = str( line.split(':')[3] )
                    perc = (perc.split(':')[0])[:-1] + '%)\n'
                    return str(acorde+freq+perc)
                    
                for i in range(1,50):
                    freq = '1-' + str(i) + ':' 
                    #print(freq)
                    if freq in line:          
                        self.ac_1.append(formata(line,freq) )
                    
                for i in range(1,120):
                    freq = '4-' + str(i) + ':'                    
                    if freq in line:
                        self.temp_4.append(formata(line,freq) )
                    freq = '8-' + str(i) + ':'                    
                    if freq in line:
                        self.temp_8.append(formata(line,freq) )
                f.close()

            # Exclui repetidos (4 acordes)
            repetido4 = []
            for i in range(0,len(self.temp_4)):
                str1 = self.temp_4[i].split('(')  # Separa acordes do texto. Str[0] = acorde
                str1 = str1[0]
                str1 = str1[:-1]
                if i not in repetido4:
                    for z in range(0,len(self.temp_4)):
                        if i != z and z not in repetido4:
                            str2 = self.temp_4[z].split('(')                            
                            str2 = str2[0]
                            str2 = str2[:-1]
                            if arePermutation4(str1, str2)==True:
                                repetido4.append(z)
            #cria lista definitiva
            for i in range(0,len(self.temp_4)):
                if i not in repetido4:
                    self.ac_4.append(self.temp_4[i])
                    
            # Exclui repetidos (4 acordes8
            repetido8 = []
            for i in range(0,len(self.temp_8)):
                str1 = self.temp_8[i].split('(')  # Separa acordes do texto. Str[0] = acorde
                str1 = str1[0]
                str1 = str1[:-1]
                if i not in repetido8:
                    for z in range(0,len(self.temp_8)):
                        if i != z and z not in repetido8:
                            str2 = self.temp_8[z].split('(')                            
                            str2 = str2[0]
                            str2 = str2[:-1]
                            if arePermutation8(str1, str2)==True:
                                repetido8.append(z)
            #cria lista definitiva
            for i in range(0,len(self.temp_8)):
                if i not in repetido8:
                    self.ac_8.append(self.temp_8[i])
                    
            # TODO: corrigir frequencias
            # fazer uma passagem sequencial pela lista e SOMAR frequencias

        except:
            #pass        
            self.noInfo = True   # 16/08: CONFERIR ISSO.. pq RAMONES dá pau?
            log("nofreq")
        
            