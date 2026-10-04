'use strict';
importScripts('chess-engine.js','chess-solver.js');
onmessage=event=>{
  try{
    const result=ChessSolver.analyze(event.data.state,event.data.options,report=>postMessage({type:'progress',report}));
    postMessage({type:'done',report:result});
  }catch(error){postMessage({type:'error',message:error.message});}
};
