#!/usr/bin/env python

# Name: wordsworth
# Description: Frequency analysis tool
# Licence: GPLv3
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

#
# modificado por Fernando Rauber para utilização em Nutella!
#

import collections
import re

class wordsworth:
    args = 0
    ignore_list = []
    out = 0
    words = []
    previous_word = ''
    previous_pair = ''
    previous_triple = ''
    previous_quad = ''
    max_n_word = 8
    n_words = []
    prev_n_words = []
    counters = []

    word_stats = {
                  'total_chars': 0,
                  'musicas': 0,
                  'total_words': 0,
                  'max_length': 0,
                  'min_length': 999,
                  'mean_length': -1,
                  'longest_word': '',
                  'shortest_word': '',
                  'char_counts': {
                                  'a': 0.0, 'b': 0.0, 'c': 0.0, 'd': 0.0, 'e': 0.0, 'f': 0.0,
                                  'g': 0.0, 'h': 0.0, 'i': 0.0, 'j': 0.0, 'k': 0.0, 'l': 0.0,
                                  'm': 0.0, 'n': 0.0, 'o': 0.0, 'p': 0.0, 'q': 0.0, 'r': 0.0,
                                  's': 0.0, 't': 0.0, 'u': 0.0, 'v': 0.0, 'w': 0.0, 'x': 0.0,
                                  'y': 0.0, 'z': 0.0
                                 },
                  'char_percentages': {
                                       'a': 0.0, 'b': 0.0, 'c': 0.0, 'd': 0.0, 'e': 0.0, 'f': 0.0,
                                       'g': 0.0, 'h': 0.0, 'i': 0.0, 'j': 0.0, 'k': 0.0, 'l': 0.0,
                                       'm': 0.0, 'n': 0.0, 'o': 0.0, 'p': 0.0, 'q': 0.0, 'r': 0.0,
                                       's': 0.0, 't': 0.0, 'u': 0.0, 'v': 0.0, 'w': 0.0, 'x': 0.0,
                                       'y': 0.0, 'z': 0.0
                                      },
                  'lexical_density': -1
                  }


    def __init__(self, commandline_args):
        args = commandline_args
        self.ignore_list = str(args.ignore_list).split(",")        

    def print_n_word_frequencies(self, n_word_counter):
        total_entries = sum(n_word_counter.values())
        unique_entries = len(n_word_counter)
        if total_entries > 0:
            m = n_word_counter.most_common(min(unique_entries, args.top_n))
            n = len(m[0][0].split(' '))

            #print('\nProgressão(' + str(n) + ')')
 
            idx = 0
            info = open( "info", "a", encoding="utf8")
            for i in range(0, min(unique_entries, args.top_n)):
                n_word = m[i][0]
                count = m[i][1]
                perc = 100.0 * (count / float(total_entries))
                
                result = str(n) + '-' + (str(idx + 1) + ':' + n_word   + ':'  + str(count).split('.')[0]  + ':'  + str(perc)[:4])        
                if not 'X' in result and n==1 or n==4 or n==8:  # somente 1-4-8
                    #print(result_perc)
                    info.write('\n' + str(result) )
                else:
                    idx -= 1
                idx += 1
            
            info.close()


    def print_results(self):        
        
        info = open( "info", "a", encoding="utf8")
        
        '''
        print('Maior Acorde=' + str(self.word_stats['longest_word']) + 
            ' (' + str(self.word_stats['max_length']) + ')')
        print('Menor Acorde=' + str(self.word_stats['shortest_word'])  +
            ' ('  + str(self.word_stats['min_length'])  + ')')
        '''
        
        info.write('\ntotal_acordes:'  + str(self.word_stats['total_words']).split('.')[0] )
        info.write('\ntotal_musicas:'  + str(self.word_stats['musicas']) )
        info.write('\ndiversidade_harmonica:'  + str(self.word_stats['lexical_density'])[:5])        
        info.close()
        for i in range(self.max_n_word):
            self.print_n_word_frequencies(self.counters[i])
            
        

        

    def init_word_counters(self):
        self.max_n_word = args.max_n_word
        self.n_words = ['' for i in range(self.max_n_word)]
        self.prev_n_words = ['' for i in range(self.max_n_word)]
        self.counters = [collections.Counter() for i in range(self.max_n_word)]

    def read_file(self):
        print("Arquivo=" + args.inputfile)
        if args.allow_digits:
            #self.words = re.findall(r"['\-\w]+", open(args.inputfile,encoding="ISO-8859-1").read().lower())
            self.words = re.findall(r"['\-\S]+", open(args.inputfile,encoding="utf-8").read() )
        else:
            #self.words = re.findall(r"['\-A-Za-z]+", open(args.inputfile,encoding="ISO-8859-1").read().lower())
            self.words = re.findall(r"['\-A-Za-z]+", open(args.inputfile,encoding="utf-8").read() )
            


    def compute_stats(self):
        
        for word in self.words:        
            if word in self.ignore_list:
                continue
        
            '''  word = word.strip(r"&^%$#@!")      '''

            # Allow hyphenated words, but not hyphens as words on their own.
            if word == '-':
                continue

            length = len(word)

            # Record longest word length
            if length > self.word_stats['max_length']:
                self.word_stats['max_length'] = length
                self.word_stats['longest_word'] = word

            # Record shortest word length
            if length < self.word_stats['min_length']:
                self.word_stats['min_length'] = length
                self.word_stats['shortest_word'] = word

            # Keep track of the total number of words and chars read.
            self.word_stats['total_chars'] += length
            self.word_stats['total_words'] += 1.0

            # Tally words.
            for i in range(1, self.max_n_word):
                if self.prev_n_words[i - 1] != '':
                    self.n_words[i] = self.prev_n_words[i - 1] + ' ' + word
                    self.counters[i][self.n_words[i]] += 1

            self.n_words[0] = word
            self.counters[0][word] += 1

            for i in range(0, self.max_n_word):
                self.prev_n_words[i] = self.n_words[i]

        # Calculate the mean word length
        #self.word_stats['mean_length'] = self.word_stats['total_chars'] / self.word_stats['total_words']

        # Calculate the lexical density of the text.
        total_unique_words = len(self.counters[0])
        total_words = sum(self.counters[0].values())
        self.word_stats['lexical_density'] = 100.0 * total_unique_words / float(total_words)
        
        # número de músicas (linhas)
        lines = open(args.inputfile,encoding="utf-8").readlines() 
        l = 0
        for line in lines:
            l += 1
        self.word_stats['musicas'] = l


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Perform letter, word and n-tuple frequency analysis on text files.')
    parser.add_argument('--filename', '-f', dest='inputfile', required=True, help='Text file to parse.')
    parser.add_argument('--ntuple', '-n', dest='max_n_word', required=False, default=8, type=int, help='The maximum length n-tuple of words. Default is 4.')
    parser.add_argument('--top', '-t', dest='top_n', required=False, default=300, type=int, help='List the top t most frequent n-words. Default is 20.')
    parser.add_argument('--allow-digits', '-d', dest='allow_digits', default=True, required=False, help='Allow digits to be parsed (true/false). Default is false.')
    parser.add_argument('--ignore', '-i', dest='ignore_list', required=False, help='Comma-delimted list of things to ignore')

    args = parser.parse_args()
    w = wordsworth(args)
    w.init_word_counters()
    w.read_file()
    w.compute_stats()
    w.print_results()