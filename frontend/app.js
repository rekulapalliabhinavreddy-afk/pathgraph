const API_BASE = 'http://127.0.0.1:8000';
const state = { roles: [], skills: [], role: 'machine-learning-engineer', selected: ['python','sql','git'], profile: null, graph: null, view: 'explore', working: false, error: '' };
const app = document.getElementById('app');

async function request(path, options={}) {
  const res = await fetch(API_BASE + path, {headers:{'Content-Type':'application/json'}, ...options});
  const data = await res.json().catch(()=>({}));
  if (!res.ok) throw new Error(data.detail || 'Something went wrong.');
  return data;
}
const esc = (s='') => String(s).replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));

async function boot(){
  try { [state.roles,state.skills] = await Promise.all([request('/api/roles'),request('/api/skills')]); render(); }
  catch(e){ state.error=e.message; render(); }
}
function render(){
  app.innerHTML = `
  <div class="app-shell">
    <header class="topbar">
      <div class="brand"><div class="brand-mark">P</div><div><strong>PathGraph</strong><span>Career intelligence</span></div></div>
      <nav>${nav('explore','Explore')}${nav('path','My Path')}${nav('graph','Graph')}</nav>
      <div class="status"><i></i> CognoDB connected</div>
    </header>
    ${state.error ? `<div class="error-banner"><span>⚠</span>${esc(state.error)}<button onclick="clearError()">Dismiss</button></div>`:''}
    <main>${viewHtml()}</main><footer>PathGraph · Graph-native career exploration · CognoDB + official Neo4j driver</footer>
  </div>`;
}
function nav(id,label){ return `<button class="nav ${state.view===id?'active':''}" ${(!state.profile&&id==='path')||(!state.graph&&id==='graph')?'disabled':''} onclick="setView('${id}')">${label}</button>`; }
function viewHtml(){
  if(state.view==='path'&&state.profile) return pathView();
  if(state.view==='graph'&&state.graph) return graphView();
  return exploreView();
}
function exploreView(){
  return `<section class="hero-wrap">
    <div class="hero-copy"><div class="eyebrow">CAREER GRAPH <span>•</span> RELATIONSHIP INTELLIGENCE</div>
      <h1>Find the skills<br><em>between</em> you and your next role.</h1>
      <p>Map your current skills against a target role and uncover the technologies, adjacent roles and missing capabilities connected through the graph.</p>
      <div class="hero-pills"><span>Graph-native</span><span>Multi-hop</span><span>Explainable</span></div>
    </div>
    <div class="panel explorer-panel"><div class="panel-label">01 · TARGET ROLE</div><label>Select the role you're aiming for</label>
      <select onchange="state.role=this.value">${state.roles.map(r=>`<option value="${esc(r.slug)}" ${r.slug===state.role?'selected':''}>${esc(r.name)}</option>`).join('')}</select>
      <div class="panel-label skill-label">02 · YOUR CURRENT SKILLS</div><label>Pick everything you already know</label>
      <div class="skill-grid">${state.skills.map(s=>`<button class="skill ${state.selected.includes(s.slug)?'selected':''}" onclick="toggleSkill('${esc(s.slug)}')">${state.selected.includes(s.slug)?'✓':'+'} ${esc(s.name)}</button>`).join('')}</div>
      <button class="primary" onclick="analyze()" ${state.working?'disabled':''}>${state.working?'Analyzing the graph…':'Build my career path →'}</button>
      <div class="tiny-note">${state.selected.length} skills selected · Relationship traversal finds the gaps</div>
    </div></section>`;
}
function pathView(){ const p=state.profile; return `<section class="content-wrap">
  <div class="section-head"><div><div class="eyebrow">YOUR CAREER PATH</div><h2>${esc(p.role_name)}</h2><p>${esc(p.description)}</p></div><button class="outline" onclick="showGraph()">Explore graph ↗</button></div>
  <div class="metrics"><div class="metric"><strong>${p.score}%</strong><span>Skill match</span></div><div class="metric"><strong>${p.missing_skills.length}</strong><span>Skills to build</span></div><div class="metric"><strong>${p.related_roles.length}</strong><span>Adjacent roles</span></div></div>
  <div class="two-col"><div class="panel result-panel"><div class="panel-label">SKILL GAP</div><h3>What gets you there?</h3><div class="progress"><span style="width:${p.score}%"></span></div>
    <div class="skill-results">${p.skills.map(s=>`<div class="result ${s.matched?'matched':''}"><span>${s.matched?'✓':'→'}</span><div><strong>${esc(s.name)}</strong><small>${esc(s.category)}</small></div><b>${s.matched?'You have it':'Build this'}</b></div>`).join('')}</div></div>
  <div class="panel"><div class="panel-label">CONNECTED OPPORTUNITIES</div><h3>Where the graph leads</h3><div class="related-list">${p.related_roles.map(r=>`<div class="related"><div class="role-icon">${esc(r.name.charAt(0))}</div><div><strong>${esc(r.name)}</strong><small>${esc(r.category)} · ${r.shared_skills} shared skills</small></div><span>→</span></div>`).join('')}</div>
  <div class="techs"><span>RECOMMENDED TECHNOLOGIES</span>${p.technologies.map(t=>`<i>${esc(t.name)}</i>`).join('')}</div></div></div></section>`; }
