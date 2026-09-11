const API = window.CAMPUS_VOICE_API || (window.location.port === '8000' ? 'http://127.0.0.1:8001' : window.location.origin);
async function api(path){const r=await fetch(API+path);if(!r.ok)throw Error();return r.json()}
async function hydrate(){try{const d=await api('/api/dashboard');document.querySelectorAll('[data-count]').forEach(e=>e.textContent=d.total_complaints);document.querySelectorAll('[data-score]').forEach(e=>e.textContent=d.campus_score.toFixed(1));document.querySelectorAll('[data-level]').forEach(e=>e.textContent=d.level);document.querySelectorAll('[data-top]').forEach(e=>e.textContent=d.categories[0]?.name||'Awaiting signals')}catch(e){document.querySelectorAll('[data-count]').forEach(x=>x.textContent='—')}}
hydrate();
