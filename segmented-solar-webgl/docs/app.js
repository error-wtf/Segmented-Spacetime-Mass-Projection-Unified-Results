import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import GUI from 'lil-gui';

/* ===========================================================
   1) Utility: Icosphere, LUTs, Bodies, Orbits
=========================================================== */
function buildIcosphere(radius=120, subdiv=5){
  // start icosahedron
  const t=(1+Math.sqrt(5))/2;
  let verts=[
    [-1, t, 0],[ 1, t, 0],[-1,-t, 0],[ 1,-t, 0],
    [ 0,-1, t],[ 0, 1, t],[ 0,-1,-t],[ 0, 1,-t],
    [ t, 0,-1],[ t, 0, 1],[-t, 0,-1],[-t, 0, 1]
  ].map(v=>new THREE.Vector3(...v));
  let faces=[
    [0,11,5],[0,5,1],[0,1,7],[0,7,10],[0,10,11],
    [1,5,9],[5,11,4],[11,10,2],[10,7,6],[7,1,8],
    [3,9,4],[3,4,2],[3,2,6],[3,6,8],[3,8,9],
    [4,9,5],[2,4,11],[6,2,10],[8,6,7],[9,8,1]
  ];

  function midpoint(i,j,cache){
    const key = i<j ? (i<<16)|j : (j<<16)|i;
    if(cache.has(key)) return cache.get(key);
    const v = new THREE.Vector3().addVectors(verts[i], verts[j]).multiplyScalar(0.5);
    const idx = verts.push(v)-1;
    cache.set(key, idx);
    return idx;
  }

  for(let s=0;s<subdiv;s++){
    const cache=new Map();
    const newFaces=[];
    for(const [a,b,c] of faces){
      const ab=midpoint(a,b,cache), bc=midpoint(b,c,cache), ca=midpoint(c,a,cache);
      newFaces.push([a,ab,ca],[b,bc,ab],[c,ca,bc],[ab,bc,ca]);
    }
    faces=newFaces;
  }

  // project to sphere
  for(const v of verts){ v.normalize().multiplyScalar(radius); }

  // build indexed geometry
  const pos = new Float32Array(verts.length*3);
  verts.forEach((v,i)=>{ pos[3*i]=v.x; pos[3*i+1]=v.y; pos[3*i+2]=v.z; });
  const idx = new Uint32Array(faces.length*3);
  faces.forEach((f,i)=>{ idx[3*i]=f[0]; idx[3*i+1]=f[1]; idx[3*i+2]=f[2]; });

  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos,3));
  geo.setIndex(new THREE.BufferAttribute(idx,1));
  geo.computeVertexNormals();
  return geo;
}

function makeOrbitPoints(rAU=1.0, segments=360){
  const pts = [];
  for(let i=0;i<segments;i++){
    const a = 2*Math.PI*i/(segments-1);
    pts.push(new THREE.Vector3(rAU*Math.cos(a), rAU*Math.sin(a), 0));
  }
  return pts;
}