function graphView(){
  const nodes=state.graph.nodes.slice(0,24), center=nodes.find(n=>n.slug===state.role)||nodes[0], others=nodes.filter(n=>n.slug!==center?.slug);
  const cx=500,cy=310,rx=350,ry=220;
  const pos=others.map((n,i)=>({...n,x:cx+rx*Math.cos(i*2*Math.PI/Math.max(1,others.length)-Math.PI/2),y:cy+ry*Math.sin(i*2*Math.PI/Math.max(1,others.length)-Math.PI/2)}));
  return `<section class="content-wrap"><div class="section-head"><div><div class="eyebrow">GRAPH EXPLORER</div><h2>See the relationships.</h2><p>A bounded two-hop neighborhood around your target role. The edges below are stored as typed graph relationships in CognoDB.</p></div></div>
  <div class="graph-panel"><svg viewBox="0 0 1000 620" preserveAspectRatio="xMidYMid meet">
  ${pos.map(n=>`<line x1="500" y1="310" x2="${n.x}" y2="${n.y}" class="edge"/>`).join('')}
  <g transform="translate(500 310)"><circle r="72" class="center-node"/><text text-anchor="middle" dy="-4" class="center-text">${esc(center?.name||'Role')}</text><text text-anchor="middle" dy="18" class="node-type">ROLE</text></g>
  ${pos.map(n=>`<g transform="translate(${n.x} ${n.y})"><circle r="48" class="node ${n.type==='Skill'?'skill-node':'tech-node'}"/><text text-anchor="middle" dy="-2" class="node-text">${esc(n.name.length>17?n.name.slice(0,16)+'…':n.name)}</text><text text-anchor="middle" dy="16" class="node-type">${esc(n.type.toUpperCase())}</text></g>`).join('')}</svg>
  <div class="legend"><span><i class="dot role-dot"></i>Role</span><span><i class="dot skill-dot"></i>Skill</span><span><i class="dot tech-dot"></i>Technology</span><span class="graph-note">${nodes.length} nodes · traversal depth ≤ 2</span></div></div></section>`;
}
window.toggleSkill = slug => { state.selected=state.selected.includes(slug)?state.selected.filter(x=>x!==slug):[...state.selected,slug]; render(); };
window.setView = view => { state.view=view; state.error=''; render(); };
window.showGraph = async () => {
  state.working = true;
  state.error = '';
  render();

  try {
    const data = await request(
      '/api/graph/' + encodeURIComponent(state.role)
    );

    const roleName =
      state.profile?.role_name |
      state.profile?.role ||
      state.role;

    const skills = Array.isArray(data) ? data : (data.nodes || []);

    state.graph = {
      nodes: [
        {
          slug: state.role,
          name: roleName,
          type: 'role'
        },
        ...skills.map(s => ({
          slug: s.slug,
          name: s.name,
          type: 'skill',
          category: s.category
        }))
      ],
      edges: []
    };

    state.view = 'graph';
  } catch (e) {
    console.error('GRAPH ERROR:', e);
    state.error = 'Unable to load graph neighborhood.';
  } finally {
    state.working = false;
    render();
  }
};
window.clearError = () => { state.error=''; render(); };
window.analyze = async () => { state.working=true; state.error=''; render(); try { state.profile=await request('/api/profile',{method:'POST',body:JSON.stringify({role_slug:state.role,current_skills:state.selected})}); state.graph=await request('/api/graph/'+encodeURIComponent(state.role)); state.view='path'; } catch(e){state.error=e.message;} finally{state.working=false;render();} };
boot();
