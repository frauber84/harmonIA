import os
from pathlib import Path
import subprocess
import time

path = r'C:\fernando\2018\python\CIFRACLUB\treinar'    # path
os.chdir(path)

for file_path in Path(path).glob('**/*.processado'):
    arquivo = str(file_path)
    # normaliza e expande
    p = subprocess.Popen(r'python expande_dataset.py ' + arquivo)
    p.wait()
    p = subprocess.Popen(r'python normaliza_dataset.py ' + arquivo)
    p.wait()

   