// Palettes → 1D LUT (256×RGB) as Uint8Array
function lutGreys(){
  const data=new Uint8Array(256*3);
  for(let i=0;i<256;i++){ data[3*i]=data[3*i+1]=data[3*i+2]=i; }
  return data;
}
function lutStops(stops){ // stops: [{t,r,g,b},...]
  const data=new Uint8Array(256*3);
  for(let i=0;i<256;i++){
    const t=i/255;
    let s0=stops[0], s1=stops[stops.length-1];
    for(let j=0;j<stops.length-1;j++){ if(t>=stops[j].t && t<=stops[j+1].t){ s0=stops[j]; s1=stops[j+1]; break; } }
    const u=(t-s0.t)/Math.max(1e-9,(s1.t-s0.t));
    const r=Math.round(s0.r + u*(s1.r-s0.r));
    const g=Math.round(s0.g + u*(s1.g-s0.g));
    const b=Math.round(s0.b + u*(s1.b-s0.b));
    data[3*i]=r; data[3*i+1]=g; data[3*i+2]=b;
  }
  return data;
}
function lutViridis(){
  return lutStops([
    {t:0.00,r:68,g:1,b:84},{t:0.25,r:58,g:82,b:139},{t:0.50,r:32,g:144,b:140},
    {t:0.75,r:94,g:201,b:97},{t:1.00,r:253,g:231,b:37}
  ]);
}
function lutPlasma(){
  return lutStops([
    {t:0.00,r:13,g:8,b:135},{t:0.25,r:126,g:3,b:168},{t:0.50,r:203,g:71,b:119},
    {t:0.75,r:248,g:149,b:64},{t:1.00,r:240,g:249,b:33}
  ]);
}
// Compact Turbo poly fit (approx) → bake to LUT
function lutTurbo(){
  const data=new Uint8Array(256*3);
  for(let i=0;i<256;i++){
    const t=i/255;
    const r = 34.61 + t*(1172.33 + t*(-10793.56 + t*(33300.12 + t*(-38394.49 + t*15054.07))));
    const g = 23.31 + t*(557.33  + t*(1225.33  + t*(-3574.69  + t*(4772.99   + t*(-2110.90)))));
    const b = 27.2  + t*(321.89  + t*(1517.40  + t*(-4642.37  + t*(5930.97   + t*(-2586.66)))));
    data[3*i]  = Math.min(255,Math.max(0, Math.round(r)));
    data[3*i+1]= Math.min(255,Math.max(0, Math.round(g)));
    data[3*i+2]= Math.min(255,Math.max(0, Math.round(b)));
  }
  return data;
}

/* ===========================================================
   2) Scene Basics
=========================================================== */
const app = document.getElementById('app');
const renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setClearColor(0x0a0a0c);
app.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0a0a0c);

const camera = new THREE.PerspectiveCamera(45, innerWidth/innerHeight, 0.01, 5000);
camera.position.set(0, 220, 420);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;

/* ===========================================================
   3) Shader Material (GPU: compute N, τ, n per-vertex)
=========================================================== */
const MAX_BODIES = 16;

// Bodies UBO replacement via flat uniforms
const bodies = []; // {name, pos:THREE.Vector3, Mscale, gamma, r0, rNb, dNb}
function addBody(name, x,y,z, Mscale, gamma, r0, rNb, dNb){
  bodies.push({name, pos:new THREE.Vector3(x,y,z), Mscale, gamma, r0, rNb, dNb});
}
addBody('Sun',     0,0,0,    1.0,      1.0, 0.005, 0.025, 0.005);
addBody('Mercury', 0.39,0,0, 1.65e-7,  1.0, 0.0002,0.001, 0.0002);
addBody('Venus',   0.72,0,0, 2.45e-6,  1.0, 0.0006,0.002, 0.0004);
addBody('Earth',   1.0,0,0,  3.00e-6,  1.0, 0.0006,0.002, 0.0004);
addBody('Mars',    1.52,0,0, 3.23e-7,  1.0, 0.0004,0.0015,0.0003);
addBody('Jupiter', 5.2,0,0,  9.54e-4,  1.0, 0.0005,0.003, 0.0006);
addBody('Saturn',  9.58,0,0, 2.86e-4,  1.0, 0.0005,0.003, 0.0006);

const bodyUniforms = {
  count: { value: bodies.length },
  pos:   { value: new Array(MAX_BODIES).fill(0).map(()=>new THREE.Vector3()) },
  M:     { value: new Float32Array(MAX_BODIES).fill(0) },
  gamma: { value: new Float32Array(MAX_BODIES).fill(0) },
  r0:    { value: new Float32Array(MAX_BODIES).fill(0) },
  rNb:   { value: new Float32Array(MAX_BODIES).fill(0) },
  dNb:   { value: new Float32Array(MAX_BODIES).fill(0) },
};
bodies.forEach((b,i)=>{
  bodyUniforms.pos.value[i].copy(b.pos);
  bodyUniforms.M.value[i]=b.Mscale;
  bodyUniforms.gamma.value[i]=b.gamma;
  bodyUniforms.r0.value[i]=b.r0;
  bodyUniforms.rNb.value[i]=b.rNb;
  bodyUniforms.dNb.value[i]=b.dNb;
});

