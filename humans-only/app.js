(function(){
 'use strict';
 const $=id=>document.getElementById(id), params=new URLSearchParams(location.search);
 const onServer=['localhost','127.0.0.1','[::1]'].includes(location.hostname)||location.hostname.endsWith('.ts.net');
 const endpoint=onServer?location.origin:window.HUMANSONLY_CONFIG.endpoint;
 const storageKey='humansonly-session:'+endpoint;
 let token='';try{token=sessionStorage.getItem(storageKey)||'';}catch{}
 const api=new HumansOnlyClient(endpoint,token);
 let user=null,rooms=[],room=params.get('room')||'commons',topic='',view='chat',joining=false,loading=false,review=null;
 if(params.get('widget')==='1')document.body.classList.add('widget');
 const element=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const date=seconds=>new Date(seconds*1000).toLocaleString(undefined,{dateStyle:'medium',timeStyle:'short'});
 function remember(value){api.token=value||'';try{if(value)sessionStorage.setItem(storageKey,value);else sessionStorage.removeItem(storageKey);}catch{announce('Your browser cannot store the sign-in for this tab. Keep this page open.');}}
 function announce(message){$('notice').textContent=message;$('notice').hidden=!message;}
 function connected(ok){$('connection').dataset.state=ok?'online':'offline';$('connection').textContent=ok?'COMMUNITY SERVER / CONNECTED · Posts refresh every 8 seconds':'COMMUNITY SERVER / UNAVAILABLE · Your draft stays here. Try Refresh shortly.';}
 async function run(button,task,errorId){if(button)button.disabled=true;try{if(errorId)$(errorId).textContent='';await task();}catch(e){if(errorId)$(errorId).textContent=e.message;else announce(e.message);}finally{if(button)button.disabled=false;syncAccount();}}
 function openAccount(){ $('account-error').textContent='';syncAccount();$('account').showModal();}
 function syncAccount(){
  $('signed-out').hidden=!!user;$('signed-in').hidden=!user;
  $('account-button').textContent=user?'@'+user.username:'Sign in / join';
  const paused=user&&user.timeout_until>Date.now()/1000;
  $('timeout').hidden=!paused;
  if(paused)$('timeout-text').textContent=user.timeout_reason+' · Returns '+date(user.timeout_until)+'.';
  $('compose-hint').textContent=user?(paused?'Reflection time. You can still read and appeal.':'Posting as @'+user.username+'. Text only; 4,000 characters maximum.'):'Sign in to post. Everyone can read the all-ages rooms.';
  $('send').textContent=user?'Post message ↗':'Sign in to post ↗';
  $('send').disabled=!!paused||!!(user&&user.must_change_password);
  $('message-body').disabled=!!paused;
  $('moderation-button').hidden=!user||!['owner','moderator'].includes(user.role);
  if(user){$('account-summary').textContent='@'+user.username+' · '+user.role;$('renew-age').value=user.age_group;$('password-details').open=!!user.must_change_password;}
 }
 function renderRooms(){
  $('rooms').replaceChildren();
  for(const r of rooms){const button=element('button',r.id===room?'active':'',r.title);button.type='button';button.append(element('small','',(r.available?'':'◇ ')+r.label));button.setAttribute('aria-pressed',String(r.id===room));button.onclick=()=>selectRoom(r.id);$('rooms').append(button);}
  const current=rooms.find(r=>r.id===room);
  if(current){$('room-title').textContent=current.title;$('room-age').textContent=current.label;$('room-description').textContent=current.description;}
 }
 async function selectRoom(id){room=id;topic='';view='chat';$('messages').replaceChildren();$('topic-list').replaceChildren();renderRooms();renderTabs();await load();}
 function renderTabs(){ $('chat-tab').setAttribute('aria-pressed',String(view==='chat'));$('topics-tab').setAttribute('aria-pressed',String(view==='topics'));$('topic-list').hidden=view!=='topics'||!!topic;$('messages').hidden=view==='topics'&&!topic;$('compose').hidden=view==='topics'&&!topic;$('topic-banner').hidden=!topic;}
 async function refreshIdentity(){const result=await api.request('/me');user=result.user;if(!user&&api.token)remember('');syncAccount();const resultRooms=await api.request('/rooms');rooms=resultRooms.rooms;if(!rooms.some(r=>r.id===room))room='commons';renderRooms();}
 async function load(){
  if(loading)return;loading=true;
  const selectedRoom=room,selectedTopic=topic,selectedView=view;
  try{
   announce('');
   if(view==='topics'&&!topic){const result=await api.request('/topics?'+new URLSearchParams({room}));if(room!==selectedRoom||topic!==selectedTopic||view!==selectedView)return;renderTopics(result.topics);$('empty').hidden=!!result.topics.length;$('empty').textContent='No topics yet. Start a conversation.';}
   else{const result=await api.messages(room,topic);if(room!==selectedRoom||topic!==selectedTopic||view!==selectedView)return;renderMessages(result.messages);$('empty').hidden=!!result.messages.length;$('empty').textContent='No messages yet. A quiet room is an invitation.';}
   connected(true);
  }catch(e){if(e.status){$('messages').replaceChildren();$('topic-list').replaceChildren();$('empty').hidden=false;$('empty').textContent=e.message;connected(true);}else{connected(false);announce('The laptop server is unreachable. Your unsent message has not been submitted.');}}
  finally{loading=false;}
 }
 function renderMessages(messages){
  const target=$('messages'),nearBottom=target.scrollHeight-target.scrollTop-target.clientHeight<70,oldScroll=target.scrollTop;
  target.replaceChildren();
  for(const m of messages){const card=element('article','message'+(m.hidden?' removed':''));const head=element('div','message-head');head.append(element('strong','',m.username));const timestamp=element('time','',date(m.created));timestamp.dateTime=new Date(m.created*1000).toISOString();head.append(timestamp);
   if(user&&!m.hidden){const report=element('button','report','Report');report.type='button';report.setAttribute('aria-label','Report message by '+m.username);report.onclick=()=>{review={type:'report',id:m.id};$('review-title').textContent='Report this message';$('review-reason').value='';$('review-error').textContent='';$('review-dialog').showModal();};head.append(report);}
   card.append(head,element('p','message-body',m.body));target.append(card);
  }
  target.scrollTop=nearBottom?target.scrollHeight:oldScroll;
 }
 function renderTopics(topics){$('topic-list').replaceChildren();for(const t of topics){const button=element('button','topic-row');button.type='button';button.append(element('strong','',t.title),element('small','',t.username+' · '+date(t.created)+' · '+t.replies+' messages'));button.onclick=async()=>{topic=t.id;$('topic-title').textContent=t.title;renderTabs();await load();};$('topic-list').append(button);}}
 $('account-button').onclick=openAccount;
 $('login-tab').onclick=()=>setAuthMode(false);$('join-tab').onclick=()=>setAuthMode(true);
 function setAuthMode(join){joining=join;$('join-fields').hidden=!join;$('join-tab').setAttribute('aria-pressed',String(join));$('login-tab').setAttribute('aria-pressed',String(!join));$('password').autocomplete=join?'new-password':'current-password';$('password').minLength=join?12:1;}
 $('auth-form').onsubmit=e=>{e.preventDefault();run(e.submitter,async()=>{
  const data={username:$('username').value,password:$('password').value};
  if(joining)Object.assign(data,{age_group:$('age-group').value,human:$('human').checked,accepted_rules:$('accept').checked,website:$('website').value});
  const result=await api.request(joining?'/auth/register':'/auth/login',data);remember(result.token);user=result.user;$('password').value='';await refreshIdentity();
  if(user.must_change_password){$('account-error').textContent='Please change your temporary setup passphrase before using owner powers.';syncAccount();}else $('account').close();await load();
 },'account-error');};
 $('logout').onclick=()=>run($('logout'),async()=>{await api.request('/auth/logout',{});remember('');user=null;room='commons';topic='';view='chat';await refreshIdentity();renderTabs();$('account').close();await load();},'account-error');
 $('age-form').onsubmit=e=>{e.preventDefault();run(e.submitter,async()=>{await api.request('/me/age',{age_group:$('renew-age').value});await refreshIdentity();await load();$('account-error').textContent='Age declaration saved.';},'account-error');};
 $('password-form').onsubmit=e=>{e.preventDefault();run(e.submitter,async()=>{const r=await api.request('/me/password',{current:$('current-password').value,password:$('new-password').value});remember(r.token);$('current-password').value='';$('new-password').value='';await refreshIdentity();$('account-error').textContent='Passphrase changed. Other sessions have been signed out.';},'account-error');};
 $('chat-tab').onclick=async()=>{view='chat';topic='';renderTabs();await load();};
 $('topics-tab').onclick=async()=>{view='topics';topic='';renderTabs();await load();};
 $('back-topics').onclick=async()=>{view='topics';topic='';renderTabs();await load();};
 $('refresh').onclick=()=>run($('refresh'),async()=>{await refreshIdentity();await load();});
 $('compose').onsubmit=e=>{e.preventDefault();if(!user){openAccount();return;}run(e.submitter,async()=>{const draft=$('message-body').value;await api.send(room,draft,topic);$('message-body').value='';await refreshIdentity();await load();});};
 $('new-topic').onclick=()=>{if(!user){openAccount();return;}if(user.timeout_until>Date.now()/1000){announce('Your commenting is paused. You can still read and appeal.');return;}$('topic-error').textContent='';$('topic-dialog').showModal();};
 $('topic-form').onsubmit=e=>{e.preventDefault();run(e.submitter,async()=>{const result=await api.request('/topics',{room,title:$('new-title').value,body:$('new-body').value});topic=result.topic;view='topics';$('topic-title').textContent=$('new-title').value;$('new-title').value='';$('new-body').value='';$('topic-dialog').close();renderTabs();await load();},'topic-error');};
 $('appeal-button').onclick=()=>{review={type:'appeal'};$('review-title').textContent='Appeal your timeout';$('review-reason').value='';$('review-error').textContent='';$('review-dialog').showModal();};
 $('review-form').onsubmit=e=>{e.preventDefault();run(e.submitter,async()=>{const body=$('review-reason').value;await api.request(review.type==='report'?'/reports':'/appeals',review.type==='report'?{message_id:review.id,reason:body}:{body});$('review-dialog').close();announce('Sent to the moderation desk. Thank you.');},'review-error');};
 $('moderation-button').onclick=()=>run($('moderation-button'),async()=>{await moderation();$('account').close();$('moderation-dialog').showModal();},'account-error');
 async function moderation(){
  const data=await api.request('/moderation');$('moderation-items').replaceChildren();
  if(!data.reports.length&&!data.appeals.length)$('moderation-items').append(element('p','','The desk is clear. No open reports or appeals.'));
  for(const item of [...data.reports.map(r=>({...r,kind:'report'})),...data.appeals.map(a=>({...a,kind:'appeal'}))]){
   const card=element('article','mod-item');card.append(element('h3','',item.kind==='report'?'Report: @'+item.username:'Appeal: @'+item.username));
   if(item.kind==='report')card.append(element('blockquote','',item.body),element('p','','Report: '+item.reason));else card.append(element('p','',item.body));
   const label=element('label','','Moderator’s reason (required)');const reason=element('textarea');reason.rows=2;reason.maxLength=1000;reason.minLength=10;label.append(reason);card.append(label);
   const actions=item.kind==='report'?[['hide','Remove message'],['timeout','Seven-day timeout'],['dismiss','Dismiss report']]:[['release','End timeout / accept appeal']];
   for(const [action,text] of actions){const button=element('button','',text);button.type='button';button.onclick=()=>run(button,async()=>{await api.request('/moderation',{action,reason:reason.value,message_id:item.message_id,report_id:item.id,user_id:item.kind==='report'?item.author_id:item.user_id});await moderation();},'moderation-error');card.append(button);}
   $('moderation-items').append(card);
  }
 }
 async function start(){try{await refreshIdentity();renderTabs();connected(true);await load();}catch{connected(false);$('empty').textContent='The community server is offline. The charter and your unsent draft remain available.';}syncAccount();}
 start();
 setInterval(async()=>{if(document.hidden||loading)return;try{await refreshIdentity();await load();}catch{connected(false);}},8000);
 document.addEventListener('visibilitychange',()=>{if(!document.hidden)start();});
})();
