importScripts('vendor/xlsx.full.min.js','engine.js');
onmessage=event=>{
 try{
  const {buffer,name}=event.data;SheetReview.zipPreflight(buffer);
  const wb=XLSX.read(buffer,{type:'array',cellFormula:true,sheetStubs:true,cellHTML:false,cellText:true,bookVBA:false,bookDeps:false});
  postMessage({ok:true,result:SheetReview.auditWorkbook(wb,name)});
 }catch(error){postMessage({ok:false,error:error.message||'This workbook could not be read.'});}
};
