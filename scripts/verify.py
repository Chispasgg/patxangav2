#!/usr/bin/env python3
import json, os

f = open('config/config.json')
d = json.load(f)
f.close()
imgs = d['items'][2]['images']
print('Total entradas JSON:', len(imgs))

non_numeric = [img['name'] for img in imgs if not img['name'].isdigit()]
print('Nombres no-numericos:', non_numeric)

for i in [0,1,2,3,4,5,86,87,88]:
    print(f'  images[{i}].name = {imgs[i]["name"]}')

fotos = sorted(os.listdir('fotos'), key=lambda x: x.lower())
print('\nArchivos en fotos/ (primeros 5):', fotos[:5])
print('Archivos en fotos/ (ultimos 5):', fotos[-5:])
print('Total archivos:', len(fotos))
