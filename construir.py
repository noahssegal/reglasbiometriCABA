#!/usr/bin/env python3
"""
Construye el sitio estatico.

    python3 construir.py

Entrada:  data/fichas.json, data/cronologia.json, data/encuadre.json, estilo.css
Salida:   dist/index.html (cronologia), dist/indice.html, dist/encuadre.html,
          docs/ficha-<slug>.html, docs/estilo.css

Editar el texto de una ficha = editar data/fichas.json y volver a correr.
Sin dependencias externas.
"""

import json, re, shutil, html
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DATA = RAIZ / "data"
DIST = RAIZ / "docs"

JURIS = {
    "nacional": ("Nacional", "National"),
    "caba": ("Ciudad de Buenos Aires", "Buenos Aires City"),
    "pba": ("Provincia de Buenos Aires", "Province of Buenos Aires"),
}
ORDEN_JURIS = ["caba", "nacional", "pba"]

ETIQ_JUR = {
    "nacional": ("nacional", "national"),
    "provincia": ("provincia", "province"),
    "tratado": ("tratado", "treaty"),
    "proyecto": ("proyecto", "bill"),
}

SITIO = ("Marco legal", "Legal framework")


def esc(t):
    return html.escape(t, quote=False)


def notas(t):
    return re.sub(r"\[(\d+)\]", r'<sup><a href="#fuentes">\1</a></sup>', esc(t))


def bi(es, en, tag="span"):
    return f'<{tag} class="es">{es}</{tag}><{tag} class="en">{en}</{tag}>'


def cabecera(titulo, activo, prof=0):
    base = ""
    def act(p):
        return ' aria-current="page"' if p == activo else ""
    return f"""<!DOCTYPE html>
<html lang="es" data-idioma="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(titulo)}</title>
<link rel="stylesheet" href="{base}estilo.css">
</head>
<body data-idioma="es">
<div class="envoltura">
<header class="sitio-cabecera">
  <a class="marca" href="{base}index.html">{bi(*SITIO)}</a>
  <nav class="nav">
    <a href="{base}index.html"{act('crono')}>{bi('Cronología','Chronology')}</a>
    <a href="{base}indice.html"{act('indice')}>{bi('Índice','Index')}</a>
    <a href="{base}derechos.html"{act('derechos')}>{bi('Qué se puede hacer','What you can do')}</a>
    <a href="{base}encuadre.html"{act('encuadre')}>{bi('Sobre este sitio','About')}</a>
    <button class="idioma" type="button" onclick="cambiarIdioma()">{bi('EN','ES')}</button>
  </nav>
</header>
"""


PIE = """<footer class="sitio-pie">
  <div class="nota">
    <span class="es">Cada afirmación cita un documento oficial y la fecha de acceso.</span>
    <span class="en">Every statement cites an official document and date accessed.</span>
    <span class="es">La ficha señala dónde un dato no pudo verificarse contra una fuente primaria, y dónde un documento existe pero está retirado de publicación.</span>
    <span class="en">Entry notes where fact could not be verified against primary source, and where a document exists but is withheld from publication.</span>
  </div>
  <p class="fecha"><span class="es">Corpus actualizado en agosto de 2026. Versión inicial: revisión de verificación pendiente.</span><span class="en">Corpus updated August 2026. Initial version: verification review pending.</span></p>
</footer>
</div>
<script>
function cambiarIdioma(){
  var b=document.body,n=b.dataset.idioma==='es'?'en':'es';
  b.dataset.idioma=n;document.documentElement.lang=n;
  try{localStorage.setItem('idioma',n)}catch(e){}
}
try{var g=localStorage.getItem('idioma');
if(g){document.body.dataset.idioma=g;document.documentElement.lang=g}}catch(e){}
</script>
</body>
</html>
"""


def enlazar(t):
    return re.sub(
        r"(?<![\w/])((?:www\.)?(?:boletinoficial\.gob\.ar|boletinoficial\.buenosaires\.gob\.ar"
        r"|documentosboletinoficial\.buenosaires\.gob\.ar|normas\.gba\.gob\.ar"
        r"|servicios\.infoleg\.gob\.ar|mpfciudad\.gob\.ar)[^\s,;)]*)",
        r'<a href="https://\1">\1</a>', t)



# ------------------------------------------------- enlaces internos a fichas

