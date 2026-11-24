const steps=[...document.querySelectorAll('.step')]
function show(n){steps.forEach(s=>s.classList.toggle('active',s.dataset.step===String(n)))}
document.querySelectorAll('.next').forEach(b=>b.onclick=()=>{
 const current=b.closest('.step');const inputs=[...current.querySelectorAll('[required]')];
 if(!inputs.every(i=>i.value.trim() && i.checkValidity())){alert('Please complete all required fields.');return}
 show(Number(current.dataset.step)+1);if(current.dataset.step==='2') renderReview()
})
document.querySelectorAll('.back').forEach(b=>b.onclick=()=>show(Number(b.closest('.step').dataset.step)-1))
function renderReview(){const fd=new FormData(document.querySelector('form'));document.querySelector('#review').innerHTML='<dl>'+[...fd.entries()].map(([k,v])=>`<dt>${k.replace('_',' ')}</dt><dd>${v}</dd>`).join('')+'</dl>'}
