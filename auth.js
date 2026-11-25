// TOPIC 2: login, register, forgot password, theme
// auth
let reg=false;$('#at').onclick=e=>{e.preventDefault();reg=!reg;['#rn','#rd'].forEach(s=>$(s).style.display=reg?'':'none');$('#ab').textContent=reg?'Register':'Login';$('#at').textContent=reg?'Back to login':'Create an account';$('#amode').textContent=reg?'Register as Faculty Member':'Sign in to continue'};
$('#ab').onclick=async()=>{try{await api(reg?'/api/register':'/api/login','POST',{name:$('#rn').value,email:$('#re').value,password:$('#rp').value,department:$('#rd').value});boot()}catch(e){tip(e)}};
$('#af').onclick=async e=>{e.preventDefault();const em=prompt('Your email:');if(!em)return;const r=await api('/api/forgot','POST',{email:em});alert(r.message);const t=prompt('Enter reset token (from server console):');if(!t)return;const p=prompt('New password (6+ chars):');try{await api('/api/reset','POST',{token:t,password:p});alert('Password updated')}catch(x){tip(x)}};
$('#lo').onclick=async()=>{await api('/api/logout','POST');location.reload()};
$('#tg').onclick=()=>$('#side').classList.toggle('c');
$('#th').onclick=()=>{const d=document.documentElement;d.dataset.theme=d.dataset.theme=='dark'?'':'dark';localStorage.t=d.dataset.theme};document.documentElement.dataset.theme=localStorage.t||'';