# Cada patrón apunta al slug de la ficha que trata ese instrumento.
# Orden importa: los patrones más específicos van primero.
NORMAS = [
    (r"Res(?:oluci[óo]n)?\.? ?MS ?1234/2024", "nac-res-ms-1234"),
    (r"Res(?:oluci[óo]n)?\.? ?MS ?866/2025", "nac-res-ms-866"),
    (r"Res(?:oluci[óo]n)?\.? ?MS ?710/2024", "nac-uiaas-710-2024"),
    (r"Res(?:oluci[óo]n)?\.? ?351[-/]MSEGC/24|Res(?:oluci[óo]n)? ?351/2024", "caba-res-351-2024"),
    (r"Res(?:oluci[óo]n)?\.? ?398/MJYSGC/19|Resoluci[óo]n 398", "caba-caso-srfp"),
    (r"Res(?:oluci[óo]n)?\.? ?141/SSGA/20", "caba-caso-srfp"),
    (r"Res(?:oluci[óo]n)? ?PBA ?9/2025|Resoluci[óo]n 9/2025", "pba-res-9-2025"),
    (r"Disposici[óo]n RENAPER 4133/2018|Disposici[óo]n RENAPER 1255/2023", "nac-renaper"),
    (r"RG ?AFIP ?5266/2022|RG ?5266/2022|RG ?AFIP ?4699/2020|RG ?4699/2020", "nac-afip"),
    (r"Decretos? ?1766/2011|Decretos? ?243/2017|Decrees? ?1766/2011|Decrees? ?243/2017", "nac-sibios"),
    (r"Decreto (?:Reglamentario )?98/2023", "nac-dto-98-2023"),
    (r"DNU ?941/2025", "nac-dnu-941"),
    (r"Ley ?25\.326", "nac-ley-25326"),
    (r"Ley ?27\.275", "nac-ley-27275"),
    (r"Ley ?27\.483|Ley ?27\.699|Convenio 108\+?|Convention 108\+?", "nac-convenios-108"),
    (r"Ley ?5688", "caba-ley-5688"),
    (r"Torres Abad", "nac-torres-abad"),
    (r"Clearview AI", "caba-clearview"),
    (r"Gemelo Digital Social", "nac-gemelo-digital"),
]


def normas(t, propio=None, prof=0):
    """Enlaza la primera aparición de cada instrumento a su ficha.

    propio: slug de la ficha actual — no se autoenlaza.
    Sólo la primera aparición de cada norma, para no llenar el texto de enlaces.
    """
    base = ""
    ya = set()

    def uno(m, slug):
        if slug in ya:
            return m.group(0)
        ya.add(slug)
        return f'<a class="norma-enl" href="{base}ficha-{slug}.html">{m.group(0)}</a>'

    partes = re.split(r"(<[^>]+>)", t)   # no tocar lo que ya es etiqueta
    for i, x in enumerate(partes):
        if x.startswith("<"):
            continue
        for pat, slug in NORMAS:
            if slug == propio or slug in ya:
                continue
            x = re.sub(pat, lambda m, s=slug: uno(m, s), x, count=1)
        partes[i] = x
    return "".join(partes)


# ---------------------------------------------------------------- cronología

def item(it, prof=0):
    base = ""
    cls = ' class="hilo"' if it.get("hilo") else ""
    et = ""
    if it.get("jur") in ETIQ_JUR:
        es, en = ETIQ_JUR[it["jur"]]
        et = f' <span class="jur">{bi(es, en)}</span>'
    return f'<a href="{base}ficha-{it["slug"]}.html"{cls}>{esc(it["nombre"])}</a>{et}'


def construir_cronologia(crono):
    p = [cabecera(f"{SITIO[0]} — cronología", "crono")]
    p.append('<div class="entrada">')
    p.append('<p class="es">Este repositorio sigue el crecimiento del reconocimiento facial y la vigilancia biométrica en Argentina, y el litigio que se les opuso, junto a las políticas nacionales de privacidad de datos y de seguridad que los rodean.</p>')
    p.append('<p class="en">This repository tracks the growth of facial recognition and biometric surveillance in Argentina, and the litigation brought against it, alongside the national data privacy and policing policies that surround it.</p>')
    p.append('</div>')
    p.append('<div class="crono-cabeza"><div><span class="et">' + bi('Reconocimiento facial porteño', 'City facial recognition') + '</span></div><div></div><div><span class="et">' + bi('Marco general', 'General framework') + '</span></div></div>')
    p.append('<div class="crono">')
    for fila in crono:
        izq = "<br>".join(item(i) for i in fila.get("izq", []))
        der = "<br>".join(item(i) for i in fila.get("der", []))
        p.append(f'<div class="izq">{izq}</div>')
        p.append(f'<div class="eje"><span>{fila["anio"]}</span></div>')
        p.append(f'<div class="der">{der}</div>')
    p.append('</div>')
    p.append('<div class="leyenda"><span class="marca">■</span> ' +
             bi('reconocimiento facial porteño: norma, litigio y fallos',
                'City facial recognition: norm, litigation and rulings') + '</div>')
    p.append(PIE)
    (DIST / "index.html").write_text("".join(p), encoding="utf-8")


