/* The same API client is used by the forum and the game-chat widget. */
(function(root){
 'use strict';
 class HumansOnlyClient {
  constructor(endpoint, token='') { this.endpoint=endpoint.replace(/\/$/,''); this.token=token; }
  async request(path, data, signal) {
   const headers={};if(this.token)headers.Authorization='Bearer '+this.token;
   if(data!==undefined)headers['Content-Type']='application/json';
   const response=await fetch(this.endpoint+'/api/v1'+path,{method:data===undefined?'GET':'POST',headers,body:data===undefined?undefined:JSON.stringify(data),cache:'no-store',credentials:'omit',signal:signal||AbortSignal.timeout(15000)});
   let value;try{value=await response.json();}catch{throw new Error('The community server returned an unreadable response.');}
   if(!response.ok){const error=new Error(value.error||'The request failed.');error.status=response.status;throw error;}
   return value;
  }
  async signIn(username,password){const value=await this.request('/auth/login',{username,password});this.token=value.token;return value;}
  messages(room,topic=''){return this.request('/messages?'+new URLSearchParams({room,topic}));}
  send(room,body,topic=''){return this.request('/messages',{room,body,topic});}
 }
 root.HumansOnlyClient=HumansOnlyClient;
 if(typeof module!=='undefined'&&module.exports)module.exports=HumansOnlyClient;
})(typeof window==='undefined'?globalThis:window);
