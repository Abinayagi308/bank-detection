const $ = id => document.getElementById(id);
async function api(url,options){const r=await fetch(url,options);const d=await r.json();if(!r.ok)throw new Error(d.error||'Failed');return d;}
const post = (url,body)=>api(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
async function refresh(){try{const d=await api('/api/admin/tokens?bank='+encodeURIComponent($('bank').value));$('tokenList').replaceChildren();for(const t of d.tokens){const p=document.createElement('div');p.className='token';p.textContent=`#${t.id} — ${t.name} — ${t.service} — ${t.people} person(s) — ${t.status}`;$('tokenList').append(p);}}catch(e){$('adminMsg').textContent=e.message;}}
$('loginButton').onclick=async()=>{try{await post('/api/admin/login',{pin:$('pin').value});$('loginCard').classList.add('hidden');$('dashboard').classList.remove('hidden');refresh();}catch(e){$('loginMsg').textContent=e.message;}};
$('nextButton').onclick=async()=>{try{const d=await post('/api/admin/next',{bank:$('bank').value});$('adminMsg').textContent=d.serving_token?'Now serving #'+d.serving_token:'No waiting tokens';refresh();}catch(e){$('adminMsg').textContent=e.message;}};
$('bank').onchange=refresh;
$('logoutButton').onclick=async()=>{await post('/api/admin/logout',{});$('dashboard').classList.add('hidden');$('loginCard').classList.remove('hidden');};
setInterval(()=>{if(!$('dashboard').classList.contains('hidden'))refresh();},10000);