# ---------------------------------------------------------------- índice

def construir_indice(fichas):
    p = [cabecera(f"{SITIO[0]} — índice", "indice")]
    p.append('<div class="entrada">')
    p.append('<p class="es">Veinte fichas, agrupadas por jurisdicción y ordenadas por fecha. Varias reúnen más de un instrumento.</p>')
    p.append('<p class="en">Twenty entries, grouped by jurisdiction and ordered by date. Several cover more than one instrument.</p>')
    p.append('</div>')
    for j in ORDEN_JURIS:
        grupo = [f for f in fichas if f["jurisdiccion"] == j]
        if not grupo:
            continue
        es, en = JURIS[j]
        p.append('<section class="grupo">')
        p.append(f'<div class="grupo-titulo">{bi(esc(es), esc(en))}</div>')
        p.append('<div class="indice">')
        for f in grupo:
            ees = esc(f["estado_es"].split("·")[0].strip())
            een = esc(f["estado_en"].split("·")[0].strip())
            p.append(
                f'<a class="fila" href="ficha-{f["slug"]}.html">'
                f'<span class="anio">{f["anio"]}</span>'
                f'<span class="nombre">{bi(esc(f["titulo_es"]), esc(f["titulo_en"]))}</span>'
                f'<span class="estado">{bi(ees, een)}</span></a>'
            )
        p.append("</div></section>")
    p.append(PIE)
    (DIST / "indice.html").write_text("".join(p), encoding="utf-8")


# ---------------------------------------------------------------- encuadre

def construir_encuadre(bloques):
    p = [cabecera(f"{SITIO[0]} — sobre este sitio", "encuadre")]
    for b in bloques:
        p.append('<section class="bloque">')
        p.append(f'<div class="bloque-etiqueta">{bi(esc(b["etiqueta_es"]), esc(b["etiqueta_en"]))}</div>')
        p.append(f'<div class="bloque-texto"><p class="es">{normas(notas(b["texto_es"]))}</p>'
                 f'<p class="en">{normas(notas(b["texto_en"]))}</p></div>')
        p.append('</section>')
    p.append('<section class="bloque" id="fuentes">')
    p.append(f'<div class="bloque-etiqueta">{bi("Fuentes","Sources")}</div>')
    p.append('<div class="fuentes">Constitución Nacional, arts. 31, 43, 75 inc. 22, 99 inc. 3, 121 y 129 — cotejados palabra por palabra contra el PDF oficial de Presidencia de la Nación (Casa Rosada) el 12/07/2026. Ley 26.122 (régimen de los DNU), art. 24 — texto oficial de InfoLEG, cotejado el 12/07/2026.</div>')
    p.append('</section>')
    p.append(PIE)
    (DIST / "encuadre.html").write_text("".join(p), encoding="utf-8")


# ---------------------------------------------------------------- ficha

