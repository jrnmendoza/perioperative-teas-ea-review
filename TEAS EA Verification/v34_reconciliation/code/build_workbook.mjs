import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const base=path.dirname(path.dirname(new URL(import.meta.url).pathname)).replaceAll('%20',' ');
const state=JSON.parse(await fs.readFile(`${base}/data/final_stage.json`,'utf8'));
const out=path.join(base,'..','TEAS_EA_RECONCILED_MASTER_DATA_v34_FINAL_LOCK_READY.xlsx');
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(`${base}/inputs/v33_working_copy.xlsx`));
const inv=state.inputs.v33.sheets;
function col(n){let s='';while(n){n--;s=String.fromCharCode(65+n%26)+s;n=Math.floor(n/26);}return s;}
const compact=new Set(['README','Summary','AF_Lock_Summary','Opioid_Primary_Summary']);
const tableLog=[];
for(const [name,rows0] of Object.entries(state.updates)){
  const exists=!!inv[name];
  const sh=exists?wb.worksheets.getItem(name):wb.worksheets.add(name);
  const nc=Math.max(...rows0.map(r=>r.length)), nr=rows0.length;
  const rows=rows0.map(r=>Array.from({length:nc},(_,i)=>r[i]??null));
  if(name==='Summary') for(const m of inv[name].merges)if(m!=='A1:H1')sh.unmergeCells(m);
  // Clear values in the old bounded area so removed derived rows do not survive.
  if(exists)sh.getRange(`A1:${col(Math.max(inv[name].columns,nc))}${Math.max(inv[name].rows,nr)}`).clear({applyTo:'contents'});
  sh.getRange(`A1:${col(nc)}${nr}`).values=rows;
  if(!exists){
    sh.showGridLines=false;
    const rg=sh.getRange(`A1:${col(nc)}${nr}`);
    rg.format.font={name:'Arial',size:10,color:'#172B4D'};
    rg.format.verticalAlignment='top';rg.format.wrapText=true;
    rg.format.columnWidth=24;rg.format.rowHeight=45;
    sh.getRange(`A1:${col(nc)}1`).format={fill:'#234E70',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:36};
    sh.freezePanes.freezeRows(1);sh.freezePanes.freezeColumns(Math.min(2,nc));
    for(let c=0;c<nc;c++){
      const h=String(rows[0][c]??'').toLowerCase();const r=sh.getRange(`${col(c+1)}1:${col(c+1)}${nr}`);
      if(/note|reason|quote|value|source_location|source location|effect_note|problem|evidence/.test(h))r.format.columnWidth=64;
      else if(/link|url|filename|source_pdf|source pdf/.test(h))r.format.columnWidth=48;
      else if(/outcome|intervention|comparator|endpoint|window|timepoint/.test(h))r.format.columnWidth=36;
      else if(/count|^n_|^mean|^sd_|^events|^se$|^effect$|^k$/.test(h))r.format.columnWidth=14;
    }
    rg.format.autofitRows();
  }else if(!compact.has(name)){
    // Existing source cells keep their styles. Format only new rows/columns.
    if(nr>inv[name].rows){const rg=sh.getRange(`A${inv[name].rows+1}:${col(nc)}${nr}`);rg.format.font={name:'Arial',size:10};rg.format.wrapText=true;rg.format.rowHeight=48;}
    if(nc>inv[name].columns){const rg=sh.getRange(`${col(inv[name].columns+1)}1:${col(nc)}${nr}`);rg.format.columnWidth=30;rg.format.wrapText=true;sh.getRange(`${col(inv[name].columns+1)}1:${col(nc)}1`).format={fill:'#234E70',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true};}
    sh.freezePanes.freezeRows(1);
  }
  // Recreate the native table at its complete current extent. The frozen input
  // preserves the historical table definitions; stale truncated filters repaired.
  const oldTables=[...sh.tables.items];
  if(oldTables.length){
    for(const t of oldTables){const oldName=t.name;const oldStyle=t.style;t.delete();const nt=sh.tables.add(`A1:${col(nc)}${nr}`,true,oldName);if(oldStyle)nt.style=oldStyle;tableLog.push({sheet:name,table:oldName,range:`A1:${col(nc)}${nr}`});}
  }else if(!compact.has(name)&&rows[0].every(h=>typeof h==='string'&&h.length)&&new Set(rows[0]).size===nc){
    const t=sh.tables.add(`A1:${col(nc)}${nr}`,true,'V34_'+name.replaceAll(/[^A-Za-z0-9_]/g,'_'));tableLog.push({sheet:name,table:t.name,range:`A1:${col(nc)}${nr}`});
  }
  console.log(`${name}: ${nr-1} rows`);
}
// Extend untouched native inventory/RoB tables to include all existing records.
for(const name of ['Corrected_RoB2','AG_Candidate_Data']){
 const sh=wb.worksheets.getItem(name);
 for(const t of [...sh.tables.items]){const n=t.name,style=t.style;t.delete();const nt=sh.tables.add(`A1:${col(inv[name].columns)}${inv[name].rows}`,true,n);if(style)nt.style=style;tableLog.push({sheet:name,table:n,range:`A1:${col(inv[name].columns)}${inv[name].rows}`});}
}
const sum=wb.worksheets.getItem('Summary');
sum.getRange('A3:A19').format.columnWidth=48;sum.getRange('B3:B19').format.columnWidth=16;
sum.getRange('D3:D19').format.columnWidth=55;sum.getRange('A3:H19').format.rowHeight=24;
sum.getRange('A4:B19').format.fill='#FFFFFF';sum.getRange('A4:B19').format.font={name:'Arial',size:11,color:'#172B4D'};
sum.getRange('D4').format.wrapText=true;sum.getRange('D4').format.rowHeight=40;
const rm=wb.worksheets.getItem('README');rm.getRange('B3:B35').format.columnWidth=120;rm.getRange('A3:B35').format.wrapText=true;rm.getRange('A3:B35').format.autofitRows();
wb.recalculate();
console.log((await wb.inspect({kind:'region',sheetId:'Summary',range:'A3:D12',maxChars:1800,tableMaxRows:10,tableMaxCols:4})).ndjson);
for(const [name,range,file] of [['Summary','A1:H19','v34_summary'],['V34_QC','A1:C8','v34_qc'],['Outcome_Data','A178:L183','liang_correction'],['V34_Source_Conflicts','A1:H5','source_conflicts'],['V34_Audit_Dispositions','A1:H5','audit_dispositions']]){
 const png=await wb.render({sheetName:name,range,scale:1.2,format:'png'});
 await fs.writeFile(`${base}/previews/${file}.png`,new Uint8Array(await png.arrayBuffer()));
}
const blob=await SpreadsheetFile.exportXlsx(wb);await blob.save(out);
// The full automatic debug dump repeats all workbook content; the bounded
// previews, stage JSON and independent QC report provide the retained audit.
await fs.rm(`${out}.inspect.ndjson`,{force:true});
await fs.writeFile(`${base}/data/table_ranges.json`,JSON.stringify(tableLog,null,2));
console.log(`EXPORTED ${out}`);
