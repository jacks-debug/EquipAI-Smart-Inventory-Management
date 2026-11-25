// TOPIC 1: helpers (api, charts, permissions)
const $=s=>document.querySelector(s);let U,charts={};
const api=async(u,m='GET',b)=>{const r=await fetch(u,{method:m,headers:{'Content-Type':'application/json'},body:b?JSON.stringify(b):undefined});const j=await r.json().catch(()=>({}));if(!r.ok)throw new Error(j.error||'Error');return j};
const tip=e=>alert(e.message||e);const pill=t=>`<span class="pill ${t}">${t}</span>`;
const can=(...r)=>r.includes(U.role);const MG=['Super Admin','College Administrator','Department Head','Lab Assistant'],AP=MG.slice(0,3);
function chart(id,type,labels,data,label,multi){if(charts[id])charts[id].destroy();const c=['#2563EB','#06B6D4','#16A34A','#F59E0B','#EF4444','#8b5cf6','#14213D'];
 charts[id]=new Chart($('#'+id),{type,data:{labels,datasets:[{label,data,backgroundColor:multi?c:c[0]+'99',borderColor:multi?c:c[0],tension:.4,fill:type=='line'}]},options:{plugins:{legend:{display:!!multi&&type!='bar'}},maintainAspectRatio:false}})}
Chart.defaults.color='#94a3b8';Chart.defaults.font.family='Segoe UI,system-ui';
const countUp=()=>document.querySelectorAll('[data-n]').forEach(el=>{const n=+el.dataset.n;let i=0;const t=setInterval(()=>{i+=Math.max(1,n/30);if(i>=n){i=n;clearInterval(t)}el.textContent=Math.round(i)},25)});
