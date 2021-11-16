import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow.contrib import rnn
from tensorflow.contrib import legacy_seq2seq
import imageio
import glob

import random
import numpy as np
import os

from beam import BeamSearch


# tirar isso!
def onClick(event):
    (x,y)   = (event.xdata, event.ydata)
    print(x)
    print(y)
    

class Model():
    def __init__(self, args, infer=False):        
        self.args = args
        if infer:
            args.batch_size = 1
            args.seq_length = 1

        if args.model == 'rnn':
            cell_fn = rnn.BasicRNNCell
        elif args.model == 'gru':
            cell_fn = rnn.GRUCell
        elif args.model == 'lstm':
            cell_fn = rnn.BasicLSTMCell
        else:
            raise Exception("model type not supported: {}".format(args.model))

        cells = []
        for _ in range(args.num_layers):
            cell = cell_fn(args.rnn_size)
            cells.append(cell)

        self.cell = cell = rnn.MultiRNNCell(cells)

        self.input_data = tf.placeholder(tf.int32, [args.batch_size, args.seq_length])
        self.targets = tf.placeholder(tf.int32, [args.batch_size, args.seq_length])
        self.initial_state = cell.zero_state(args.batch_size, tf.float32)
        self.batch_pointer = tf.Variable(0, name="batch_pointer", trainable=False, dtype=tf.int32)
        self.inc_batch_pointer_op = tf.assign(self.batch_pointer, self.batch_pointer + 1)
        self.epoch_pointer = tf.Variable(0, name="epoch_pointer", trainable=False)
        self.batch_time = tf.Variable(0.0, name="batch_time", trainable=False)
        tf.summary.scalar("time_batch", self.batch_time)
        

        def variable_summaries(var):
            """Attach a lot of summaries to a Tensor (for TensorBoard visualization)."""
            with tf.name_scope('summaries'):
                mean = tf.reduce_mean(var)
                tf.summary.scalar('mean', mean)
                tf.summary.scalar('max', tf.reduce_max(var))
                tf.summary.scalar('min', tf.reduce_min(var))
                tf.summary.histogram('histogram', var)

        with tf.variable_scope('rnnlm'):
            softmax_w = tf.get_variable("softmax_w", [args.rnn_size, args.vocab_size])
            variable_summaries(softmax_w)
            softmax_b = tf.get_variable("softmax_b", [args.vocab_size])
            variable_summaries(softmax_b)
            with tf.device("/cpu:0"):                
                #atencao para essa parte
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
        tf.summary.scalar("cost", self.cost)
        
        self.final_state = last_state
        self.lr = tf.Variable(0.0, trainable=False)
        tvars = tf.trainable_variables()
        grads, _ = tf.clip_by_global_norm(tf.gradients(self.cost, tvars),
                args.grad_clip)
        optimizer = tf.train.AdamOptimizer(self.lr)
        self.train_op = optimizer.apply_gradients(zip(grads, tvars))

    def sample(self, sess, words, vocab, num=200, prime='first all', sampling_type=1, pick=0, width=4, quiet=False, criatividade=70, desenha=0, out='cifras.txt'):
        def weighted_pick(weights):
            t = np.cumsum(weights)
            #s = np.sum(weights)
            s = t[-1]
            
            # Explicação para esse correção em Ss--> https://github.com/hunkim/word-rnn-tensorflow/pull/67/commits/48b27bc9b46399e630fd66f38d905dca25f12eeb
            
            r = np.random.rand(1)
            
            print("número aleatório %f" % r)
            #print("t = %f (soma cumulativa)" % t )
            
            '''
            Now I got it. t = np.cumsum(weights) makes words 
            with higher probability to have bigger interval just 
            before itself and that makes the seemingly random choice to be 
            weighted pick. Makes sense.
            '''        
            return(int(np.searchsorted(t, r*s)))

        def beam_search_predict(sample, state):
            """Returns the updated probability distribution (`probs`) and
            `state` for a given `sample`. `sample` should be a sequence of
            vocabulary labels, with the last word to be tested against the RNN.
            """

            x = np.zeros((1, 1))
            x[0, 0] = sample[-1]
            feed = {self.input_data: x, self.initial_state: state}
            [probs, final_state] = sess.run([self.probs, self.final_state],
                                            feed)
            return probs, final_state

        def beam_search_pick(prime, width):
            """Returns the beam search pick."""
            if not len(prime) or prime == ' ':
                prime = random.choice(list(vocab.keys()))
            prime_labels = [vocab.get(word, 0) for word in prime.split()]
            bs = BeamSearch(beam_search_predict,
                            sess.run(self.cell.zero_state(1, tf.float32)),
                            prime_labels)
            samples, scores = bs.search(None, None, k=width, maxsample=num)
            return samples[np.argmin(scores)]

        ret = ''
        if pick == 1:
            state = sess.run(self.cell.zero_state(1, tf.float32))
            if not len(prime) or prime == ' ':
                prime  = random.choice(list(vocab.keys()))
                '''
                mudei isso aqui:
                caso usuário não especifique acorde inicial,
                usar máxima probabilidade , que nesse caso é o acorde
                de maior ocorrência com np.argmax[p],  e p=probs[0]
                
                word = "######## # # ###"
                x = np.zeros((1, 1))
                x[0, 0] = vocab.get(word, 0)
                feed = {self.input_data: x, self.initial_state:state}
                [probs, state] = sess.run([self.probs, self.final_state], feed)
                p = probs[0]
                prime = words[np.argmax(p)]                
                #
                não funcionou isso aqui ainda.. usar alguma opção mais simples...
                contar palavras e escolher maiores ocorrencias (randomico entre os 5+ ? )
                
                
                '''
                
                
            if not quiet:
                print(prime)
            for word in prime.split()[:-1]:
                x = np.zeros((1, 1))
                x[0, 0] = vocab.get(word,0)
                feed = {self.input_data: x, self.initial_state:state}
                [state] = sess.run([self.final_state], feed)

            #formata acordes iniciais  (antes, ret=prime ))            
            contexto = prime.split()   
            n2 = 0
            for acorde in contexto:
                if ('C' in acorde) or ('D' in acorde) or ('E' in acorde) or ('F' in acorde) or ('G' in acorde) or ('A' in acorde) or ('B' in acorde):
                    n2 += 1
                    ret += " " + acorde + "  "                    
                    if len(acorde) < 12:
                        pad = ""
                        for i in range(0,12-len(acorde)):
                            pad += " "
                        pad += " | "
                        ret+=pad
                        
                        if (n2 % 4 == 0):
                            ret += '\n'                             
            
            word = prime.split()[-1]
            
            z = 0                       
            acordes= prime + "  "
            cifra = prime + "  "
                        
            for n in range(num-n2):                
                z += 1
                n2 += 1
                x = np.zeros((1, 1))
                x[0, 0] = vocab.get(word, 0)
                feed = {self.input_data: x, self.initial_state:state}
                [probs, state] = sess.run([self.probs, self.final_state], feed)
                p = probs[0]
                
                idx = 0 # indice para contagem da matriz
                print(cifra) # Soma dos acordes
                
                #matriz de duas dimensões, 2 itens para len(words) listas 
                MatrizProb = [[0 for x in range(2)] for y in range(len(words))]  
                for prob in probs[0]:
                    #print(words[idx] + " - probabilidade: %.2f \n" % (prob*100) )
                    MatrizProb[idx][0] = idx
                    MatrizProb[idx][1] = prob*100
                    idx += 1
                
                # ordena da maior para menor probabilidade
                MatrizProb =sorted(MatrizProb, key=lambda x:x[1],reverse=True)
                                
                for i in range(50):
                    if MatrizProb[i][1] > 1:
                        print(words[MatrizProb[i][0]] + " - probabilidade: %.2f" % (MatrizProb[i][1]) )                    
                
                #Desenha rede
                if desenha==1: 
                    #pega 4 últimas cifras
                    palavras = sum(1 for palavra in cifra.split() if not " " in palavra) # numero de palavras
                    if palavras > 3:
                        acordes = cifra.split()[-3] + "  " + cifra.split()[-2] + "  " + cifra.split()[-1]

                    ''' testar posicoinamento de texto
                    x0, xmax = plt.xlim()
                    y0, ymax = plt.ylim()
                    data_width = xmax - x0
                    data_height = ymax - y0
                    plt.text(x0 + data_width * 1.5, y0 + data_height * 0.5, 'Some text')
                    '''
                    
                    fig = plt.figure()
                    fig.set_facecolor("#FEFEFE")
                    df = pd.DataFrame({ 'origem':[ acordes, acordes, acordes, acordes, acordes, acordes ], 'destino':[ words[MatrizProb[0][0]], words[MatrizProb[1][0]], words[MatrizProb[2][0]], words[MatrizProb[3][0]], words[MatrizProb[4][0]], words[MatrizProb[5][0]] ] , 'prob':[ MatrizProb[0][1], MatrizProb[1][1],MatrizProb[2][1],MatrizProb[3][1],MatrizProb[4][1],MatrizProb[5][1] ] })
                    G=nx.from_pandas_dataframe(df, 'origem', 'destino')
                    nx.draw(G, with_labels=True, node_size=df['prob']*100, node_color="skyblue", node_shape = "o", aplha=0.5,linewidth=40, edge_color=df['prob'], width=6.0, edge_cmap=plt.cm.Blues)
                    plt.axis('off')
                    plt.text(0, 1.6, cifra, fontsize=12, color='red', horizontalalignment='center',verticalalignment='center')
                    # To Do: SALVAR COM O NOME ADEQUADO (removendo path então)
                    plt.savefig('png/img{}.png'.format(n), dpi=120, bbox_inches='tight')
                    
                    fig.canvas.mpl_connect('button_press_event', onClick)

                    #plt.show()
                    plt.close()
                                
                
                #print (criatividade)
                
                
                # tipo de amostragem 
                if sampling_type == 0:
                    sample = np.argmax(p)                    
                elif sampling_type == 2:
                    if word == '\n':
                        sample = weighted_pick(p)
                    else:
                        sample = np.argmax(p)
                else: # sampling_type == 1 default:
                    sample = weighted_pick(p)

                pred = words[sample]                
                                
                #pred = words[MatrizProb[random.randint(0,6)][0]]
                
                # acha outra previsao para fim   
                while pred == "|FIM|":     
                    sample = weighted_pick(p)
                    pred = words[sample]
                    
                ret += ' ' + pred              
                
                #teste: randomizando método (40% 1, 60% determinístico)
                r = random.randint(0,100)
                if r < criatividade:
                    sampling_type = 1
                else:
                    sampling_type = 0
                    
                if criatividade == 0:
                    sampling_type = 0
                elif criatividade == 100:
                    sampling_type = 1
                                
                # formatação
                ret += '  '
                if len(pred) < 12:
                  for i in range(0,12-len(pred)):                      
                      ret += " "      # pad                 
                  ret += " | "        # separador
                   
                word = pred
                acordes = word + "  " # último acorde da rede
                cifra += word +  "  " # cifra total da rede
                palavras = sum(1 for palavra in cifra.split() if not " " in palavra) # numero de palavras
                if (palavras % 8 == 0) and not palavras == 0:
                    cifra += '\n'
                
                if palavras > 3:
                    acordes = cifra.split()[-3]
                
                #separa/formata cifras
                if (n2 % 4 == 0):                    
                    ret+= '\n'                    
                    
                # desenha gráfico na´última iteração
                if num-n2 == 0 and desenha==1:
                    #pega 4 últimas cifras
                    palavras = sum(1 for palavra in cifra.split() if not " " in palavra) # numero de palavras
                    if palavras > 3:
                        acordes = cifra.split()[-3] + "  " + cifra.split()[-2] + "  " + cifra.split()[-1]
                        
                    fig = plt.figure()
                    fig.set_facecolor("#FEFEFE")
                    df = pd.DataFrame({ 'origem':[acordes], 'destino':[acordes] , 'prob':[0] })
                    G=nx.from_pandas_dataframe(df, 'origem', 'destino')
                    nx.draw(G, with_labels=True, node_size=1500, node_color="skyblue", node_shape = "s", aplha=0.5,linewidth=40,  edge_color=df['prob'], width=6.0, edge_cmap=plt.cm.Blues)
                    plt.axis('off')
                    plt.text(0, 0, "\n\n\n\n\n\n\n\n" + cifra, fontsize=12, color='red', horizontalalignment='center',verticalalignment='center')
                    plt.savefig('png/img{}.png'.format(n+1), dpi=120, bbox_inches='tight')
                    plt.close()
                                        
                    #escreve GIF animado
                    image_path = "png/"
                    movie_filename = 'png/cifras.gif'
                    fps = 0.5             
                    filenames = glob.glob(image_path + 'img*.png')
                    filenames_sort_indices = np.argsort([int(os.path.basename(filename).split('.')[0][3:]) for filename in filenames])
                    filenames = [filenames[i] for i in filenames_sort_indices]
                    with imageio.get_writer(movie_filename, mode='I', fps=fps) as writer:
                        for filename in filenames:
                            image = imageio.imread(filename)
                            writer.append_data(image)                    
                    
        elif pick == 2:
            pred = beam_search_pick(prime, width)
            for i, label in enumerate(pred):
                ret += ' ' + words[label] if i > 0 else words[label]
        return ret        