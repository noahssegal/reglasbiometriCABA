const fs=require('fs');
const {Document,Packer,Paragraph,TextRun,HeadingLevel,BorderStyle}=require('docx');
const F=JSON.parse(fs.readFileSync('data/fichas.json','utf8'));
const D=JSON.parse(fs.readFileSync('data/derechos.json','utf8'));
const E=JSON.parse(fs.readFileSync('data/encuadre.json','utf8'));
const JUR={nacional:'National',caba:'Buenos Aires City',pba:'Province of Buenos Aires'};
const NEW=['caba-camaras-privadas','caba-res-398-2019','nac-conarc'];
const k=[];
const P=(t,o={})=>new Paragraph({spacing:{after:o.after??120},...o,children:[new TextRun({text:t,...o.run})]});
const lbl=t=>new Paragraph({spacing:{before:170,after:55},children:[new TextRun({text:t,bold:true,size:19,color:"666660"})]});
const rule=()=>new Paragraph({spacing:{before:230,after:110},border:{bottom:{style:BorderStyle.SINGLE,size:6,color:"CCCCC4"}},children:[]});
k.push(new Paragraph({heading:HeadingLevel.HEADING_1,children:[new TextRun("Entries 9 to 23 — English")]}));
k.push(P("Entries 1 to 8 are settled. These are the rest, in the same format: what it does, in context, sources.",{run:{size:22}}));
k.push(P("Edit in track changes. Use comments for anything you want me to decide, check or cut. Send the file back and I will apply it and match the Spanish.",{run:{size:22,italics:true}}));
k.push(P("Conventions from the first eight: instrument as subject, active verb, one idea per sentence. Spanish only for instrument names. No claims argued from a document's silence — state the rule positively instead. Absence claims are fine when they report a dated search.",{run:{size:21,color:"666660"}}));
F.forEach((f,i)=>{
  if(i<8) return;
  k.push(new Paragraph({spacing:{before:290,after:55},heading:HeadingLevel.HEADING_2,children:[new TextRun(`${i+1}. ${f.titulo_en}${NEW.includes(f.slug)?"  ·  NEW, unverified":""}`)]}));
  k.push(P(`${JUR[f.jurisdiccion]} · ${f.tema}`,{run:{size:19,color:"888880"}}));
  k.push(P(`estado: ${f.estado}   |   operación: ${f.operacion}${f.litigio?'   |   litigio: '+f.litigio:''}${f.gestion?'   |   gestión: '+f.gestion:''}`,{run:{size:18,color:"777770"}}));
  if(f.nota_estado) k.push(P(f.nota_estado,{run:{size:18,color:"888880",italics:true}}));
  k.push(lbl("What it does"));  k.push(P(f.que_hace_en,{run:{size:21}}));
  if(f.contexto_en){k.push(lbl(`In context — ${f.ctx_en||''}`)); k.push(P(f.contexto_en,{run:{size:21}}));}
  k.push(lbl("Sources")); k.push(P(f.fuentes,{run:{size:17,color:"777770"}}));
  k.push(rule());
});
k.push(new Paragraph({pageBreakBefore:true,heading:HeadingLevel.HEADING_1,children:[new TextRun("What you can do")]}));
D.derechos.forEach(x=>{k.push(lbl(`${x.nombre_en}  —  ${x.norma||''}`));k.push(P(x.texto_en,{run:{size:21}}));});
if(D.aviso_en) k.push(P(D.aviso_en,{run:{size:20,italics:true}}));
k.push(new Paragraph({pageBreakBefore:true,heading:HeadingLevel.HEADING_1,children:[new TextRun("About this site")]}));
E.forEach(e=>{k.push(lbl(e.etiqueta_en));k.push(P(e.texto_en,{run:{size:21}}));});
const doc=new Document({styles:{default:{document:{run:{font:"Calibri",size:21}}}},
 sections:[{properties:{page:{size:{width:12240,height:15840},margin:{top:1080,bottom:1080,left:1200,right:1200}}},children:k}]});
Packer.toBuffer(doc).then(b=>{fs.writeFileSync('../marco_legal_entradas_9_a_23.docx',b);console.log('escrito');});
