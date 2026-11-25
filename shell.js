// TOPIC 8: app shell, sidebar navigation, router
const VIEWS={dashboard:['📊','Dashboard'],equipment:['🖥️','Equipment'],requests:['🔁','Issue & Return'],ai:['🧠','AI Insights'],alerts:['🔔','Smart Alerts'],chat:['💬','EquipAI Assistant'],users:['👥','Users'],profile:['👤','Profile']};
async function boot(){try{U=await api('/api/me')}catch{return}$('#auth').style.display='none';$('#app').style.display='block';$('#who').textContent=`${U.name} · ${U.role}`;
 $('#nav').innerHTML=Object.entries(VIEWS).filter(([k])=>k!='users'||can('Super Admin','College Administrator')).map(([k,[i,t]])=>`<div class="nav" data-v="${k}">${i} <span class="t">${t}</span></div>`).join('');
 document.querySelectorAll('.nav').forEach(n=>n.onclick=()=>go(n.dataset.v));go('dashboard')}
async function go(v){document.querySelectorAll('.nav').forEach(n=>n.classList.toggle('on',n.dataset.v==v));$('#title').textContent=VIEWS[v][1];$('#view').innerHTML='Loading…';try{await R[v]()}catch(e){tip(e)}}
const R={};
