#!/usr/bin/env node
'use strict';
const fs=require('node:fs');
const {Habitat}=require('./chess-engine.js');
const {analyze}=require('./chess-solver.js');
const args=process.argv.slice(2),file=args.find(a=>!a.startsWith('--'));
const number=(name,fallback)=>Number(args.find(a=>a.startsWith(`--${name}=`))?.split('=')[1])||fallback;
const state=file?JSON.parse(fs.readFileSync(file,'utf8')):new Habitat(8,8,'solver-start',1);
const result=analyze(state,{milliseconds:number('ms',5000),maxNodes:number('nodes',100000),maxDepth:number('depth',1200)});
process.stdout.write(JSON.stringify(result,null,2)+'\n');