// Global params
const params = {
  phi: (1+Math.sqrt(5))/2,
  alpha: 1.0,
  kappa: 0.015,
  p: 2.0,
  Nbg: 0.0,
  Nmax: 5.0,
  colorMode: 'N',  // 'N' | 'TAU' | 'NIDX'
  palette: 'Turbo', // 'Turbo' | 'Viridis' | 'Plasma' | 'Greys'
  wireframe: false,
  showBodies: true,
  showOrbits: true
};

// LUT texture
function makeLUTTexture(name){
  let data;
  if(name==='Viridis') data = lutViridis();
  else if(name==='Plasma') data = lutPlasma();
  else if(name==='Greys') data = lutGreys();
  else data = lutTurbo();
  const tex = new THREE.DataTexture(data, 256,1, THREE.RGBFormat);
  tex.needsUpdate = true;
  tex.magFilter = THREE.LinearFilter;
  tex.minFilter = THREE.LinearFilter;
  tex.generateMipmaps = false;
  return tex;
}
let lutTex = makeLUTTexture(params.palette);

// Legend draw
const legendCanvas = document.getElementById('legendCanvas');
const legendCtx = legendCanvas.getContext('2d');
function drawLegend(){
  const img = legendCtx.createImageData(256,1);
  const src = lutTex.image.data;
  for(let i=0;i<256;i++){
    img.data[4*i]=src[3*i]; img.data[4*i+1]=src[3*i+1]; img.data[4*i+2]=src[3*i+2]; img.data[4*i+3]=255;
  }
  legendCtx.putImageData(img,0,0);
  document.getElementById('legendLabel').textContent = `Color: ${
    params.colorMode==='N' ? 'N(x) - Segment Density' : 
    (params.colorMode==='TAU' ? 'τ(x) - Time Dilation' : 'n(x) - Refractive Index')
  }`;
}
drawLegend();

// Shaders
const vert = /* glsl */`
uniform int uBodyCount;
uniform vec3 uPos[${MAX_BODIES}];
uniform float uM[${MAX_BODIES}];
uniform float uGamma[${MAX_BODIES}];
uniform float uR0[${MAX_BODIES}];
uniform float uRNb[${MAX_BODIES}];
uniform float uDNb[${MAX_BODIES}];

uniform float uP;     // kernel falloff p
uniform float uNbg;   // background N
uniform float uNmax;  // clamp
uniform float uPhi;   // golden ratio
uniform float uAlpha; // τ scaling
uniform float uKappa; // n scaling
uniform int   uColorMode; // 0=N,1=TAU,2=NIDX

varying float vScalar;

float logistic(float x){ return 1.0 / (1.0 + exp(-x)); }

void main(){
  // position in AU
  vec3 P = position;
  float N = uNbg;

  for(int i=0;i<${MAX_BODIES};i++){
    if(i>=uBodyCount) break;
    float r = length(P - uPos[i]);
    float k = (uM[i] / pow(r + uR0[i], uP)) * logistic((uRNb[i] - r)/uDNb[i]);
    N += uGamma[i] * k;
  }
  N = clamp(N, 0.0, uNmax);

  float TAU = pow(uPhi, -uAlpha * N);
  float NIDX = 1.0 + uKappa * N;

  if(uColorMode==0) vScalar = N;
  else if(uColorMode==1) vScalar = TAU;
  else vScalar = NIDX;

  gl_Position = projectionMatrix * modelViewMatrix * vec4(P, 1.0);
}
`;

