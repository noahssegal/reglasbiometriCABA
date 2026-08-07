# Marco legal — reconocimiento facial y vigilancia biométrica en Argentina

Repositorio público de veinte fichas sobre reconocimiento facial, identificación
biométrica y videovigilancia en la Nación, la Ciudad de Buenos Aires y la
Provincia de Buenos Aires, con el litigio que se les opuso y las normas de
protección de datos que los rodean. Bilingüe, castellano e inglés.

> **El corpus no completó todavía su revisión final de verificación.** Nueve de las veinte fichas pasaron por una
> lectura independiente contra el documento original; las once restantes se
> apoyan por ahora en una sola lectura, y ocho citan documentos cuyo enlace
> oficial no está resuelto. Se publica en ese estado, no como un texto cerrado.

Sitio: `docs/index.html`

## Cómo se cita

Cada afirmación remite a un documento oficial y a la fecha en que se lo leyó.
Cuando un dato no pudo verificarse contra una fuente primaria, la ficha lo dice
en lugar de omitirlo. Cuando un documento existe pero está retirado de
publicación, la ficha lo señala como tal.

El corpus se cerró en agosto de 2026. La legislación cambia: conviene cotejar
contra la fuente oficial antes de usar estos datos.

## Cómo está armado

Todo el contenido vive en cuatro archivos de datos. El sitio se genera a partir
de ellos, en Python, sin dependencias externas.

```
data/fichas.json       las veinte fichas
data/cronologia.json   la portada
data/derechos.json     "Qué se puede hacer"
data/encuadre.json     "Sobre este sitio"

chequeos.py   controles mecánicos — corre primero y frena si algo falla
construir.py  genera el sitio en docs/
verificar.py  genera la tabla de cotejo afirmación/fuente
```

Para reconstruir:

```
python3 chequeos.py && python3 construir.py && python3 verificar.py
```

`chequeos.py` verifica paridad de notas al pie entre castellano e inglés, que
toda fuente esté citada y toda cita tenga fuente, que no haya fechas de lectura
futuras, que no haya enlaces rotos en la cronología, y que el instrumento del
título aparezca en su propia fuente [1].

## Verificación

Además de los controles mecánicos, las afirmaciones del corpus se sometieron a
una lectura independiente: diez lotes de preguntas respondidos por otro agente
sobre el documento fuente adjunto, sin ver la ficha. Las respuestas se cotejaron
carácter por carácter contra el texto oficial.

```
lotes_verificacion/   los diez lotes y sus documentos fuente
COTEJO_LOTES_1-9.md   resultado del cotejo
```

Ese procedimiento encontró un error de fondo (DNU 941/2025) y confirmó el resto.
Su límite está documentado: un lector independiente que contesta preguntas
escritas por quien redactó el corpus no puede encontrar lo que el corpus omitió.

## Uso de inteligencia artificial

Este sitio se hizo con ayuda de inteligencia artificial para organizar el
material, acceder a los textos oficiales y redactar los primeros borradores de
las fichas.

---

# Legal framework — facial recognition and biometric surveillance in Argentina

A public repository of twenty entries on facial recognition, biometric
identification, and video surveillance at national level, in Buenos Aires City,
and in the Province of Buenos Aires, together with the litigation brought
against them and the data protection rules that surround them. Bilingual,
Spanish and English.

> **The corpus has not yet completed its final verification review.** Nine of the twenty entries have been through an
> independent reading against the original document; the remaining eleven rest on
> a single reading, and eight cite documents whose official link is unresolved.
> It is published in that state, not as a closed text.

Every statement points to an official document and the date it was read. The
corpus closed in August 2026; legislation changes, so check against the official
source before relying on anything here.

Content lives in four JSON files under `data/`. The site is generated from them
in plain Python, no external dependencies. Run `python3 chequeos.py &&
python3 construir.py`.