def construir_ficha(f, ant, sig):
    es, en = JURIS[f["jurisdiccion"]]
    p = [cabecera(f'{f["titulo_es"]} — {SITIO[0]}', "", prof=1)]
    p.append('<article>')
    p.append(f'<div class="ficha-meta">{bi(esc(es)+" · "+esc(f["tema"]), esc(en)+" · "+esc(f["tema"]))}</div>')
    p.append(f'<h1 class="ficha-titulo">{bi(esc(f["titulo_es"]), esc(f["titulo_en"]))}</h1>')
    p.append(f'<p class="ficha-estado">{bi(esc(f["estado_es"]), esc(f["estado_en"]))}</p>')

    p.append('<section class="bloque">')
    p.append(f'<div class="bloque-etiqueta">{bi("Qué hace","What it does")}</div>')
    p.append(f'<div class="bloque-texto"><p class="es">{normas(notas(f["que_hace_es"]), f["slug"], 1)}</p>'
             f'<p class="en">{normas(notas(f["que_hace_en"]), f["slug"], 1)}</p></div>')
    p.append('</section>')

    p.append('<section class="bloque">')
    p.append(f'<div class="bloque-etiqueta">{bi("En contexto: "+esc(f["ctx_es"]), "In context: "+esc(f["ctx_en"]))}</div>')
    p.append(f'<div class="bloque-texto"><p class="es">{normas(notas(f["contexto_es"]), f["slug"], 1)}</p>'
             f'<p class="en">{normas(notas(f["contexto_en"]), f["slug"], 1)}</p></div>')
    p.append('</section>')

    p.append('<section class="bloque" id="fuentes">')
    p.append(f'<div class="bloque-etiqueta">{bi("Fuentes","Sources")}</div>')
    p.append(f'<div class="fuentes">{enlazar(esc(f["fuentes"]))}</div>')
    p.append('</section>')

    a = '<a href="ficha-{}.html">← {}</a>'.format(ant[0], esc(ant[1])) if ant else ""
    s = '<a href="ficha-{}.html">{} →</a>'.format(sig[0], esc(sig[1])) if sig else ""
    p.append(f'<nav class="pie-ficha"><span>{a}</span><span>{s}</span></nav>')
    p.append('</article>')
    p.append(PIE)
    (DIST / f'ficha-{f["slug"]}.html').write_text("".join(p), encoding="utf-8")


def construir_derechos(d):
    p = [cabecera(f"{SITIO[0]} — qué se puede hacer", "derechos")]
    p.append('<div class="entrada ancha">')
    p.append(f'<p class="es">{esc(d["entrada_es"])}</p><p class="en">{esc(d["entrada_en"])}</p>')
    p.append('</div>')
    for r in d["derechos"]:
        p.append('<section class="derecho">')
        p.append(f'<div class="derecho-nombre">{bi(esc(r["nombre_es"]), esc(r["nombre_en"]))}'
                 f'<span class="norma">{normas(esc(r["norma"]))}</span></div>')
        p.append(f'<div class="derecho-texto"><p class="es">{normas(marcado(r["texto_es"]))}</p>'
                 f'<p class="en">{normas(marcado(r["texto_en"]))}</p></div>')
        p.append('</section>')
    p.append(f'<div class="aviso"><p class="es">{normas(marcado(d["aviso_es"]))}</p>'
             f'<p class="en">{normas(marcado(d["aviso_en"]))}</p></div>')
    p.append('<section class="bloque" id="fuentes" style="margin-top:30px">')
    p.append(f'<div class="bloque-etiqueta">{bi("Fuentes","Sources")}</div>')
    p.append(f'<div class="fuentes">{enlazar(esc(d["fuentes"]))}</div></section>')
    p.append(PIE)
    (DIST / "derechos.html").write_text("".join(p), encoding="utf-8")


def marcado(t):
    """Escapa el texto pero conserva los <span class="plazo">."""
    partes = re.split(r'(<span class="plazo">|</span>)', t)
    salida = []
    for x in partes:
        salida.append(x if x.startswith("<span") or x == "</span>" else notas(x))
    return "".join(salida)


def main():
    fichas = json.loads((DATA / "fichas.json").read_text(encoding="utf-8"))
    crono = json.loads((DATA / "cronologia.json").read_text(encoding="utf-8"))
    encuadre = json.loads((DATA / "encuadre.json").read_text(encoding="utf-8"))
    derechos = json.loads((DATA / "derechos.json").read_text(encoding="utf-8"))

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    shutil.copy(RAIZ / "estilo.css", DIST / "estilo.css")

    construir_cronologia(crono)
    construir_indice(fichas)
    construir_encuadre(encuadre)
    construir_derechos(derechos)
    for i, f in enumerate(fichas):
        ant = (fichas[i-1]["slug"], fichas[i-1]["titulo_es"]) if i > 0 else None
        sig = (fichas[i+1]["slug"], fichas[i+1]["titulo_es"]) if i < len(fichas)-1 else None
        construir_ficha(f, ant, sig)

    print(f"listo — {len(fichas)} fichas + cronología + índice + derechos + encuadre")


if __name__ == "__main__":
    main()
