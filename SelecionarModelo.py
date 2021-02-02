# -*- coding: utf-8 -*-
"""
Created on Sat Apr  7 13:20:34 2018
@author: frauber

MENU DE SELEÇÃO MULTI-MODELO

"""
import wx
import os
import sys


def log(log):
    os.chdir(r"C:\fernando\2018\python\CIFRACLUB")
    if os.path.exists("log_smodelo.txt") == False:                
        f = open("log_smodelo.txt", "w", encoding="utf8")
        f.write(log + '\n')    
    elif os.path.exists("log_smodelo.txt") == True :
        f = open("log_smodelo.txt", "a", encoding="utf8")    
        f.write(log + '\n')
    f.close()



class Dialog(wx.Dialog):
    def OnRadio(self,event):
        if self.rb1.GetValue(): 
            path = "modelos\\tonalidade\\"
        if self.rb2.GetValue(): 
            path = "modelos\\estilo\\"
        if self.rb3.GetValue(): 
            path = "modelos\\artista\\"
        
        dir_mod = os.path.abspath(os.path.dirname(sys.argv[0])) + "\\" + path
        self.model_dir1 = path            
        self.modelos1 = os.listdir(dir_mod)
        
        self.modelo1.Clear()
        for opcao in self.modelos1:
            self.modelo1.Append(opcao)
        self.modelo1.SetSelection(0)
        
        self.savedir1 = self.model_dir1 + self.modelos1[self.modelo1.GetSelection()]       
        #log('ONRADIO self.savedir1 = ' + self.savedir1)
        
    def OnRadio2(self,event):
        if self.rb4.GetValue(): 
            path = "modelos\\tonalidade\\"
        if self.rb5.GetValue(): 
            path = "modelos\\estilo\\"
        if self.rb6.GetValue(): 
            path = "modelos\\artista\\"
        
        dir_mod = os.path.abspath(os.path.dirname(sys.argv[0])) + "\\" + path
        self.model_dir2 = path            
        self.modelos2 = os.listdir(dir_mod)
        
        self.modelo2.Clear()
        for opcao in self.modelos2:
            self.modelo2.Append(opcao)
        self.modelo2.SetSelection(0)
        self.savedir2 = self.model_dir2 + self.modelos2[self.modelo2.GetSelection()] 
        
        #log('ONRADIO self.savedir2 = ' + self.savedir2)
            
    def OnCombo(self,event):
        self.savedir1 = self.model_dir1 + self.modelos1[self.modelo1.GetSelection()]
        self.savedir2 = self.model_dir2 + self.modelos2[self.modelo2.GetSelection()]
        #log('ONCOMBO self.savedir1 = ' + self.savedir1)
        #log('ONCOMBO self.savedir2 = ' + self.savedir2)

    def __init__(self, parent, title, caption, rb, cb):
        style = wx.DEFAULT_DIALOG_STYLE        
        super(Dialog, self).__init__(parent, -1, title, style=style)        
        #print(rb)
        #print(cb)
                        
        # Cria modelos
        dir_modelos = os.path.abspath(os.path.dirname(sys.argv[0])) + "\\modelos\\tonalidade\\"
        self.modelos1 = os.listdir(dir_modelos)
        self.modelos2 = os.listdir(dir_modelos)
        self.model_dir1 = "modelos\\tonalidade\\"                
        self.model_dir2 = "modelos\\tonalidade\\"
        
        self.modelo1 = wx.ComboBox(self, pos=(20, 40), size=(130,35), style=wx.CB_READONLY, choices=self.modelos1)
        self.txt1 = wx.StaticText(self, label='1.', pos=(5, 45))
        self.modelo2 = wx.ComboBox(self, pos=(220, 40), size=(130,35), style=wx.CB_READONLY, choices=self.modelos2)
        self.txt2 = wx.StaticText(self, label='2.', pos=(205, 45))
                
        # Seleções e diretórios
        self.modelo1.SetSelection(cb)
        self.modelo2.SetSelection(0)
        self.savedir1 = self.model_dir1 + self.modelos1[self.modelo1.GetSelection()]
        self.savedir2 = self.model_dir2 + self.modelos2[self.modelo2.GetSelection()]
        
        # Cria grupos de RadioButtons
        self.rb1 = wx.RadioButton(self, label="Tonalidade", pos=(20, 80), style = wx.RB_GROUP)        
        self.rb2 = wx.RadioButton(self, label="Estilo", pos=(20, 105))
        self.rb3 = wx.RadioButton(self, label="Artista", pos=(20, 130))        
        self.rb1.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.rb1)
        self.rb2.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.rb2)
        self.rb3.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.rb3)
        
        # Disclaimer sobre estado atual dessa função
        self.disclaimer = wx.StaticText(self, label='OBS: este modo é experimental e pode ocasionar travamentos no programa.', pos=(20, 180))                  

        
        # Pega dados e popula ComboBox
        if rb==1:
            self.rb1.SetValue(True)
        elif rb==2:
            self.rb2.SetValue(True)
        elif rb==3:
            self.rb3.SetValue(True)
            
        if self.rb1.GetValue(): 
            path = "modelos\\tonalidade\\"
        if self.rb2.GetValue(): 
            path = "modelos\\estilo\\"
        if self.rb3.GetValue(): 
            path = "modelos\\artista\\"
        
        dir_mod = os.path.abspath(os.path.dirname(sys.argv[0])) + "\\" + path
        self.model_dir1 = path            
        self.modelos1 = os.listdir(dir_mod)
        
        self.modelo1.Clear()
        for opcao in self.modelos1:
            self.modelo1.Append(opcao)
        self.modelo1.SetSelection(cb)
        
        self.savedir1 = self.model_dir1 + self.modelos1[self.modelo1.GetSelection()]       
        
        self.rb4 = wx.RadioButton(self, label="Tonalidade", pos=(220, 80), style = wx.RB_GROUP)
        self.rb4.SetValue(True)        
        self.rb5 = wx.RadioButton(self, label="Estilo", pos=(220, 105))
        self.rb6 = wx.RadioButton(self, label="Artista", pos=(220, 130))        
        self.rb4.Bind(wx.EVT_RADIOBUTTON, self.OnRadio2, self.rb4)
        self.rb5.Bind(wx.EVT_RADIOBUTTON, self.OnRadio2, self.rb5)
        self.rb6.Bind(wx.EVT_RADIOBUTTON, self.OnRadio2, self.rb6)
                
        #bind do combobox
        self.modelo1.Bind(wx.EVT_COMBOBOX, self.OnCombo)
        self.modelo2.Bind(wx.EVT_COMBOBOX, self.OnCombo)

        buttons = self.CreateButtonSizer(wx.OK|wx.CANCEL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # it's a mystery... but it works! certamente deve existir algum jeito menos bizarro
        # de misturar posições absolutas com Sizers
        for _ in range(13):
            sizer.Add(buttons, 0, wx.EXPAND|wx.RIGHT, 130)
            
        # Finaliza posicionamento
        self.SetSizerAndFit(sizer)
        self.SetSize( (450,360) )
        self.Center()