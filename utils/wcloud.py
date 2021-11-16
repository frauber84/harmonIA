# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 20:47:57 2018

@author: frauber
"""

# Libraries
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import sys

# Create a list of word

f=open(sys.argv[1], 'r', encoding='utf-8')

text=f.read()
f.close()

#stopwords
text=text.replace("_START_", " ")
text=text.replace("_END_", " ")

# atenção! este wordcloud foi modificado, as modificações da biblioteca original estão em wordcloud_modificado.py 
wordcloud = WordCloud(width=1000, height=800, margin=0, max_words=100).generate(text)

# Display the generated image:
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.margins(x=0, y=0)
#plt.show()
plt.savefig('cloud.png', dpi=200)