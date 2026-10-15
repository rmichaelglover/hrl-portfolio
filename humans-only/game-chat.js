'use strict';
document.getElementById('game-room').addEventListener('change',event=>{
 document.getElementById('game-widget').src='index.html?widget=1&room='+encodeURIComponent(event.target.value);
});
