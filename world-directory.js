/* Native front-page links first; search and filters enhance the same directory. */
(() => {
 'use strict';
 const root=document.getElementById('world-directory');if(!root)return;
 const search=document.getElementById('world-search'),cards=[...document.querySelectorAll('#world-links>a')];
 const buttons=[...root.querySelectorAll('[data-category]')].filter(el=>el.tagName==='BUTTON');
 const count=document.getElementById('world-count'),more=document.getElementById('world-more');
 let category='All',limit=18;
 const normalized=s=>s.normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
 const text=new Map(cards.map(card=>[card,normalized(card.textContent+' '+card.getAttribute('href'))]));
 function filter(){
  const words=normalized(search.value).trim().split(/\s+/).filter(Boolean);
  const matches=cards.filter(card=>(category==='All'||card.dataset.category===category)&&words.every(word=>text.get(card).includes(word)));
  const shown=new Set(matches.slice(0,limit));cards.forEach(card=>card.hidden=!shown.has(card));
  buttons.forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.category===category)));
  count.textContent=`Showing ${shown.size} of ${matches.length} ${category==='All'?'worlds & projects':category.toLowerCase()}${words.length?' matching your search':''}.`;
  document.getElementById('world-empty').hidden=matches.length!==0;more.hidden=matches.length<=limit;
  more.textContent=`Show ${Math.min(18,Math.max(0,matches.length-limit))} more worlds`;
 }
 buttons.forEach(button=>button.addEventListener('click',()=>{category=button.dataset.category;limit=18;filter();}));
 search.addEventListener('input',()=>{limit=18;filter();});
 document.getElementById('world-clear').addEventListener('click',()=>{search.value='';category='All';limit=18;filter();search.focus();});
 more.addEventListener('click',()=>{const oldVisible=cards.filter(c=>!c.hidden).length;limit+=18;filter();cards.filter(c=>!c.hidden)[oldVisible]?.focus();});
 filter();
})();
