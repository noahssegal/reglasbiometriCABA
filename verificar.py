#!/usr/bin/env python3
"""
Tabla de verificacion, agrupada por documento fuente.

    python3 verificar.py

Agrupar por documento —y no por ficha— permite abrir cada fuente una sola vez
y cotejar de una todas las afirmaciones que dependen de ella.
Salida: verificacion/tabla.html
"""
import json, re, html
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SAL = RAIZ / "verificacion"

def esc(t): return html.escape(t, quote=False)

def frases(t):
    t = re.sub(r"(Res|Disp|art|arts|inc|Dto|Expte|Ley|N|n)\.", r"\1<PUNTO>", t)
    partes = re.split(r"(?<=[.:])\s+(?=[A-ZÁÉÍÓÚÑ«“])", t)
    return [p.replace("<PUNTO>", ".").strip() for p in partes if p.strip()]

def fuentes_map(s):
    d, act, buf = {}, None, []
    for tok in re.split(r"(\[\d+\])", s):
        m = re.fullmatch(r"\[(\d+)\]", tok)
        if m:
            if act: d[act] = "".join(buf).strip(" .")
            act, buf = m.group(1), []
        elif act:
            buf.append(tok)
    if act: d[act] = "".join(buf).strip(" .")
    return d

# afirmaciones ya cotejadas contra el texto fuente (07/08/2026)
COTEJADAS = [
    "Decreto 1766/2011 creó un servicio centralizado",
    "usuarios eran seis",
    "Decreto 243/2017 amplió",
    "Decreto 243/2017 registra que la unidad",
    "sistema fue creado y ampliado por decreto",
    "para ubicar a personas ya sujetas a una orden de captura judicial",
    "creó el Registro del Sistema de Identificación de Prófugos",
    "Lo que este acto crea por primera vez",
    "El acto no menciona el expediente judicial",
    "sumó condiciones: probar si el software",
    "declaró inconstitucional la implementación",
]

def ya_cotejada(t):
    return any(x.lower() in t.lower() for x in COTEJADAS)


# documentos que son el mismo aunque la ficha los nombre distinto
CANON = [
    (r"Res\.? 398/MJYSGC/19|Resoluci[óo]n 398", "Res. 398/MJYSGC/19 (BO CABA 5604, 2019)"),
    (r"Res\.? 351-MSEGC/24|Resoluci[óo]n 351-MSEGC/24", "Res. 351-MSEGC/24 y Anexo I (2024)"),
    (r"Anexo I: Gu[íi]a de Gesti[óo]n", "Res. 351-MSEGC/24 y Anexo I (2024)"),
    (r"CSJN", "CSJN «Torres Abad» (30/04/2026)"),
    (r"ODIA y otros|Sentencia de primera instancia", "Sentencia de primera instancia (07/09/2022)"),
    (r"C[áa]mara CATyRC", "Sentencia de Cámara (28/04/2023)"),
    (r"Resoluci[óo]n PIA|Resoluci[óo]n cautelar CAF|Amparo colectivo CAF", None),
    (r"Verificaci[óo]n del proyecto", "Verificación del proyecto (búsqueda con fecha)"),
    (r"Resoluci[óo]n 9/2025", "Res. PBA 9/2025 (texto oficial)"),
    (r"Ley 5688", "Ley 5688, Libro VII (consolidación 30/01/2026)"),
    (r"Decreto 1766/2011", "Decreto 1766/2011 (SIBIOS)"),
    (r"Decreto 243/2017", "Decreto 243/2017 (SIBIOS)"),
]

def canon(t):
    for pat, nombre in CANON:
        if re.search(pat, t):
            if nombre: return nombre
            break
    return re.split(r"—", t)[0].strip().rstrip(".,;:")[:70]

def main():
    fichas = json.loads((RAIZ / "data/fichas.json").read_text(encoding="utf-8"))
    SAL.mkdir(exist_ok=True)
    grupos = defaultdict(list)
    total = 0

    for f in fichas:
        fte = fuentes_map(f["fuentes"])
        for bloque, campo in (("Qué hace", "que_hace_es"), ("En contexto", "contexto_es")):
            for fr in frases(f[campo]):
                nums = re.findall(r"\[(\d+)\]", fr)
                limpio = re.sub(r"\[\d+\]", "", fr).strip()
                total += 1
                for n in (nums or ["?"]):
                    txt = fte.get(n, "⚠ FUENTE INEXISTENTE")
                    grupos[canon(txt)].append((f["titulo_es"], bloque, limpio, txt, ya_cotejada(limpio)))

    orden = sorted(grupos.items(), key=lambda kv: -len(kv[1]))

    p = ["""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<title>Tabla de verificación — Marco legal</title>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,sans-serif;
 background:#FAF9F6;color:#2C2C2A;margin:0;padding:34px 30px;font-size:14px;line-height:1.55}
h1{font-family:Charter,Georgia,serif;font-weight:400;font-size:22px;margin:0 0 6px}
.sub{color:#5F5E5A;font-size:13px;margin:0 0 30px;max-width:78ch}
h2{font-size:14px;font-weight:500;margin:30px 0 0;padding:9px 0 7px;
 border-top:1px solid #2C2C2A;display:flex;justify-content:space-between;align-items:baseline;gap:16px}
h2 .n{font-family:ui-monospace,Menlo,monospace;font-size:11px;color:#888780;font-weight:400;white-space:nowrap}
.det{font-family:ui-monospace,Menlo,monospace;font-size:10.5px;color:#888780;margin:0 0 8px;line-height:1.6}
table{border-collapse:collapse;width:100%}
td{border-bottom:0.5px solid #D3D1C7;padding:9px 10px 9px 0;vertical-align:top}
tr:hover{background:#F3F1EC}
.ficha{font-size:11px;color:#5F5E5A;width:150px}
.bloque{font-size:10px;color:#B4B2A9;text-transform:uppercase;letter-spacing:0.05em;width:72px}
.ok{width:74px;text-align:center;color:#B4B2A9;font-family:ui-monospace,Menlo,monospace;font-size:11px}
.hecha{color:#0F6E56}
@media print{body{padding:0;font-size:11px}tr,h2{break-inside:avoid}h2{break-after:avoid}}
</style></head><body>"""]
    p.append("<h1>Tabla de verificación</h1>")
    p.append(f'<p class="sub">Agrupada por documento fuente: cada fuente se abre una vez y se cotejan de una todas las '
             f'afirmaciones que dependen de ella. {total} afirmaciones sobre {len(orden)} documentos. '
             f'Statements marked “checked” were compared against the source text on 07/08/2026; '
             f'the rest have an empty box for the reviewer.</p>')
    for nombre, filas in orden:
        det = max((x[3] for x in filas), key=len)
        pend = sum(1 for x in filas if not x[4])
        p.append(f'<h2><span>{esc(nombre)}</span><span class="n">{pend} to check of {len(filas)}</span></h2>')
        p.append(f'<p class="det">{esc(det)}</p><table>')
        for tit, bl, af, _, hecha in filas:
            marca = '<span class="hecha">checked</span>' if hecha else '☐'
            p.append(f'<tr><td class="ficha">{esc(tit)}</td><td class="bloque">{esc(bl)}</td>'
                     f'<td>{esc(af)}</td><td class="ok">{marca}</td></tr>')
        p.append("</table>")
    p.append("</body></html>")
    (SAL / "tabla.html").write_text("".join(p), encoding="utf-8")
    print(f"listo — {total} afirmaciones · {len(orden)} documentos → verificacion/tabla.html")

if __name__ == "__main__":
    main()
