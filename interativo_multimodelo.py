# -------------------------------------------------------------------------------- #
# harmonia v1.0 - Fernando Rauber --> fernandorauber.com.br/hia
# Licença: MIT

print ("[ HarmonIA v1.0 ]\n")
print ("Carregando TensorFlow ...") # pq tão lento, Google?
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # sem erros
import tensorflow as tf
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)  # sem warnings
print ("Carregando Rede Neural ...")
import random
import argparse
import sys
from six.moves import cPickle
from tensorflow.contrib import rnn
from tensorflow.contrib import legacy_seq2seq
print ("Carregando interface e demais módulos ...")
import wx
import threading
#from wx.lib.pubsub import pub 
from pubsub  import pub   # para Pyinstaller
import squarify
import matplotlib.cm  # para cores do TreeMap
import dic_acordes 
import stats
import MIDI
import SelecionarModelo
import time
import datetime
#from pymusicxml import *   # ignorar aviso, é usado na criaçaõ de XML
import pymusicxml as mxml
import subprocess
from pathlib import Path
    
# -------------------------------------------------------------------------------- #
# Variáveis Globais 
logVerboso = 0 # logar erros e execução
myEVT_MODELO = wx.NewEventType()
EVT_MODELO = wx.PyEventBinder(myEVT_MODELO, 1)
EscolhaAcorde = threading.Event()
frame1 = None
Escolha = 'C'  # acorde inicial
NumProb = 9   # número de possibilidades exibidas 
threadErrors = [] # lista de EXCEÇÕES causadas pelas worker threads
MAX_ACORDES = 32 # número de acordes criados

# -------------------------------------------------------------------------------- #
# THREAD E EVENTOS

def log(log):    
    if logVerboso ==1:            
        if os.path.exists("log_erros.txt") == False:                
            f = open("log_erros.txt", "w", encoding="utf8")
            f.write(str(datetime.datetime.now()) )
            f.write(log)        
        elif os.path.exists("log_erros.txt") == True :
            f = open("log_erros.txt", "a", encoding="utf8")    
            f.write(str(datetime.datetime.now()) +  ' ')
            f.write(log + '\n')
        f.close()
    
class ModeloThread(threading.Thread):
    def __init__(self, parent, value, num_id, savedir, prime):
        threading.Thread.__init__(self)
        self._parent = parent
        self._value = value        
        self.num_id = num_id
        self.savedir = savedir   # diretório do modelo
        self.n = 64 # número de acordes (antigo)
        self.prime = prime   # acordes iniciais
        self._sample = 1   # sample each timestep 
        self.count = 1  # número de progressões
        self.pick = 1  # weighted ou beam, antigo
        self.width = 4  # width do beam search
        self.quiet = False  # não-verboso

    def run(self): # acionado por thread.start()                

        try:
            self.sample()
        except:
            log('erro na função sample, savedir = ' + self.savedir + ' thread = ' + self.num_id)
        
        if self.num_id == 0:  # modelo principal, sinalização para trocar/fechar programa            
            event = ModeloEvent(myEVT_MODELO, -1, self._value)
            wx.PostEvent(self._parent, event)
        
    def sample(self):
        with open(os.path.join(self.savedir, 'config.pkl'), 'rb') as f:
            saved_args = cPickle.load(f)
        with open(os.path.join(self.savedir, 'words_vocab.pkl'), 'rb') as f:
            words, vocab = cPickle.load(f)
            
        model = Model(saved_args, self.num_id, True) 
            
        with tf.Session() as sess:
            tf.global_variables_initializer().run()
            saver = tf.train.Saver(tf.global_variables())
            ckpt = tf.train.get_checkpoint_state(self.savedir)
            if ckpt and ckpt.model_checkpoint_path:
                saver.restore(sess, ckpt.model_checkpoint_path)
                model.sample(sess, words, vocab, self.savedir, self.n, self.prime, self._sample, self.pick, self.width, self.quiet)

# -------------------------------------------------------------------------------- #
# MODELO
        
class Model():
    def __init__(self, args, num_id, infer=False):        
        self.args = args
        self.num_id = num_id
        if infer:
            args.batch_size = 1
            args.seq_length = 1

        cell_fn = rnn.BasicLSTMCell
        cells = []
        
        for _ in range(args.num_layers):
            cell = cell_fn(args.rnn_size)
            cells.append(cell)

        self.cell = cell = rnn.MultiRNNCell(cells)

        #seq_lenght = num step  
        # veja tutorial sobre 'truncated backpropagation'
        # https://www.tensorflow.org/tutorials/recurrent
        
        self.input_data = tf.placeholder(tf.int32, [args.batch_size, args.seq_length])
        self.targets = tf.placeholder(tf.int32, [args.batch_size, args.seq_length])
        self.initial_state = cell.zero_state(args.batch_size, tf.float32)
        self.batch_pointer = tf.Variable(0, name="batch_pointer", trainable=False, dtype=tf.int32)
        self.inc_batch_pointer_op = tf.assign(self.batch_pointer, self.batch_pointer + 1)
        self.epoch_pointer = tf.Variable(0, name="epoch_pointer", trainable=False)
        self.batch_time = tf.Variable(0.0, name="batch_time", trainable=False)
        tf.summary.scalar("time_batch", self.batch_time)
        
        with tf.variable_scope('rnnlm'):
            softmax_w = tf.get_variable("softmax_w", [args.rnn_size, args.vocab_size])
            softmax_b = tf.get_variable("softmax_b", [args.vocab_size])
            with tf.device("/cpu:0"):                
                embedding = tf.get_variable("embedding", [args.vocab_size, args.rnn_size])
                inputs = tf.split(tf.nn.embedding_lookup(embedding, self.input_data), args.seq_length, 1)
                inputs = [tf.squeeze(input_, [1]) for input_ in inputs]                

        def loop(prev, _):
            prev = tf.matmul(prev, softmax_w) + softmax_b
            prev_symbol = tf.stop_gradient(tf.argmax(prev, 1))
            return tf.nn.embedding_lookup(embedding, prev_symbol)

        outputs, last_state = legacy_seq2seq.rnn_decoder(inputs, self.initial_state, cell, loop_function=loop if infer else None, scope='rnnlm')
        output = tf.reshape(tf.concat(outputs, 1), [-1, args.rnn_size])
        self.logits = tf.matmul(output, softmax_w) + softmax_b
        self.probs = tf.nn.softmax(self.logits)
        loss = legacy_seq2seq.sequence_loss_by_example([self.logits],
                [tf.reshape(self.targets, [-1])],
                [tf.ones([args.batch_size * args.seq_length])],
                args.vocab_size)
        self.cost = tf.reduce_sum(loss) / args.batch_size / args.seq_length
        
        self.final_state = last_state
        self.lr = tf.Variable(0.0, trainable=False)
        tvars = tf.trainable_variables()
        grads, _ = tf.clip_by_global_norm(tf.gradients(self.cost, tvars),
                args.grad_clip)
        optimizer = tf.train.AdamOptimizer(self.lr)
        self.train_op = optimizer.apply_gradients(zip(grads, tvars))

    def sample(self, sess, words, vocab, savedir, num=200, prime='C ', sampling_type=1, pick=0, width=4, quiet=False, criatividade=70, desenha=0, out=''):
        ret = ''
        if pick == 1:
            state = sess.run(self.cell.zero_state(1, tf.float32))
            for acorde in prime.split()[:-1]:
                x = np.zeros((1, 1))                
                x[0, 0] = vocab.get(acorde,0)
                feed = {self.input_data: x, self.initial_state:state}
                [state] = sess.run([self.final_state], feed)
            acorde = prime.split()[-1] # último acorde

            progressao = prime
            global NumProb            
                
            while not Escolha == 'Fechar0':  # Fechar0 sinaliza que as threads devem fechar na próxima iteração
                EscolhaAcorde.clear()
                x = np.zeros((1, 1))
                x[0, 0] = vocab.get(acorde, 0)
                feed = {self.input_data: x, self.initial_state:state}
                [probs, state] = sess.run([self.probs, self.final_state], feed)
                                    
                # print("Modelo #" + str(self.num_id) + " --> " + str(savedir) )
                 
                idx = 0
                MatrizProb = [[0 for x in range(2)] for y in range(len(words))]  
                for prob in probs[0]:
                    MatrizProb[idx][0] = idx       # indice da palavra
                    MatrizProb[idx][1] = prob*100  # probabilidade (em %)
                    idx += 1
                MatrizProb =sorted(MatrizProb, key=lambda x:x[1],reverse=True)  
                                                                
                if NumProb > len(words):
                    NumProb = len(words)                                    
                    
                # envia dados para outra thread e espera evento                                
                ultima = progressao.split()[-1]
                if ultima == 'Fechar0' or ultima == 'FecharTodos' or ultima =='Fechar1':
                    progressao = progressao[:-len(ultima)-1]
                    # print(progressao)
                
                # comunicação com a outra thread por pubsub
                pub.sendMessage("listener", num_prob=NumProb, MatrizProb=MatrizProb, words=words, progressao=progressao, num_id = self.num_id)
                
                #log('thread # ' + str(self.num_id) + ' savedir = ' + str(savedir) + '  esperando escolha')
                EscolhaAcorde.wait() # espera a escolha de um novo acorde
                # print('Escolha Recebida:' + str(Escolha) )                
                if not Escolha == 'Fechar0':  # sair do programa                    
                    while Escolha == 'Atualizar': # redesenhar interface
                        
                        EscolhaAcorde.clear()
                        if NumProb > len(words):
                            NumProb = len(words)                    

                        # filtra mensagens de Fechar
                        ultima = progressao.split()[-1]
                        if ultima == 'Fechar0':
                            progressao = progressao[:-len(ultima)-1]

                        pub.sendMessage("listener", num_prob=NumProb, MatrizProb=MatrizProb, words=words, progressao=progressao, num_id = self.num_id)
                        EscolhaAcorde.wait()
                    
                    if not Escolha=='Fechar1':  # fechar segunda thread [ segundo modelo ]
                        acorde = Escolha  # acorde escolhido
                        ret += " " + acorde  # conta        # retorno para formação de arquivo .txt (pré-formatação)
                        progressao += " " + acorde   # label para display no GUI                
            # print("modelo fechando #" + str(self.num_id) )
        return ret        

