#!/usr/bin/env python3
"""Compara los instrumentos nombrados en el corpus contra el registro.

    python3 verificar_registro.py

Falla si una ficha afirma algo sobre un instrumento que no está ni como ficha
ni como exclusión documentada. Es el control que encontró la Res. 710/2024,
la Ley 6339 y el Sistema Preventivo.
"""
import json, re, sys
from pathlib import Path
R = Path(__file__).resolve().parent
d = json.load(open(R/'data/fichas.json', encoding='utf-8'))
reg = json.load(open(R/'data/registro_instrumentos.json', encoding='utf-8'))

PAT = [r'Ley(?:es)?\s*N?[°º]?\s*\d{1,2}\.?\d{3}',
       r'(?:DNU|Decretos?)\s*N?[°º]?\s*\d{1,4}/\d{2,4}',
       r'Res(?:oluci[óo]n(?:es)?)?\.?\s*(?:MS\s*)?N?[°º]?\s*\d{1,4}[-/][A-Za-z]*[-/]?\d{2,4}',
       r'Disposici[óo]n(?:es)?\s*(?:RENAPER\s*)?\d{1,4}/\d{2,4}',
       r'RG\s*(?:AFIP\s*)?\d{3,4}/\d{4}']

conocidos = ' | '.join([f['instrumento'] for f in reg['fichas']]
                       + [c['instrumento'] for c in reg['citados_sin_ficha']]
                       + reg['exclusiones_por_categoria'])
faltan = []
for f in d:
    texto = (f.get('que_hace_es') or '') + ' ' + (f.get('contexto_es') or '')
    for pat in PAT:
        for m in re.findall(pat, texto):
            num = re.search(r'[\d\.]+(?:/\d+)?', m).group(0)
            if num not in conocidos and num not in f['titulo_es']:
                faltan.append((f['slug'], m.strip()))

if faltan:
    print(f"{len(set(faltan))} instrumento(s) sin categoría en el registro:\n")
    for slug, ins in sorted(set(faltan)):
        print(f"  {ins:26} afirmado en {slug}")
    print("\nCada uno necesita: ficha propia, ítem de índice, o exclusión con motivo y fecha.")
    sys.exit(1)
print(f"sin observaciones · {len(reg['fichas'])} fichas registradas")
