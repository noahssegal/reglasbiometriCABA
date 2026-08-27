const fs=require('fs');
const {Document,Packer,Paragraph,TextRun,HeadingLevel,BorderStyle}=require('docx');
const F=JSON.parse(fs.readFileSync('data/fichas.json','utf8'));
const D=JSON.parse(fs.readFileSync('data/derechos.json','utf8'));
const E=JSON.parse(fs.readFileSync('data/encuadre.json','utf8'));
const JUR={nacional:'National',caba:'Buenos Aires City',pba:'Province of Buenos Aires'};
const NEW=['caba-camaras-privadas','caba-res-398-2019','nac-conarc'];
const k=[];
const P=(t,o={})=>new Paragraph({spacing:{after:o.after??120},...o,children:[new TextRun({text:t,...o.run})]});
const lbl=t=>new Paragraph({spacing:{before:180,after:60},children:[new TextRun({text:t,bold:true,size:19,color:"666660"})]});
const rule=()=>new Paragraph({spacing:{before:240,after:120},border:{bottom:{style:BorderStyle.SINGLE,size:6,color:"CCCCC4"}},children:[]});
k.push(new Paragraph({heading:HeadingLevel.HEADING_1,children:[new TextRun("Marco legal — final read-through")]}));
k.push(P("Twenty-three entries, both languages. English sits above Spanish: English is authoritative, Spanish follows it.",{run:{size:22}}));
k.push(P("Entries 1, 5, 8, 10, 19 and 21, plus both closing sections, are rewritten to a plainer register — instrument as subject, active verb, one idea per sentence, same facts and same footnotes.",{run:{size:22}}));
k.push(P("Status now uses two fields: what the instrument is, and whether what it authorises is running. Anything else sits in a note beneath.",{run:{size:22}}));
k.push(P("Edit in track changes and comment anything you want me to decide.",{run:{size:22,italics:true}}));
k.push(new Paragraph({heading:HeadingLevel.HEADING_2,children:[new TextRun("Still open")]}));
[["RENAPER — a sentence removed by your own rule","Applying “match Spanish to English”, I cut «el RENAPER no ejecutó en más de tres años una sola cancelación de datos» from the Spanish, because you had deleted it from the English. It also still appears on the rights page, citing the same source. Restore, or cut there too?"],
 ["SIBIOS — where I broke the rule on purpose","The English had lost the clause about the 2017 decree designating the Dirección Nacional de Policía Científica. That is the fact the independent reader confirmed word for word, so I added it to English rather than delete it from Spanish. Confirm or reverse."],
 ["Theme labels","Never translate — every entry reads “Buenos Aires City · Reconocimiento facial” in English mode. Twenty-three short translations; the terms are yours."],
 ["Three new entries","Marked NEW below. Added after the independent-reading exercise closed, so nobody but me has checked them."],
 ["Two statuses I am unsure of","The SRFP case is marked “appeals court ruling”, not “final”: whether it went to a higher court was never verified. And Ley 5688 is marked “conditioned by court ruling” because the SRFP is, while the Preventive and Forensic Systems have no known implementation. Both carry notes."]
].forEach(([h,b])=>{k.push(lbl(h));k.push(P(b,{run:{size:21}}))});
k.push(new Paragraph({pageBreakBefore:true,heading:HeadingLevel.HEADING_2,children:[new TextRun("The entries")]}));
F.forEach((f,i)=>{
  k.push(new Paragraph({spacing:{before:300,after:60},heading:HeadingLevel.HEADING_3,children:[new TextRun(`${i+1}. ${f.titulo_en}${NEW.includes(f.slug)?"  ·  NEW, unverified":""}`)]}));
  k.push(P(`${JUR[f.jurisdiccion]} · ${f.tema}`,{run:{size:19,color:"888880"}}));
  k.push(P(`estado: ${f.estado}   |   operación: ${f.operacion}${f.litigio?'   |   litigio: '+f.litigio:''}${f.gestion?'   |   gestión: '+f.gestion:''}`,{run:{size:18,color:"777770"}}));
  if(f.nota_estado) k.push(P(f.nota_estado,{run:{size:18,color:"888880",italics:true}}));
  k.push(lbl("What it does"));   k.push(P(f.que_hace_en,{run:{size:21}}));
  k.push(lbl("Qué hace"));       k.push(P(f.que_hace_es,{run:{size:21,color:"444440"}}));
  if(f.contexto_en){k.push(lbl(`In context: ${f.ctx_en||''}`));k.push(P(f.contexto_en,{run:{size:21}}));
                    k.push(lbl(`En contexto: ${f.ctx_es||''}`));k.push(P(f.contexto_es,{run:{size:21,color:"444440"}}));}
  k.push(lbl("Sources")); k.push(P(f.fuentes,{run:{size:17,color:"777770"}}));
  k.push(rule());
});
k.push(new Paragraph({pageBreakBefore:true,heading:HeadingLevel.HEADING_2,children:[new TextRun("What you can do")]}));
D.derechos.forEach(x=>{k.push(lbl(`${x.nombre_en}  —  ${x.norma||''}`));k.push(P(x.texto_en,{run:{size:21}}));k.push(P(x.texto_es,{run:{size:21,color:"444440"}}));});
if(D.aviso_en) k.push(P(D.aviso_en,{run:{size:20,italics:true}}));
k.push(new Paragraph({pageBreakBefore:true,heading:HeadingLevel.HEADING_2,children:[new TextRun("About this site")]}));
E.forEach(e=>{k.push(lbl(e.etiqueta_en));k.push(P(e.texto_en,{run:{size:21}}));k.push(P(e.texto_es,{run:{size:21,color:"444440"}}));});
const doc=new Document({styles:{default:{document:{run:{font:"Calibri",size:21}}}},
 sections:[{properties:{page:{size:{width:12240,height:15840},margin:{top:1080,bottom:1080,left:1200,right:1200}}},children:k}]});
Packer.toBuffer(doc).then(b=>{fs.writeFileSync('../marco_legal_revision_final.docx',b);console.log('escrito');});
