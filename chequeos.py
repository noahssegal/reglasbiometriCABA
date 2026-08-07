#!/usr/bin/env python3
"""
Chequeos mecanicos del corpus. Corre en segundos, no reemplaza la lectura.

    python3 chequeos.py

Verifica lo que no depende de criterio: numeracion de notas, paridad ES/EN,
fechas imposibles, enlaces rotos de la cronologia, y coherencia entre el
instrumento del titulo y la primera fuente citada.
"""
import json, re, datetime, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
P = r'\[(\d+)\]'
HOY = datetime.date.today()

def main():
    F = json.loads((RAIZ/"data/fichas.json").read_text(encoding="utf-8"))
    C = json.loads((RAIZ/"data/cronologia.json").read_text(encoding="utf-8"))
    fallos = []

    for f in F:
        s = f["slug"]
        cuerpo = f["que_hace_es"] + f["contexto_es"]
        nums, disp = set(re.findall(P, cuerpo)), set(re.findall(P, f["fuentes"]))
        if nums - disp:
            fallos.append(f"nota sin fuente · {s} · cita {sorted(nums-disp)}")
        if disp - nums:
            fallos.append(f"fuente no citada · {s} · sobra {sorted(disp-nums)}")
        for a, b, lbl in (("que_hace_es","que_hace_en","qué hace"),
                          ("contexto_es","contexto_en","contexto")):
            if re.findall(P, f[a]) != re.findall(P, f[b]):
                fallos.append(f"ES/EN descalzado · {s} · {lbl}")
        for m in re.finditer(r'le[íi]d[oa]s? (?:completos? )?(\d{2})/(\d{2})/(\d{4})', f["fuentes"]):
            d = datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
            if d > HOY:
                fallos.append(f"fecha futura · {s} · {m.group(0)}")
        # el instrumento del titulo deberia aparecer en la primera fuente
        partes = re.split(P, f["fuentes"])
        f1 = partes[2] if len(partes) > 2 else ""
        clave = re.search(r'(?<!Expte\. )(\d[\d\.]{2,})(?:/(\d{2,4}))?', f["titulo_es"]) if "Expte." not in f["titulo_es"] else None
        if clave:
            num = clave.group(1).replace(".", "")
            plano = re.sub(r"[.\-/]", "", f1)
            if num not in plano:
                fallos.append(f"revisar · {s} · título cita {clave.group(1)}, fuente [1] no lo menciona")

    slugs = {f["slug"] for f in F}
    for fila in C:
        for lado in ("izq","der"):
            for it in fila.get(lado, []):
                if it["slug"] not in slugs:
                    fallos.append(f"enlace roto · cronología {fila['anio']} → {it['slug']}")

    if fallos:
        print(f"{len(fallos)} punto(s) a revisar:\n")
        for x in fallos: print("  " + x)
        sys.exit(1)
    print(f"sin observaciones · {len(F)} fichas")

if __name__ == "__main__":
    main()