const frag = /* glsl */`
precision highp float;
uniform sampler2D uLUT;
uniform vec2 uRange; // min,max of current scalar
varying float vScalar;

void main(){
  float t = (vScalar - uRange.x) / max(1e-9, (uRange.y - uRange.x));
  t = clamp(t, 0.0, 1.0);
  vec3 rgb = texture2D(uLUT, vec2(t, 0.5)).rgb;
  gl_FragColor = vec4(rgb, 0.78);
}
`;

// Geometry & material
const geo = buildIcosphere(120, 5);
const mat = new THREE.ShaderMaterial({
  vertexShader: vert,
  fragmentShader: frag,
  transparent: true,
  uniforms: {
    uBodyCount: { value: bodyUniforms.count.value },
    uPos:   { value: bodyUniforms.pos.value },
    uM:     { value: bodyUniforms.M.value },
    uGamma: { value: bodyUniforms.gamma.value },
    uR0:    { value: bodyUniforms.r0.value },
    uRNb:   { value: bodyUniforms.rNb.value },
    uDNb:   { value: bodyUniforms.dNb.value },
    uP:     { value: params.p },
    uNbg:   { value: params.Nbg },
    uNmax:  { value: params.Nmax },
    uPhi:   { value: params.phi },
    uAlpha: { value: params.alpha },
    uKappa: { value: params.kappa },
    uColorMode: { value: 0 }, // 0=N 1=TAU 2=NIDX
    uLUT: { value: lutTex },
    uRange: { value: new THREE.Vector2(0,1) } // min/max scalar (updated below)
  },
  side: THREE.DoubleSide,
  wireframe: false
});

const mesh = new THREE.Mesh(geo, mat);
scene.add(mesh);

// Simple min/max probe on CPU: sample few vertices each frame (fast)
function estimateScalarRange(){
  // Heuristic range per mode:
  let min, max;
  if(params.colorMode==='N'){ 
    min=0.0; max=params.Nmax; 
  }
  else if(params.colorMode==='TAU'){ 
    min=Math.pow(params.phi, -params.alpha*params.Nmax); max=1.0; 
  }
  else { 
    min=1.0; max=1.0 + params.kappa*params.Nmax; 
  }

  mat.uniforms.uRange.value.set(min,max);
}
estimateScalarRange();

// Orbits (lines) & body spheres
const orbitGroup = new THREE.Group();
const bodyGroup = new THREE.Group();
scene.add(orbitGroup);
scene.add(bodyGroup);

const orbitDefs = [
  { name:'Mercury', r:0.39, color:0x8888aa },
  { name:'Venus',   r:0.72, color:0x8888aa },
  { name:'Earth',   r:1.00, color:0x88aadd },
  { name:'Mars',    r:1.52, color:0xaa8877 },
  { name:'Jupiter', r:5.20, color:0xccaa88 },
  { name:'Saturn',  r:9.58, color:0xccaacc }
];

for(const o of orbitDefs){
  const pts = makeOrbitPoints(o.r, 512);
  const geoL = new THREE.BufferGeometry().setFromPoints(pts);
  const line = new THREE.LineLoop(geoL, new THREE.LineBasicMaterial({
    color:o.color, 
    opacity:0.4, 
    transparent:true
  }));
  orbitGroup.add(line);
}

function addPlanetDot(b, color){
  const size = b.name==='Sun' ? 0.15 : (b.name==='Jupiter' ? 0.06 : 0.03);
  const m = new THREE.Mesh(
    new THREE.SphereGeometry(size, 16, 16),
    new THREE.MeshBasicMaterial({color, transparent:true, opacity:0.9})
  );
  m.position.copy(b.pos);
  m.userData = {name: b.name};
  bodyGroup.add(m);
}

addPlanetDot(bodies[0], 0xffd878); // Sun
['Mercury','Venus','Earth','Mars','Jupiter','Saturn'].forEach(n=>{
  const b = bodies.find(x=>x.name===n); 
  if(!b) return;
  addPlanetDot(b, 0xf0ead2);
});