class ModeloEvent(wx.PyCommandEvent):    # enviado ao término do processo
    def __init__(self, etype, eid, value=None):
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._value = value
    def GetValue(self):
        return self._value

# -------------------------------------------------------------------------------- #
# GUI

class AcordeDialog(wx.Dialog):
    def __init__(self, parent, title, caption, espaco=False):
        style = wx.DEFAULT_DIALOG_STYLE
        super(AcordeDialog, self).__init__(parent, -1, title, style=style)
        acorde = wx.TextCtrl(self, value="")
        acorde.SetInitialSize((100, 25))
        buttons = self.CreateButtonSizer(wx.OK|wx.CANCEL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(acorde, 1, wx.EXPAND|wx.ALL, 5)
        sizer.Add(buttons, 0, wx.EXPAND|wx.ALL, 5)
        self.SetSizerAndFit(sizer)
        self.input = acorde
        acorde.Bind(wx.EVT_CHAR, self.onChar)
        self.PermitirEspaco = espaco
    def SetValue(self, value):
        self.input.SetValue(value)
    def GetValue(self):
        return self.input.GetValue()
    
    def onChar(self, event): 
        key = event.GetKeyCode()   
        if self.PermitirEspaco: # para criação de nova sequência
            if (self.input.GetValue().count(' ')) < 6:  # max 6 acordes
                acceptable_characters = "12345679()abcdefgABCDEFG#+-mMo/i " + "\b"
            else:
                acceptable_characters = "\b"
        else:
            acceptable_characters = "12345679()abcdefgABCDEFG#+-mMo/i" + "\b"
            
        if chr(key) in acceptable_characters:        
            event.Skip() 
            return
        elif key == 314 or key == 316 or key == 127 or key == 313 or key == 312:    # setas, home, end, delete
            event.Skip()
            return
        else:             
            return False

        
class Panel1(wx.Panel):     
    def PegarAcordeOuTocar(self, event,vel_strum = 0.026, transp=0, strum=True):    
        #Tocar acorde
        if self.Escutar == True:
            acorde = event.GetEventObject().acorde
            if not "nulo" in acorde:
                try:
                    notas = dic_acordes.Acordes[acorde]
                    MIDI.TocarAcorde(notas, 0.026, 0, True, self.InstrumentoMIDI)
                except:
                    #print("Acorde não encontrado no dicionário = " + acorde)                    
                    pass
                 
        #pegar acorde e Mudar acorde
        elif self.Escutar == False:                        
                ac = event.GetEventObject()
                dlg = AcordeDialog(self, 'Mudar acorde:','Mudar Acorde')
                dlg.SetValue(ac.acorde)
                x,y = ac.GetPosition()
                dlg.SetPosition( (x-150,y+25) )
                if dlg.ShowModal() == wx.ID_OK:
                    ac.acorde= dlg.GetValue().replace('o', '\u00b0') # troca diminuto
                    ac.acordeMIDI = ac.acorde # para posições alternativas
                    acordes = self.LabelProgressao.GetLabel().split()
                    acordes[ac.idx] = ac.acorde
                    self.LabelProgressao.SetLabel( ' '.join(acordes) )
                    self.ReposicionaAcordes(self)
                    # reinicia com novo modelo [não consegui sem recarregar o modelo]
                    self.Prime = self.LabelProgressao.GetLabel()
                    self.Busy(self)
                    self.MudarModelo(event)
                        
    def RotarAcordeOuTocar(self, event,vel_strum = 0.026, transp=0, strum=True):    
        #Tocar acorde
        if self.Escutar == True:
            acorde = event.GetEventObject().acordeMIDI
            #print(acorde)
            
            if not "nulo" in acorde: 
                try:
                    notas = dic_acordes.Acordes[acorde]
                    MIDI.TocarAcorde(notas, 0.026, 0, True, self.InstrumentoMIDI)
                except:
                    #print("Acorde não encontrado no dicionário = " + acorde)
                    pass
                 
        # Rota entre posições alternativas
        elif self.Escutar == False:                             
                ac = event.GetEventObject()                
                ac.pos += 1 
                acorde = ac.acorde.replace("/", "_") # acordes2xml.py --> troca caráter inválido
                # TODO: Verificar dinamicamente até quando existe
                
                if ac.pos >= 1 and ac.pos <= 4:  
                    acorde = acorde + "alt" + str(ac.pos)
                    img = os.path.abspath(os.path.dirname(sys.argv[0])) + "\\acordes\\" + acorde
                    if os.path.exists(img) == True:                
                        ac.acordeMIDI = acorde.replace("_", "/") # atualize acorde MIDI e volta caráter normal
                        bmp = self.ScaleBitmap(img,204/self.escala, 330/self.escala)            
                        ac.SetBitmap(bmp)
                        #ac.SetBitmapLabel(bmp)
                        ac.Refresh()                                    
                elif ac.pos > 4:
                    ac.pos = 0
                    img = os.path.abspath(os.path.dirname(sys.argv[0])) + "\\acordes\\" + acorde
                    if os.path.exists(img) == True:                
                        ac.acordeMIDI = acorde.replace("_", "/") # atualize acorde MIDI e volta caráter normal
                        bmp = self.ScaleBitmap(img,204/self.escala, 330/self.escala)            
                        ac.SetBitmap(bmp)
                        #ac.SetBitmapLabel(bmp)
                        ac.Refresh()                                                            
            
    def NovaMusica(self,event):
        ''' TO DO: consertar essa função no modo multimodelo '''
        
        if not wx.IsBusy():
            #if self.MultiModelo == 1:
                #msg = wx.MessageDialog(self, "Feche o modo multimodelo (no painel da direita) antes de iniciar uma nova música.", "Aviso", wx.OK)
                #msg.ShowModal()                    
            #else:
            dlg = AcordeDialog(self, 'Acordes iniciais:','Mudar Acorde', espaco=True)
            dlg.SetValue("C") 
            # talvez pegar o ACORDE mais comum do modelo como sugestão
            x,y = wx.GetMousePosition()
            dlg.SetPosition( (x,y) )
            if dlg.ShowModal() == wx.ID_OK and dlg.GetValue() != "":
                # reseta progressão e posições, recarrega modelo inicial                
                self.LabelProgressao.SetLabel ( dlg.GetValue().replace('o', '\u00b0') )
                self.Prime = self.LabelProgressao.GetLabel()
                self.ResetaAcordes(event)
                self.Busy(self)
                self.MudarModelo(event)
                self.Pagina2 = False
                self.PaginaPrev.Disable()
                self.PaginaProx.Disable()
                self.PaginaLabel.Disable()
                self.PaginaLabel.SetLabel("Pg. 1")
                
                # reseta posições dos acordes na partitura
                for obj in self.GetChildren():            
                    if type(obj) == wx._core.BitmapButton:
                        try:
                            if (obj.ac == False and obj.img == True):   # label é um acorde na partitura
                                obj.pos = 0
                        except:
                            pass                        
        
    def MudarAcorde(self,event):
        if not wx.IsBusy():
            if self.Escutar == False:
                ac = event.GetEventObject()
                dlg = AcordeDialog(self, 'Mudar acorde:','Mudar Acorde')
                dlg.SetValue(ac.acorde)
                x,y = ac.GetPosition()
                dlg.SetPosition( (x-150,y) )
                if dlg.ShowModal() == wx.ID_OK and dlg.GetValue() != "":
                    ac.acorde= dlg.GetValue().replace('o', '\u00b0') # troca diminuto
                    ac.acordeMIDI = ac.acorde # para posições alternativas
                    acordes = self.LabelProgressao.GetLabel().split()
                    acordes[ac.idx] = ac.acorde
                    self.LabelProgressao.SetLabel( ' '.join(acordes) )
                    self.ReposicionaAcordes(self)
                    # reinicia com novo modelo 
                    self.Prime = self.LabelProgressao.GetLabel()
                    self.Busy(self)
                    self.MudarModelo(event)
                        
    def PosicaoAcorde(self,event, i=0):
        widthTela, heightTela = wx.GetDisplaySize()        
        offset_x = (widthTela/3) *2  + 90   # 2/3 da tela + 30px
        offset_y = 20
       
        #divide espaçamento na tela disponível
        heightDisponivel = heightTela-180
        espacoY = (int) (heightDisponivel/4)   #  16 acordes        
        widthDisponivel = (widthTela - offset_x - 40) 
        espacoX = int(widthDisponivel/4)
        
        x = offset_x + ( (i%4)*espacoX )
        y = offset_y + ( int(i/4)*espacoY )   # antes = 86
        
        #testando pag 2
        y = offset_y + ( int(i%16/4)*espacoY )   # antes = 86
        
        return x, y

    def PosicaoAcordePNG(self,event, i=0):
        widthTela, heightTela = wx.GetDisplaySize()        
        offset_x = (widthTela/3) *2  + 80   # 2/3 da tela + 30px
        offset_y = 50

        #divide espaçamento na tela disponível
        heightDisponivel = heightTela-180
        espacoY = (int) (heightDisponivel/4)   #  16 acordes        
        widthDisponivel = (widthTela - offset_x - 40) 
        espacoX = int(widthDisponivel/4)
        
        x = offset_x + ( (i%4)*espacoX )
        y = offset_y + ( int(i/4)*espacoY )   # antes = 86
        
        #testando pag 2
        y = offset_y + ( int(i%16/4)*espacoY )   # antes = 86

        
        return x, y
    
    def ResetaAcordes(self,event):                
        self.NumAcordes = 0
        self.NumAcordesPrev = 0
        for obj in self.GetChildren():            
            if type(obj) == wx._core.StaticText:
                try:
                    if obj.ac == True:
                        obj.SetPosition( (0,0) )
                        obj.SetLabel("")
                        obj.origem = (0,0)
                        obj.acorde = ""
                except:
                    pass
            elif type(obj) == wx._core.BitmapButton:
                try:
                    if obj.ac == False and obj.img == True:
                        obj.SetPosition( (10000,10000) )
                except:
                    pass
            
                
    def ReposicionaAcordes(self,event):          
        acordes = self.LabelProgressao.GetLabel().split()            
        idx = 0
        try:
            for acorde in acordes:
                idx += 1
        except:
            pass             
        self.NumAcordes = idx
        
        if self.NumAcordes == 17 and self.NumAcordesPrev == 16:
            self.Pagina2 = True
            self.PaginaPrev.Enable()
            self.PaginaProx.Disable()
            self.PaginaLabel.Enable()
            self.PaginaLabel.SetLabel("Pg. 2")
            #print("Página 2")
            
        self.NumAcordesPrev = idx
        
        if self.NumAcordes > 4:
            self.pauta2.Show()
        if self.NumAcordes > 8:
            self.pauta3.Show()
        if self.NumAcordes > 12:
            self.pauta4.Show()
        if self.NumAcordes > 16 and self.Pagina2:
            self.pauta2.Hide()
            self.pauta3.Hide()
            self.pauta4.Hide()
        if self.NumAcordes > 20 and self.Pagina2:
            self.pauta2.Show()
        if self.NumAcordes > 24 and self.Pagina2:
            self.pauta3.Show()
        if self.NumAcordes > 28 and self.Pagina2:
            self.pauta4.Show()
        if self.NumAcordes > 16 and not self.Pagina2:
            self.pauta2.Show()
            self.pauta3.Show()
            self.pauta4.Show()            

        if self.NumAcordes < 5:  # nova música
            self.pauta2.Hide()
            self.pauta3.Hide()
            self.pauta4.Hide()
        elif self.NumAcordes < 9:  # nova música
            self.pauta3.Hide()
            self.pauta4.Hide()
        elif self.NumAcordes < 13:  # nova música
            self.pauta4.Hide()

        # busca acorde
        Acordes = []        
        for obj in self.GetChildren():            
            if type(obj) == wx._core.StaticText:
                try:
                    if (obj.ac == True):   # label é um acorde
                        Acordes.append(obj)
                except:
                    pass
                
        # posiciona acordes
        for i in range(len(acordes)):
            ac = Acordes[i]            
            ac.acorde = acordes[i]
            ac.SetLabel(acordes[i])
                        
            x,y = self.PosicaoAcorde(self, i)
            ac.SetPosition( self.PosicaoAcorde(self, i) )
            ac.origem = self.PosicaoAcorde(self, i)
            
            if self.Pagina2:                
                if i <= 15:
                    ac.Hide()
                elif i > 15:
                    ac.Show()

            if not self.Pagina2:                
                if i <= 15:
                    ac.Show()
                elif i > 15:
                    ac.Hide()

    def ReposicionaAcordesPNG(self,event):          
        acordes = self.LabelProgressao.GetLabel().split()            
        idx = 0
        try:
            for acorde in acordes:
                idx += 1
        except:
            pass
        self.NumAcordes = idx        

        # busca imagens de acordes
        Acordes = []        
        for obj in self.GetChildren():            
            if type(obj) == wx._core.BitmapButton:
                try:
                    if (obj.ac == False and obj.img == True):   # label é um acorde
                        Acordes.append(obj)
                except:
                    pass

        # posiciona acordes e recarrega imagens
        for i in range(len(acordes)):
            ac = Acordes[i]
            ac.acorde = acordes[i]
            ac.acordeMIDI = acordes[i]
            ac.SetLabel(acordes[i])
            x,y = self.PosicaoAcordePNG(self, i)
            ac.SetPosition( self.PosicaoAcordePNG(self, i) )

            if self.Pagina2:                
                if i <= 15:
                    ac.Hide()
                elif i > 15:
                    ac.Show()

            if not self.Pagina2:                
                if i <= 15:
                    ac.Show()
                elif i > 15:
                    ac.Hide()
                
            acorde = ac.acorde.replace("/", "_") # acordes2xml.py --> troca caráter inválido
            
            # to do: NONE se não existir imagem            
            if ac.pos == 0:
                img_path = os.path.abspath(os.path.dirname(sys.argv[0])) + "\\acordes\\" + acorde
                if os.path.isfile(img_path):
                    img = img_path
                else:
                    img = os.path.abspath(os.path.dirname(sys.argv[0])) + "\\acordes\\" + "NONE"            
                bmp = self.ScaleBitmap(img,204/self.escala, 330/self.escala)
                ac.SetBitmap(bmp)
                ac.Refresh()
            elif ac.pos >= 1 and ac.pos <= 4:  
                acorde = acorde + "alt" + str(ac.pos)
                img = os.path.abspath(os.path.dirname(sys.argv[0])) + "\\acordes\\" + acorde
                if os.path.exists(img) == True:                
                    ac.acordeMIDI = acorde.replace("_", "/")
                    bmp = self.ScaleBitmap(img,204/self.escala, 330/self.escala)            
                    ac.SetBitmap(bmp)
                    ac.Refresh()                                    
            elif ac.pos > 4:
                ac.pos = 0
                img = os.path.abspath(os.path.dirname(sys.argv[0])) + "\\acordes\\" + acorde
                if os.path.exists(img) == True:                
                    ac.acordeMIDI = acorde.replace("_", "/")
                    bmp = self.ScaleBitmap(img,204/self.escala, 330/self.escala)            
                    ac.SetBitmap(bmp)
                    ac.Refresh()                                                            
            
    
    def onMouseOverSave(self,event):                
        if not wx.IsBusy():
            self.SalvarBot.Hide()
            self.SalvarTXT.Show()
            self.SalvarXML.Show()
            self.Refresh()
            self.Update()
            wx.ToolTip.SetDelay(100)
            wx.ToolTip.SetReshow(100)
        
    def onMouseLeaveSave(self,event):        
        x, y = wx.GetMousePosition()
        if (y > 475-93 and y < 568-93 and x > 5 and x < 5+96):
            event.Skip()
        else:
            self.SalvarBot.Show()
            self.SalvarTXT.Hide()
            self.SalvarXML.Hide()
            self.Refresh()
            self.Update()
            wx.ToolTip.SetDelay(100)
            wx.ToolTip.SetReshow(100)
        
    def AcordeMouseOver(self,event):
        ac = event.GetEventObject()    
        self.Freeze()
        ac.SetBackgroundColour( (119,136,153) )
        ac.SetForegroundColour( (255, 255, 255) )        
        self.Thaw()        
        self.Refresh()
        self.Update()
        
    def AcordeMouseLeave(self,event):
        ac = event.GetEventObject()
        self.Freeze()
        ac.SetBackgroundColour( (255,255,255) )
        ac.SetForegroundColour( (0, 0, 168) )
        self.Thaw()
        self.Refresh()
        self.Update()                        
        
    def onProbCheck(self,event):
        if not wx.IsBusy():
            if self.MostraProb == True:
                self.MostraProb = False
                self.ProbCheck.SetValue(False)
            else:
                self.MostraProb = True  
                self.ProbCheck.SetValue(True)
            self.AtualizaMatriz()
            
    def Busy(self,event):
        self.Freeze()
        self.Calculando.Show()
        wx.BeginBusyCursor()         
        self.Thaw()
        self.Refresh()
        self.Update()
        #self.modelo.Enable(False)
        #self.rb1.Enable(False)
        #self.rb2.Enable(False)
        #self.rb3.Enable(False)
    
    def NotBusy(self,event):
        wx.EndBusyCursor()            
        self.Calculando.Hide()
        #self.modelo.Enable(True)
        #self.rb1.Enable(True)
        #self.rb2.Enable(True)
        #self.rb3.Enable(True)
    
    def MultiModelo(self,event):        
        if not wx.IsBusy() and self.MultiModelo == 0: 
            
            rb=1
            # pega dados do modelo atual
            if self.rb1.GetValue():
                rb==1                
            elif self.rb2.GetValue():
                rb=2
            elif self.rb3.GetValue():
                rb=3
            
            dlg = SelecionarModelo.Dialog(self, 'Modo Multimodelo:','Selecionar modelos', rb, self.modelo.GetSelection())
            dlg.SetPosition( (150,205) )
            if dlg.ShowModal() == wx.ID_OK:
                self.Busy(self)
                self.MultiModeloBotao.Hide()
                self.MonoModeloBotao.Show()   
                self.MultiModelo = 1
                self.modelo.Enable(False)
                self.rb1.Enable(False)
                self.rb2.Enable(False)
                self.rb3.Enable(False)                        
                self.txt1.Enable(False)
                self.stats.Enable(False)            
                
                #print("savedir1")
                #print(dlg.savedir1)
                #print("savedir2")
                #print(dlg.savedir2)
                
                self.SaveDir = dlg.savedir1
                self.SaveDir2 = dlg.savedir2
                                
                #ATUALIZAR MODELO AQUI
                self.nome_modelo1.SetLabel(dlg.savedir1)
                self.nome_modelo2.SetLabel(dlg.savedir2)                
                self.nome_modelo1.Show()
                self.nome_modelo2.Show()
                self.stats1.Show()
                self.stats2.Show()

                #cria thread
                modelo2 = ModeloThread(self, 1, 1, dlg.savedir2, self.Prime)
                modelo2.start()            
                                                
                self.AtualizaMatriz()
                self.Busy(self)  # necessário chamar novamente
                
        if not wx.IsBusy() and self.MultiModelo == 1:
            self.MultiModeloBotao.Show()
            self.MonoModeloBotao.Hide()                   
            self.Busy(self)            
            self.MultiModelo = 0
            self.modelo.Enable(True)
            self.rb1.Enable(True)
            self.rb2.Enable(True)
            self.rb3.Enable(True)                        
            self.txt1.Enable(True)
            self.stats.Enable(True)            
            self.nome_modelo1.Hide()
            self.nome_modelo2.Hide()
            global Escolha        
            
            Escolha = 'Fechar1'
            EscolhaAcorde.set()
            botoes = self.ListaBotoes(self,1)            
            for bot in botoes:
                bot.SetPosition( (0,0) )
                bot.SetSize( (0,0) )
                
            self.stats1.Hide()
            self.stats2.Hide()
            self.AtualizaMatriz()
            self.Busy(self)  # necessário chamar novamente
            
    def MudaMatriz(self,event,inc=0):        
        global NumProb
        np = NumProb
        Estados = [ 2, 3, 4, 6, 9, 12, 16, 21, 25, 30, 36, 44, 54, 67, 74]        
        
        if not self.EstadoMatriz+inc > len(Estados) or self.EstadoMatriz+inc < 0:
            self.EstadoMatriz += inc
        
        if self.EstadoMatriz < 0:
            self.EstadoMatriz = 0
        elif self.EstadoMatriz > len(Estados)-1:
            self.EstadoMatriz = len(Estados)-1
                
        NumProb = Estados[self.EstadoMatriz]
        
        if not np == NumProb:
            self.AtualizaMatriz()
        
    def MudaEscolha(self, escolha='Atualizar'):
        global Escolha        
        Escolha = escolha        
        EscolhaAcorde.set()
    
    def AtualizaMatriz(self):
        global Escolha
        Escolha = 'Atualizar'
        EscolhaAcorde.set()
        self.ManterCor = True
        
    def TrocarCursor(self,event, mouse=False):
        if not wx.IsBusy():            
            if mouse==False:
                if self.AvisoEscutar == False:
                    self.AvisoEscutar = True
                    erro = wx.MessageDialog(self, "Clique em qualquer acorde para escutá-lo.\n\nAlterne entre o modo de escuta/escolha utilizando\no botão direito do mouse.", "Modo escuta", wx.OK)
                    erro.ShowModal()
                
            if self.Escutar == False:
                self.SetCursor( wx.Cursor("imagens/guitar", wx.BITMAP_TYPE_CUR) )
                self.Escutar =True 
            elif self.Escutar == True:
                self.SetCursor( wx.Cursor(wx.CURSOR_ARROW) )
                self.Escutar = False
                
        
    def AvancaPagina(self,event):
        if not self.Pagina2:
            self.Pagina2 = True
            self.PaginaProx.Disable()
            self.PaginaPrev.Enable()
            self.PaginaLabel.SetLabel("Pg. 2")
            self.ReposicionaAcordes(self)
            self.ReposicionaAcordesPNG(self)

    def RetrocedePagina(self,event):
        if self.Pagina2:
            self.Pagina2 = False
            self.PaginaPrev.Disable()
            self.PaginaProx.Enable()            
            self.PaginaLabel.SetLabel("Pg. 1")
            self.ReposicionaAcordes(self)
            self.ReposicionaAcordesPNG(self)
            
    def FecharApp(self,event):        
        sair = wx.MessageBox("Sair do programa?", "Fechar Programa", wx.YES_NO, self) 
        if sair == wx.YES:
            self.TrocarModelo = False
            self.Busy(self)
            global Escolha            
            Escolha = 'Fechar0'
            EscolhaAcorde.set()

    def MostrarAjuda(self,event):
        if not wx.IsBusy():            
            msg = wx.MessageDialog(self, "harmonIA v1.0 - Ajuda rápida: \n\n- Clique nos acordes para montar sua progressão. Botões maiores representam as probabilidades de continuação mais comuns no modelo escolhido.\n\n- Os botões + e - aumentam ou diminuem o número de acordes mostrados.\n\n- Clique na partitura para alterar a posição do acorde ou na cifra para alterar a harmonia escolhida.\n\n- O botão direito do mouse alterna entre o modo de escolha ou escuta do acorde.\n\nUtilize a lista no canto inferior direito para alternar o modelo de geração (tonalidade, estilo ou artista)\n\n- O modo multimodelo permite a utilização simultânea dois modelos\n\nPara informações e progressões mais comuns do modelo, clique no botão 'i'\n\nSalve sua criação em formato .txt (cifra pura) ou MusicXML (partitura) \n\nVisite http://fernandorauber.com.br para mais informações e atualizações.", "harmonIA v1.0 por Fernando Rauber", wx.OK)
            msg.ShowModal()
            
    def OnModelo(self, event):                
        if self.TrocarModelo == False:            
            time.sleep(1)
            self.Close()
            frame1.Close()                
        elif self.TrocarModelo == True:
            # reinicia com novo modelo
            global Escolha
            Escolha = 'Atualizar'  # sem escolha, somente atualizar layout
            EscolhaAcorde.set()
                        
            if self.MultiModelo ==1:            
                # pega pelos labels do modelo e cria as duas threads
                worker = ModeloThread(self, 1, 0, self.nome_modelo1.GetLabel(), self.Prime)
                #print(self.nome_modelo1.GetLabel() )
                worker.start()            
                
                modelo2 = ModeloThread(self, 1, 1, self.nome_modelo2.GetLabel(), self.Prime)
                modelo2.start()            
            else:
                # pega pelo modelo escolhido no ComboBox
                worker = ModeloThread(self, 1, 0, self.SaveDir, self.Prime)
                worker.start()

        
    def EscolhaAleatoria(self, event):        
        if not wx.IsBusy():
            global Escolha
            global NumProb
            
            if self.NumAcordes < MAX_ACORDES:
            
                AcordeAleatorio = 'X'
                
                while 'X' in AcordeAleatorio:
                    AcordeAleatorio = ''                
                    r = random.randint(0, NumProb-1)                
                    i = 0
                    
                    #log('escolha aleatoria r = ' + str(r) )
                    
                    for obj in self.GetChildren():            
                        if type(obj) == wx._core.Button:                            
                            if r == i:
                                try:                                    
                                    Escolha = obj.acorde
                                    EscolhaAcorde.set()                                    
                                    MIDI.TocarAcorde(dic_acordes.Acordes[obj.acorde], 0.026, 0, True, self.InstrumentoMIDI)
                                    #log('escolha aleatoria = ' + str(obj.acorde) )
                                    break                                
                                except:
                                    pass
                            i += 1                                     
                
    def EscolherAcorde(self, event, escolha=0):        
        botao = event.GetEventObject()
        escolha = botao.escolha
        
        if not "nulo" in event.GetEventObject().acorde:   # ignora marcadores |X|        
            #print(escolha)
                    
            if not wx.IsBusy():    
                if not self.Escutar:     
                    if self.NumAcordes < MAX_ACORDES:
                        global Escolha
                        Escolha = event.GetEventObject().acorde
                        EscolhaAcorde.set()
                    else:
                        erro = wx.MessageDialog(self, "Número máximo de acordes excedido,\ninicie uma nova música.", "Erro!", wx.OK|wx.ICON_EXCLAMATION)
                        erro.ShowModal()          
                    
                if not Escolha=='Fechar0' and not Escolha=='Fechar1':
                    acorde = event.GetEventObject().acorde
                try:
                    MIDI.TocarAcorde(dic_acordes.Acordes[acorde], 0.026, 0, True, self.InstrumentoMIDI)
                    #MIDI.TocarAcorde(dic_acordes.Acordes[acorde], 0.026)
                    #print(str(acorde) + ": ", end ='')
                    #xprint(MIDI.NotasDoAcorde(dic_acordes.Acordes[acorde]))
                except:
                    #print("acorde não encontrado em dic_acordes.py: " + acorde)
                    log("acorde não encontrado em dic_acordes.py: " + acorde)
        else:
            print("escolha nula")
                
    def CriaAlternativas(self, num_prob, MatrizProb, words, progressao, num_id):
        widthTela, heightTela = wx.GetDisplaySize()
        
        #log('cria alternativas, num_id = ' + str(num_id) + ' multimodelo= ' + str(self.MultiModelo) )
        
        # chamo isso aqui na CriaAlternativas e em ReposicionarBotoes pois às vezes a ordem de
        # execução das threads impede que a interface seja liberada na hora correta...
        if wx.IsBusy():
            self.NotBusy(self)
            #log('CriaAlternativas() dispara self.NotBusy(self)' )
            
        if self.MultiModelo==1:
            
            #MODELO 1
            if num_id == 0:            
                offset_x = 105
                offset_y = 30
                width = 930 / 2
                height = heightTela-10-offset_y
                prob, prob2, acordes, x, y, dx, dy =  ([] for _ in range(7))
                
                # prepara TreeMaps
                for idx in range(num_prob):                    
                    if not "|X" in words[MatrizProb[idx][0]]:
                        acordes.append( words[MatrizProb[idx][0]] )    
                        prob.append( MatrizProb[idx][1] )
                    else:
                        acordes.append( "nulo" )    # # esconde marcadores ("|X|")
                        prob.append( 0.0000000000001 )  # esconde marcadores
                        
                prob_norm = squarify.normalize_sizes(prob, width, height)                                 
                
                # Robin Hood: rouba dos botoes grandes para aumentar os pequenos
                if NumProb > 6:
                    ip = 0
                    compensacao = 0
                    for p in prob_norm:            
                        if p < 1000 and p > 0.01: # tamanho mínimo
                            compensacao += 1000 -p
                            prob_norm[ip] = 1000  # muda tamanho mínimo
                        ip += 1
                    
                    ''' TO DO:                         
                        SE APÓS A COMPENSAÇÃO ALGUM DOS BOTÕES FFICAR COM ÁREA
                        MENOR QUE 1000, resetar e aumentar o número de divisões, etc..
                    '''
                    
                    prob_norm[0] -= compensacao / 4
                    prob_norm[1] -= compensacao / 4
                    prob_norm[2] -= compensacao / 4        
                    prob_norm[3] -= compensacao / 4
                            
                # copia progressão para variável global que vai ser uzada na troca do modelo
                self.LabelProgressao.SetLabel(progressao)                 
                self.Prime = progressao
                
                cmap = matplotlib.cm.get_cmap()
                if self.ManterCor == True:
                    colors = self.LastColormap
                    self.ManterCor = False
                else:
                    colors = [cmap(random.random()) for i in range(80)]
                rects = squarify.squarify(prob_norm, offset_x, offset_y, width, height)
                self.LastColormap = colors
                        
                for rect in rects:
                    x.append( rect['x'] )
                    y.append( rect['y'] )
                    dx.append( rect['dx'] )
                    dy.append( rect['dy'] )
                    
                for p in prob:
                    p_str = "{0:.1f}".format(p)                    
                    prob2.append(p_str)
                    
                # Desenha o Treemap
                alpha=0.6
                botoes = self.ListaBotoes(self,0)
                try:
                    self.ReposicionaBotoes(self, botoes, acordes, prob2, x,y,dx,dy, colors, alpha)
                    self.ReposicionaAcordes(self)
                    self.ReposicionaAcordesPNG(self)
                except:
                    #log('erro com a função reposiciona botoes ou acordes (Modelo #0)')
                    pass
                
            #MODELO 2
            elif num_id == 1:    
                offset_x = 580
                offset_y = 30
                width = 930 / 2
                height = heightTela-10-offset_y
                prob, prob2, acordes, x, y, dx, dy =  ([] for _ in range(7))
                
                # prepara TreeMaps
                for idx in range(num_prob):
                    # isso não existe nos datasets mais recentes, excluir com cuidado
                    if not "|X" in words[MatrizProb[idx][0]]: 
                        acordes.append( words[MatrizProb[idx][0]] )    
                        prob.append( MatrizProb[idx][1] )
                    else:
                        acordes.append( "nulo" )    # # esconde marcadores ("|X|")
                        prob.append( 0.0000000000001 )  # esconde marcadores
                prob_norm = squarify.normalize_sizes(prob, width, height)                                 
                
                # Robin Hood: rouba dos botoes grandes para aumentar os pequenos
                if NumProb > 6:
                    ip = 0
                    compensacao = 0
                    for p in prob_norm:            
                        if p < 1000 and p > 0.01: # tamanho mínimo
                            compensacao += 1000 -p
                            prob_norm[ip] = 1000  # muda tamanho mínimo
                        ip += 1
                    prob_norm[0] -= compensacao / 4
                    prob_norm[1] -= compensacao / 4
                    prob_norm[2] -= compensacao / 4        
                    prob_norm[3] -= compensacao / 4
                            
                # copia progressão para variável global que vai ser uzada na troca do modelo
                self.LabelProgressao.SetLabel(progressao)                 
                self.Prime = progressao
                
                cmap = matplotlib.cm.get_cmap()
                if self.ManterCor == True:
                    colors = self.LastColormap
                    self.ManterCor = False
                else:
                    colors = [cmap(random.random()) for i in range(80)]
                rects = squarify.squarify(prob_norm, offset_x, offset_y, width, height)
                self.LastColormap = colors
                        
                for rect in rects:
                    x.append( rect['x'] )
                    y.append( rect['y'] )
                    dx.append( rect['dx'] )
                    dy.append( rect['dy'] )
                    
                for p in prob:
                    p_str = "{0:.1f}".format(p)                    
                    prob2.append(p_str)
                    
                # Desenha o Treemap
                alpha=0.6
                botoes = self.ListaBotoes(self,1)
                try:
                    self.ReposicionaBotoes(self, botoes, acordes, prob2, x,y,dx,dy, colors, alpha)
                    self.ReposicionaAcordes(self)
                    self.ReposicionaAcordesPNG(self)
                except:
                    #log('erro com a função reposiciona botoes ou acordes (Modelo #1)')
                    pass

            
        elif self.MultiModelo==0:
            # Atributos do TreeMap                        
            offset_x = 105
            offset_y = 10
            width = 930
            width = (widthTela/3)*2 - offset_x  # 2/3 da tela - offset
            height = heightTela -10-offset_y
            prob, prob2, acordes, x, y, dx, dy =  ([] for _ in range(7))
                                
            # prepara TreeMap
            #sobra = 0
            acordes.clear()
            prob.clear()
            for idx in range(num_prob):
                if not "|X" in words[MatrizProb[idx][0]]:
                    acordes.append( words[MatrizProb[idx][0]] )    
                    prob.append( MatrizProb[idx][1] )
                else:
                    acordes.append( "nulo" )    # # esconde marcadores ("|X|")
                    prob.append( 0.0000000000001 )  # esconde marcadores
                 
                    #sobra += MatrizProb[idx][1]                    
            #if sobra > 0:
                #print(sobra)
                #for indice in range(num_prob):
                #MatrizProb[0][1] = MatrizProb[indice][1] + sobra/num_prob  # divide excendente entre todos outros (BUG AQUI)


            prob_norm = squarify.normalize_sizes(prob, width, height)                     
            
            # robin hood: rouba dos botoes grandes para aumentar os pequenos
            if NumProb > 6:
                ip = 0
                compensacao = 0
                for p in prob_norm:            
                    if p < 1000 and p > 0.01: # tamanho mínimo
                        compensacao += 1000 -p
                        prob_norm[ip] = 1000  # muda tamanho mínimo
                    ip += 1
                prob_norm[0] -= compensacao / 4
                prob_norm[1] -= compensacao / 4
                prob_norm[2] -= compensacao / 4        
                prob_norm[3] -= compensacao / 4
                        
            # copia progressão para variável global que vai ser uzada na troca do modelo
            self.LabelProgressao.SetLabel(progressao)             
            self.Prime = progressao
            
            cmap = matplotlib.cm.get_cmap()                
            if self.ManterCor == True:
                colors = self.LastColormap
                self.ManterCor = False
            else:
                colors = [cmap(random.random()) for i in range(80)]
            rects = squarify.squarify(prob_norm, offset_x, offset_y, width, height)
            self.LastColormap = colors
                    
            for rect in rects:
                x.append( rect['x'] )
                y.append( rect['y'] )
                dx.append( rect['dx'] )
                dy.append( rect['dy'] )
                
            for p in prob:
                p_str = "{0:.1f}".format(p)                    
                prob2.append(p_str)
                
            # Desenha o Treemap
            alpha=0.6
            botoes = self.ListaBotoes(self,0)
            try:
                self.ReposicionaBotoes(self, botoes, acordes, prob2, x,y,dx,dy, colors, alpha)
                self.ReposicionaAcordes(self)
                self.ReposicionaAcordesPNG(self)
            except:
                #log('erro com a função reposiciona botoes ou acordes. SaveDir = ' + self.SaveDir)
                pass
                
                # mostra msg inicial na primeira vez que a interface for desenhada        
        if self.ajudaInicial:            
            msg = wx.MessageDialog(self, "harmonIA v1.0\n\n- Bem-vindo! Clique no botão '?' no canto inferior esquerdo para obter ajuda.", "harmonIA v1.0 por Fernando Rauber", wx.OK)
            msg.ShowModal()
            self.ajudaInicial = False


    def ReposicionaBotoes(self,event, botoes, acordes, prob2, x,y,dx,dy, colors, alpha):        
        
        if wx.IsBusy():
            self.NotBusy(self)
            #log('ReposicionaBotoes() dispara self.NotBusy(self)' )
        self.Freeze()
        i = 0
        for b in botoes:
            try:                
                if(self.MostraProb==True):                        
                    b.SetLabel( acordes[i] + "\n" + str(prob2[i]) )
                    if float(prob2[i]) < 0.2 and float(prob2[i]) > 0.1:
                        b.SetLabel( acordes[i])
                    if float(prob2[i]) < 0.008: # LIMIAR PROBABILÍSTICO
                        b.SetLabel( acordes[i] + "0")
                else:
                    b.SetLabel( acordes[i] )
                                    
                b.SetBackgroundColour( ( alpha*colors[i][0]*255 + (1-alpha)*255,alpha*colors[i][1]*255 + (1-alpha)*255,alpha*colors[i][2]*255 + (1-alpha)*255 )  )                
                # pad para não faltar espaço (por conta do arrendodamente de dx/dy de floats para int)
                incx = 0 
                incy = 0
                if (dx[i] > 10):
                    incx = 1
                if (dy[i] > 10):
                    incy = 1
                b.SetSize(dx[i]+incx,dy[i]+incy)                
                b.SetPosition( wx.Point(x[i], y[i]) )
                b.acorde = acordes[i]
            except:
                pass
            i+= 1   
            
        self.Thaw()
        self.Refresh()
        self.Update()
                                
    def ListaBotoes(self, event, num_id=0):
        botoes = []
        for obj in self.GetChildren():            
            if type(obj) == wx._core.Button:
                try:
                    if num_id==0:
                        if obj.acordeBut == True: #primeiro modelo
                            botoes.append(obj)
                    elif num_id==1:
                        if obj.acordeBut2 == True: #segundo modelo
                            botoes.append(obj)
                except:
                    pass
        return botoes
    
    def SalvaTXT(self, event):  
        if not wx.IsBusy():
            dir_atual = os.getcwd() + "\musicas"
            nome = self.modelos[self.modelo.GetSelection()]
            i = 00
            inc = "%02d" % i        
            saida = "musicas\\" + nome + inc + ".txt"        
            if os.path.exists(saida) == True:            
                while os.path.exists(saida) == True:
                    i += 1
                    inc = "%02d" % i
                    saida = "musicas\\" + nome + inc + ".txt"        
            saida = nome + inc + ".txt"
            dlg = wx.FileDialog(self, message="Salvar cifra  ...", defaultDir=dir_atual, defaultFile=saida, wildcard="Arquivo TXT (*.txt)|*.txt", style=wx.FD_SAVE)
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()                  
                with open(path, 'w') as f:
                    contador=0
                    f.write("O Sucesso do Momento (por harmonIA v1.0)\n----------------------------------------\n\n") 
                    for acorde in str(self.LabelProgressao.GetLabel() ).split():
                        contador+=1                        
                        espaco = 18 - len(acorde)
                        espacamento = ""
                        for _ in range(espaco):
                            espacamento += " "
                        f.write(acorde + espacamento + " | " )
                        if contador % 4 == 0:
                            f.write('\n')            
            subprocess.Popen("notepad " + path)  
            dlg.Destroy()
        
    def SalvaXML(self, event):   
        # ou salvar em .msxc, melhor talvez...
        if not wx.IsBusy():
            dir_atual = os.getcwd() + "\musicas"
            nome = self.modelos[self.modelo.GetSelection()]  #saida                        
            i = 00
            inc = "%02d" % i        
            saida = "musicas\\" + nome + inc + ".xml"
            if os.path.exists(saida) == True:            
                while os.path.exists(saida) == True:
                    i += 1
                    inc = "%02d" % i
                    saida = "musicas\\" + nome + inc + ".xml"
            saida = nome + inc + ".xml"
            dlg = wx.FileDialog(self, message="Salvar partitura MusicXML  ...", defaultDir=dir_atual, defaultFile=saida, wildcard="Partitura MusicXML (*.xml)|*.xml", style=wx.FD_SAVE)
            
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                
                # cria partitura
                                
                score = mxml.Score(title="O sucesso do momento", composer="harmonIA v1.0\n(e um humano atrapalhando)")
                part = mxml.Part("Guitar")
                score.append(part)

                # lê acordes                
                Acordes = []
                for acorde in str(self.LabelProgressao.GetLabel() ).split():
                    Acordes.append(acorde)
                    
                # Ler posições de acordes
                AcordesPos = []        
                for obj in self.GetChildren():            
                    if type(obj) == wx._core.BitmapButton:
                        try:
                            if (obj.ac == False and obj.img == True):   # label é um acorde PNG
                                AcordesPos.append(obj)
                        except:
                            pass
                
                compassos = []
                for i in range(len(Acordes)):
                    if i == 0:
                        m = mxml.Measure(time_signature=(4, 4), clef=("G", 2, -1) if i == 0 else None)
                    elif i == len(Acordes)-1:
                        m = mxml.Measure(barline='end',clef=("G", 2, -1) if i == 0 else None)                    
                    else:                                    
                        m = mxml.Measure(clef=("G", 2, -1) if i == 0 else None)
                                        
                    # Lê posições alternativas se necessária                    
                    if AcordesPos[i].pos >= 1 and AcordesPos[i].pos <= 4:
                        AcNome = Acordes[i] + "alt" + str(AcordesPos[i].pos)
                        notas = dic_acordes.Acordes[AcNome]
                    else:
                        notas = dic_acordes.Acordes[Acordes[i]] # posição padrão

                    # converte número em notas
                    NotasAcorde = []                    
                    NomeNotas = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B']
                    for nota in notas:
                        nome = NomeNotas[nota%12] + str(int(nota/12)-1)
                        NotasAcorde.append(nome)
                                            
                    for beat_num in range(4):
                        if (i + beat_num) % 4 == 0:
                            m.append(mxml.Chord(NotasAcorde, 4.0, directions=mxml.TextAnnotation(Acordes[i]) ))                    
                    compassos.append(m)
                    
                part.extend(compassos)                
                score.export_to_file(path)
                
                mscore = Path("/Program Files/MuseScore 3/bin/MuseScore3.exe")   # instalação padrão no Windows
                if mscore.is_file():
                    #print("MuseScore 3 encontrado")
                    subprocess.Popen(str(mscore) + " " + path)   
                else:
                    print("MuseScore 3 não encontrado em /Program Files/MuseScore 3/bin/MuseScore3.exe")
                        
            dlg.Destroy()
        
    def ScaleBitmap(self, img, width, height):        
        bmp = wx.Bitmap(img, wx.BITMAP_TYPE_ANY)        
        #image = wx.ImageFromBitmap(bmp)   # depreciado
        image = wx.Bitmap.ConvertToImage(bmp)
        resized = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        #bmp = wx.BitmapFromImage(resized) # depreciado
        bmp = wx.Bitmap(resized, wx.BITMAP_TYPE_ANY)        
        return bmp

    def MudarModelo(self,event):        
        self.SaveDir = self.model_dir + self.modelos[self.modelo.GetSelection()]        
        self.nome_modelo.SetLabel(self.modelos[self.modelo.GetSelection()])
        self.TrocarModelo = True
        global Escolha
        Escolha = 'Fechar0'  # fechar
        EscolhaAcorde.set()
    
    def OnCombo(self,event):
        self.Busy(self)
        self.MudarModelo(event)
    
    def OnRadio(self,event):
        self.Busy(self)
        
        if self.rb1.GetValue():                        
            dir_mod = os.path.abspath(os.path.dirname(sys.argv[0])) + "\\modelos\\tonalidade\\"            
            self.model_dir = "modelos\\tonalidade\\"            
        if self.rb2.GetValue():            
            dir_mod = os.path.abspath(os.path.dirname(sys.argv[0])) + "\\modelos\\estilo\\"
            self.model_dir = "modelos\\estilo\\"                        
        if self.rb3.GetValue():
            dir_mod = os.path.abspath(os.path.dirname(sys.argv[0])) + "\\modelos\\artista\\"
            self.model_dir = "modelos\\artista\\"
                        
        self.modelos = os.listdir(dir_mod)
        self.modelo.Clear()
        for opcao in self.modelos:
            self.modelo.Append(opcao)
        self.modelo.SetSelection(0)      
        
        # mudar modelo
        self.SaveDir = self.model_dir + self.modelos[self.modelo.GetSelection()]                            
        self.nome_modelo.SetLabel(self.modelos[self.modelo.GetSelection()])
        self.MudarModelo(event)
    
    def MostraStats(self,event, diretorio):
        if not wx.IsBusy():            
            self.Busy(self)
            dlg = stats.PainelStats(self, diretorio, self.nome_modelo.GetLabel() )
            self.NotBusy(self)
            dlg.ShowModal()
            dlg.Destroy()
            
    def MostraStats1(self,event, diretorio):
        if not wx.IsBusy():            
            self.Busy(self)
            dlg = stats.PainelStats(self, diretorio, self.nome_modelo.GetLabel() )
            self.NotBusy(self)
            dlg.ShowModal()
            dlg.Destroy()            
            
    def MostraStats2(self,event, diretorio):   # posso transformar isso em uma função única com a anterior
        if not wx.IsBusy():             
            self.Busy(self)
            dlg = stats.PainelStats(self, diretorio, self.nome_modelo2.GetLabel() )
            self.NotBusy(self)
            dlg.ShowModal()
            dlg.Destroy()        
    
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)        
        self.SetBackgroundColour( (255,255,255) )
        
        widthTela, heightTela = wx.GetDisplaySize()
        #print("Resolução: " + str(widthTela)+"x"+str(heightTela))
        
        # ComboBox modelo
        FonteMaior = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL)         
        dir_modelos = os.path.abspath(os.path.dirname(sys.argv[0])) + "\\modelos\\tonalidade\\"
        self.modelos = os.listdir(dir_modelos)
        self.model_dir = "modelos\\tonalidade\\"                
        self.txt1 = wx.StaticText(self, label='Modelo:', pos=( (widthTela/3)*2+30, heightTela-75))   
        self.txt1.SetFont(FonteMaior)
        self.modelo = wx.ComboBox(self, pos=( (widthTela/3)*2+30+75, heightTela-80), size=(190,25), style=wx.CB_READONLY, choices=self.modelos)
        self.modelo.SetFont(FonteMaior)
        self.modelo.SetBackgroundColour((255,255,255))
        self.modelo.SetSelection(4)
         
        # RadioButtons
        self.rb1 = wx.RadioButton(self, label="Tonalidade", pos=( (widthTela/3)*2+30, heightTela-115), size=(115,25))        
        self.rb1.SetValue(True)
        self.rb1.SetFont(FonteMaior)
        self.rb2 = wx.RadioButton(self, label="Estilo", pos=((widthTela/3)*2+30+135, heightTela-115), size=(80,25))
        self.rb2.SetFont(FonteMaior)
        self.rb3 = wx.RadioButton(self, label="Artista", pos=((widthTela/3)*2+30+135+95, heightTela-115), size=(80,25))
        self.rb3.SetFont(FonteMaior)
        self.rb1.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.rb1)
        self.rb2.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.rb2)
        self.rb3.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.rb3)
        
        # Congela interface
        self.Calculando = wx.StaticText(self, label='Aguarde ...', pos=(widthTela/2-150, heightTela/2))
        self.Calculando.SetFont(FonteMaior)
        self.Calculando.SetForegroundColour((255,255,255)) # set text color
        self.Calculando.SetBackgroundColour((0,0,255)) # set text back color
        self.Calculando.Hide()
        self.Busy(self)
        self.SaveDir = 'modelos\\tonalidade\\f'
        self.SaveDir2 = 'modelos\\tonalidade\\f'
        
        self.Prime = "C7M "  # feed inicial para rede neural
                
        # Cria botões
        for i in range(0,80): # Botões para escolha de acordes (Modelo #1)
            but = wx.Button(self, label='', pos= (0, 0), size=(0,0), style = wx.BORDER_NONE | wx.CLIP_CHILDREN)
            but.escolha = i
            but.Bind(wx.EVT_BUTTON, lambda event: self.EscolherAcorde(event,but.escolha))
            but.acordeBut = True
            
        for i in range(0,80): # Botões para escolha de acordes (Modelo #2)
            but = wx.Button(self, label='', pos= (0, 0), size=(0,0), style = wx.BORDER_NONE)
            but.escolha = i
            but.Bind(wx.EVT_BUTTON, lambda event: self.EscolherAcorde(event,but.escolha))
            but.acordeBut2 = True
            
        self.LabelProgressao = wx.StaticText(self, label="C7M", pos=(1070, 100))        
        font = wx.Font(0, wx.DEFAULT, wx.NORMAL, wx.NORMAL)        
        self.LabelProgressao.SetFont(font)          
        self.MostraProb = False        
        self.Pagina2 = False
        
        # Carrega imagens
        self.img1 = self.ScaleBitmap("imagens/mais", 64,64)
        self.img2 = self.ScaleBitmap("imagens/menos", 64,64)
        self.img3 = self.ScaleBitmap("imagens/guitar2", 64,64)
        self.img4 = self.ScaleBitmap("imagens/dice", 64,64)
        self.img5 = self.ScaleBitmap("imagens/briga", 48, 48)
        self.img6 = self.ScaleBitmap("imagens/save", 48, 48)
        self.img7 = self.ScaleBitmap("imagens/txt", 48, 48)
        self.img8 = self.ScaleBitmap("imagens/xml", 48, 48)
        self.img9 = self.ScaleBitmap("imagens/fechar2", 64, 64)
        self.img10 = self.ScaleBitmap("imagens/novo", 64,64)
        self.img11 = self.ScaleBitmap("imagens/info", 26,26)
        self.img12 = self.ScaleBitmap("imagens/homi", 48, 48)
        self.seta1 = self.ScaleBitmap("imagens/seta_voltar", 36,36)
        self.seta2 = self.ScaleBitmap("imagens/seta_avancar", 36,36)
        self.imgajuda = self.ScaleBitmap("imagens/ajuda", 64, 64)
        
        # Botões laterais
        
        botY = int(round( (heightTela-20) / 9) )  # divide espaço para os botoes e aredonda
        #print("heightbotoes = " + str(botY) )
        
        y = 10 # offset y
        self.Mais = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=self.img1,size=(96,botY), pos=(5, y+botY*0) )
        self.Menos = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=self.img2,size=(96,botY), pos=(5, y+botY*1) )
        self.EscutarAcorde = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=self.img3,size=(96,botY), pos=(5, y+botY*2) )
        self.Aleatorio = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=self.img4,size=(96,botY), pos=(5, y+botY*3) )        
        self.SalvarBot = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=self.img6,size=(96,botY), pos=(5, y+botY*4) )
        self.SalvarTXT = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=self.img7,size=(50,botY), pos=(5, y+botY*4) )
        self.SalvarXML = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=self.img8,size=(48,botY), pos=(5+48, y+botY*4) )
        self.MultiModeloBotao = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=self.img5,size=(96,botY), pos=(5, y+botY*5) )
        self.MonoModeloBotao = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=self.img12,size=(96,botY), pos=(5, y+botY*5) )
        self.MonoModeloBotao.Hide()
        self.Novo = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=self.img10,size=(96,botY), pos=(5, y+botY*6) )
        self.Sair = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=self.img9,size=(96,botY), pos=(5, y+botY*7) )
        self.BotaoAjuda = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=self.imgajuda,size=(96,botY), pos=(5, y+botY*8) )
        
        #botões de estatísticas
        self.stats = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=self.img11,size=(26,26), pos=((widthTela/3)*2+30+270,heightTela-80), style = wx.BORDER_NONE)
        self.stats.SetBackgroundColour( (255,255,255) )
        self.stats.SetToolTip(wx.ToolTip("Informações do modelo"))
        self.stats.Bind(wx.EVT_BUTTON, lambda event: self.MostraStats(event,self.SaveDir))
        self.stats.Show()
        
        self.stats1 = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=self.img11,size=(26,26), pos=(105,0), style = wx.BORDER_NONE)
        self.stats1.SetBackgroundColour( (255,255,255) )
        self.stats1.SetToolTip(wx.ToolTip("Informações do modelo"))
        self.stats1.Bind(wx.EVT_BUTTON, lambda event: self.MostraStats(event,self.SaveDir))
        self.stats1.Hide() 
                
        self.stats2 = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=self.img11,size=(26,26), pos=(575,0), style = wx.BORDER_NONE)
        self.stats2.SetBackgroundColour( (255,255,255) )
        self.stats2.SetToolTip(wx.ToolTip("Informações do modelo"))
        self.stats2.Bind(wx.EVT_BUTTON, lambda event: self.MostraStats2(event,self.SaveDir2))
        self.stats2.Hide()
                
        # Alterna entre páginas
        self.PaginaPrev = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=self.seta1,size=(36,36), pos=( (widthTela/3)*2+185, heightTela-150 ), style = wx.BORDER_NONE )
        self.PaginaProx = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=self.seta2,size=(36,36), pos=( (widthTela/3)*2+285, heightTela-150 ), style = wx.BORDER_NONE )        
        self.PaginaPrev.SetBackgroundColour((255,255,255))
        self.PaginaProx.SetBackgroundColour((255,255,255))
        self.PaginaPrev.SetToolTip(wx.ToolTip("Página anterior"))
        self.PaginaProx.SetToolTip(wx.ToolTip("Próxima página"))
        self.PaginaProx.Bind(wx.EVT_BUTTON, self.AvancaPagina)
        self.PaginaPrev.Bind(wx.EVT_BUTTON, self.RetrocedePagina)        
        self.PaginaLabel = wx.StaticText(self, label="Pg. 1", pos=((widthTela/3)*2+240, heightTela-144))
        self.PaginaPrev.Disable()
        self.PaginaProx.Disable()
        self.PaginaLabel.Disable()
        
        # Tool Tips
        wx.ToolTip.SetDelay(100)
        wx.ToolTip.SetReshow(100)
        self.Mais.SetToolTip(wx.ToolTip("Mais acordes"))
        self.Menos.SetToolTip(wx.ToolTip("Menos acordes"))
        self.EscutarAcorde.SetToolTip(wx.ToolTip("Escutar acordes"))
        self.Aleatorio.SetToolTip(wx.ToolTip("Escolha aleatória"))
        self.MultiModeloBotao.SetToolTip(wx.ToolTip("Modelo VS Modelo"))
        self.MonoModeloBotao.SetToolTip(wx.ToolTip("Modelo único"))
        self.SalvarTXT.SetToolTip(wx.ToolTip("Cifra"))
        self.SalvarXML.SetToolTip(wx.ToolTip("Partitura MusicXML"))
        self.Novo.SetToolTip(wx.ToolTip("Começar do zero"))
        self.Sair.SetToolTip(wx.ToolTip("Fechar programa"))
        self.BotaoAjuda.SetToolTip(wx.ToolTip("Ajuda"))

        self.MultiModeloBotao.Bind(wx.EVT_BUTTON, self.MultiModelo)
        self.MonoModeloBotao.Bind(wx.EVT_BUTTON, self.MultiModelo)
        
        # Bind de Botões
                
        self.ProbCheck = wx.CheckBox(self, pos=((widthTela/3)*2+30, heightTela-40))
        self.ProbCheckLabel = wx.StaticText(self, label="Mostrar probabilidades", pos=((widthTela/3)*2+50, heightTela-40))
        Ft13 = wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.NORMAL)         
        self.ProbCheckLabel.SetFont(Ft13)        
        self.ProbCheckLabel.Bind(wx.EVT_LEFT_DOWN, self.onProbCheck)
        self.ProbCheck.Bind(wx.EVT_CHECKBOX, self.onProbCheck)
        self.Mais.Bind(wx.EVT_BUTTON, lambda event: self.MudaMatriz(event,+1))
        self.Menos.Bind(wx.EVT_BUTTON, lambda event: self.MudaMatriz(event,+-1))
        self.EscutarAcorde.Bind(wx.EVT_BUTTON, lambda event: self.TrocarCursor(event,False)) 
        self.Aleatorio.Bind(wx.EVT_BUTTON, self.EscolhaAleatoria)
        self.EstadoMatriz = 4        
        self.SalvarBot.Bind(wx.EVT_ENTER_WINDOW, self.onMouseOverSave)        
        self.SalvarTXT.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeaveSave)
        self.SalvarXML.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeaveSave)
        self.SalvarTXT.Bind(wx.EVT_BUTTON, self.SalvaTXT)
        self.SalvarXML.Bind(wx.EVT_BUTTON, self.SalvaXML)
        self.SalvarTXT.Hide()
        self.SalvarXML.Hide()
        self.Sair.Bind(wx.EVT_BUTTON, self.FecharApp)
        self.Novo.Bind(wx.EVT_BUTTON, self.NovaMusica)
        self.BotaoAjuda.Bind(wx.EVT_BUTTON, self.MostrarAjuda)
        
        self.Bind(EVT_MODELO, self.OnModelo) # término da thread que roda o modelo
        
        # Funções para DragAndDrop   (drag and drop não existe mais...)     
        self.AcordeSelecionado = None        
        self.Escutar = False
        self.ManterCor = False
        self.LastColormap = None        
        self.TrocarModelo = False        
        
        # Labels individuais para acordes
        FonteAcordes = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL)         
        for i in range(MAX_ACORDES):
            ac = wx.StaticText(self, label="")
            ac.SetFont(FonteAcordes)
            ac.ac = True
            ac.idx = i            
            ac.acorde = None
            ac.acordeMIDI = None
            ac.SetPosition( (0, 0) )
            ac.origem = ( (0, 0) )
            ac.SetForegroundColour( (0, 0, 168) )
            ac.Bind(wx.EVT_ENTER_WINDOW, self.AcordeMouseOver)
            ac.Bind(wx.EVT_LEAVE_WINDOW, self.AcordeMouseLeave)                        
            ac.Bind(wx.EVT_LEFT_DOWN, lambda event: self.PegarAcordeOuTocar(event) )
            #ac.Bind(wx.EVT_LEFT_DCLICK, self.MudarAcorde)
            ac.Bind(wx.EVT_RIGHT_DOWN, lambda event: self.TrocarCursor(event,True))   
            
        # Imagens para acordes
        
        #divide espaçamento na tela disponível
        heightDisponivel = heightTela-180
        espacoY = (int) (heightDisponivel/5)   #  16 acordes                
        self.escala = 4.0        
        
        #considerar também a dimensão horizontal        
        offset_x = (widthTela/3) *2  + 30   # 2/3 da tela + 30px
        widthDisponivel = (widthTela - offset_x - 30) 
        espacoX = int(widthDisponivel/4)
        
        while (330/self.escala) < (espacoY) and (204/self.escala) < (espacoX-30):
            self.escala -= 0.1 
        #print(self.escala)
        
        # acordes na partitura
        for i in range(MAX_ACORDES):
            acorde = "C7M"
            acorde = acorde.replace("/", "_") # acordes2xml.py --> troca caráter inválido
            img = os.path.abspath(os.path.dirname(sys.argv[0])) + "\\acordes\\" + acorde
            bmp = self.ScaleBitmap(img,204/self.escala, 330/self.escala)            
            img_ac = wx.BitmapButton(self, id=wx.ID_ANY, size=(204/self.escala,330/self.escala), pos=(1060, 300), style = wx.BORDER_NONE )
            img_ac.ac = False  # não é acorde
            img_ac.img = True  # é imagem
            img_ac.idx = i            
            img_ac.pos = 0 # primeira posição 
            img_ac.acorde = None
            img_ac.acordeMIDI = acorde # para posições alternativas
            img_ac.SetPosition( (10000, 10000) )
            img_ac.SetBackgroundColour((255,255,255))   # cinza para canal alfa
            img_ac.Bind(wx.EVT_RIGHT_DOWN, lambda event: self.TrocarCursor(event,True))   
            img_ac.Bind(wx.EVT_LEFT_DOWN, lambda event: self.RotarAcordeOuTocar(event) )

        # Pautas
        img = os.path.abspath(os.path.dirname(sys.argv[0])) + "\\acordes\\" + "linha"                        
        offsetX = (widthTela/3) *2  + 30   # 2/3 da tela + 30px
       
        #divide espaçamento na tela disponível
        heightDisponivel = heightTela-180
        espacoY = (int) (heightDisponivel/4)   #  16 acordes                        
        
        bmp = self.ScaleBitmap(img,1151/self.escala,330/self.escala)        
                
        self.pauta1 = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp,size=(1151/self.escala,330/self.escala), pos=(offsetX, 50), style = wx.BORDER_NONE)
        self.pauta1.SetBackgroundColour((255,255,255))   # cinza para canal alfa        
        #self.pauta1.Bind(wx.EVT_RIGHT_DOWN, lambda event: self.TrocarCursor(event,True))   
        self.pauta2 = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp,size=(1151/self.escala,330/self.escala), pos=(offsetX, 50+espacoY*1), style = wx.BORDER_NONE )
        self.pauta2.SetBackgroundColour((255,255,255))   # cinza para canal alfa        
        self.pauta3 = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp,size=(1151/self.escala,330/self.escala), pos=(offsetX, 50+espacoY*2), style = wx.BORDER_NONE )
        self.pauta3.SetBackgroundColour((255,255,255))   # cinza para canal alfa        
        self.pauta4 = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmp,size=(1151/self.escala,330/self.escala), pos=(offsetX, 50+espacoY*3), style = wx.BORDER_NONE )
        self.pauta4.SetBackgroundColour((255,255,255))   # cinza para canal alfa        
        self.pauta1.Show()
        self.pauta2.Hide()
        self.pauta3.Hide()
        self.pauta4.Hide()
        
        self.LabelProgressao.Hide()
        self.NumAcordes = 1        
        self.NumAcordesPrev = 1
        self.SaveDir = self.model_dir + self.modelos[self.modelo.GetSelection()]
        self.ajudaInicial = True
        
        self.txt1.SetBackgroundColour((255,255,255))        
        
        self.modelo.Bind(wx.EVT_COMBOBOX, self.OnCombo)
        self.nome_modelo = wx.StaticText(self, label=self.modelos[self.modelo.GetSelection()], pos = (135,10) )
        self.nome_modelo.Hide()        
        
        self.nome_modelo1 = wx.StaticText(self, label=self.modelos[self.modelo.GetSelection()], pos = (135,10) )
        self.nome_modelo1.Hide()        
        
        self.nome_modelo2 = wx.StaticText(self, label=self.modelos[self.modelo.GetSelection()], pos = (605,10) )
        self.nome_modelo2.Hide()
        
        self.AvisoEscutar = False
        self.MultiModelo = 0
        
        # Trocar cursor em todos focos
        for obj in self.GetChildren():            
            obj.Bind(wx.EVT_RIGHT_DOWN, lambda event: self.TrocarCursor(event,True))
        self.Bind(wx.EVT_RIGHT_DOWN, lambda event: self.TrocarCursor(event,True))                
    
        # Instrumento padrão para escuta de acordes
        self.InstrumentoMIDI = 25  # violão
        
        # Inicia thread com rede neural
        pub.subscribe(self.CriaAlternativas, "listener")   # comunicação entre threads         
        worker = ModeloThread(self, 1, 0, self.SaveDir, self.Prime)
        worker.start()        
        
# -------------------------------------------------------------------------------- #
#ENTRADA

def main():            
    app = wx.App(False)
    FRAMESTYLE = wx.SYSTEM_MENU | wx.CAPTION | wx.CLIP_CHILDREN
    global frame1
    frame1 = wx.Frame(None, -1, "" + "harmonIA", style = FRAMESTYLE)    
    panel1 = Panel1(frame1, -1)
    panel1.SetDoubleBuffered(True)
    frame1.SetTitle('harmonIA v1.0')     
    frame1.ShowFullScreen(True)
    app.MainLoop()    
    
# -------------------------------------------------------------------------------- #    

if __name__ == '__main__':    
    main()