/* ===========================================================
   4) GUI Controls
=========================================================== */
const gui = new GUI({title:'🌌 Segmented Spacetime'});

const F = gui.addFolder('⚙️ Field Parameters');
F.add(params, 'alpha', 0.1, 3.0, 0.05).name('α (time dilation)').onChange(v=>{
  mat.uniforms.uAlpha.value=v; 
  estimateScalarRange(); 
  drawLegend(); 
});
F.add(params, 'kappa', 0.0, 0.05, 0.001).name('κ (refractive index)').onChange(v=>{
  mat.uniforms.uKappa.value=v; 
  estimateScalarRange(); 
  drawLegend(); 
});
F.add(params, 'p', 1.2, 3.0, 0.05).name('p (kernel falloff)').onChange(v=>{
  mat.uniforms.uP.value=v; 
});
F.add(params, 'Nmax', 1.0, 10.0, 0.2).name('N_max (saturation)').onChange(v=>{
  mat.uniforms.uNmax.value=v; 
  estimateScalarRange(); 
  drawLegend(); 
});
F.add(params, 'Nbg', 0.0, 2.0, 0.05).name('N_bg (background)').onChange(v=>{
  mat.uniforms.uNbg.value=v; 
  estimateScalarRange(); 
});
F.open();

const C = gui.addFolder('🎨 Visualization');
C.add(params, 'colorMode', { 
  'N(x) - Segment Density': 'N', 
  'τ(x) - Time Dilation': 'TAU', 
  'n(x) - Refractive Index': 'NIDX' 
}).name('Field Mode').onChange(v=>{
  mat.uniforms.uColorMode.value = (v==='N')?0:((v==='TAU')?1:2);
  estimateScalarRange(); 
  drawLegend();
});
C.add(params, 'palette', ['Turbo','Viridis','Plasma','Greys']).name('Color Palette').onChange(v=>{
  lutTex.dispose();
  lutTex = makeLUTTexture(v);
  mat.uniforms.uLUT.value = lutTex;
  drawLegend();
});
C.add(params, 'wireframe').name('Wireframe Mode').onChange(v=>{
  mat.wireframe = v;
});
C.add(params, 'showBodies').name('Show Bodies').onChange(v=>{
  bodyGroup.visible = v;
});
C.add(params, 'showOrbits').name('Show Orbits').onChange(v=>{
  orbitGroup.visible = v;
});
C.add({screenshot:()=>savePNG()}, 'screenshot').name('📸 Screenshot PNG');
C.open();

const I = gui.addFolder('ℹ️ Info');
I.add({vertices: geo.attributes.position.count}, 'vertices').name('Mesh Vertices').disable();
I.add({faces: geo.index.count/3}, 'faces').name('Mesh Faces').disable();
I.add({phi: params.phi.toFixed(6)}, 'phi').name('φ (Golden Ratio)').disable();

function savePNG(){
  renderer.render(scene,camera);
  const a=document.createElement('a');
  a.href=renderer.domElement.toDataURL('image/png');
  a.download='segmented_spacetime_webgl.png';
  a.click();
  console.log('📸 Screenshot saved: segmented_spacetime_webgl.png');
}

/* ===========================================================
   5) Resize + Animate
=========================================================== */
addEventListener('resize', ()=>{
  renderer.setSize(innerWidth, innerHeight);
  camera.aspect = innerWidth/innerHeight;
  camera.updateProjectionMatrix();
});

function loop(){
  controls.update();
  renderer.render(scene,camera);
  requestAnimationFrame(loop);
}

// Start the application
console.log('🌌 Segmented Spacetime WebGL initialized');
console.log(`📊 Mesh: ${geo.attributes.position.count} vertices, ${geo.index.count/3} faces`);
console.log(`⚙️ Bodies: ${bodies.length} gravitational sources`);
console.log(`🎨 Palette: ${params.palette} (${lutTex.image.data.length/3} colors)`);

loop();
