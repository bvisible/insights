import{x as A,L as B,M as j,j as u,B as F,u as L,r as q,o,d as f,f as i,h as w,w as V,K as r,c as v,a6 as z,e as D,aA as _,J as b,F as I,g as P,t as U}from"./frappe-ui-8751eb88.js";import{S as Z}from"./search-4bcd879e.js";import{c as d}from"./index-eff4cfc7.js";/**
 * @license lucide-vue-next v0.484.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const $=d("arrow-down-a-z",[["path",{d:"m3 16 4 4 4-4",key:"1co6wj"}],["path",{d:"M7 20V4",key:"1yoxec"}],["path",{d:"M20 8h-5",key:"1vsyxs"}],["path",{d:"M15 10V6.5a2.5 2.5 0 0 1 5 0V10",key:"ag13bf"}],["path",{d:"M15 14h5l-5 6h5",key:"ur5jdg"}]]);/**
 * @license lucide-vue-next v0.484.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const E=d("arrow-up-a-z",[["path",{d:"m3 8 4-4 4 4",key:"11wl7u"}],["path",{d:"M7 4v16",key:"1glfcx"}],["path",{d:"M20 8h-5",key:"1vsyxs"}],["path",{d:"M15 10V6.5a2.5 2.5 0 0 1 5 0V10",key:"ag13bf"}],["path",{d:"M15 14h5l-5 6h5",key:"ur5jdg"}]]);/**
 * @license lucide-vue-next v0.484.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const H=d("square-check-big",[["path",{d:"M21 10.5V19a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h12.5",key:"1uzm8b"}],["path",{d:"m9 11 3 3L22 4",key:"1pflzl"}]]);/**
 * @license lucide-vue-next v0.484.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const J=d("square",[["rect",{width:"18",height:"18",x:"3",y:"3",rx:"2",key:"afitv7"}]]),K={class:"flex flex-col gap-2"},O={class:"flex items-center gap-2"},G=["title"],Q={class:"max-h-[10rem] overflow-y-scroll"},R=["onClick"],T={class:"flex-1 truncate"},ee=A({__name:"ColumnFilterValueSelector",props:B({valuesProvider:{type:Function}},{modelValue:{type:Array,default:()=>[]},modelModifiers:{}}),emits:["update:modelValue"],setup(g){const C=g,s=j(g,"modelValue"),y=u([]),m=u(""),h=u(!1),l=u("asc");F(()=>m.value,t=>{h.value=!0,C.valuesProvider(t).then(e=>y.value=e).finally(()=>h.value=!1)},{debounce:300,immediate:!0});const M=L(()=>{const t=[...y.value],e=l.value==="asc"?1:-1;return t.sort((p,a)=>{const n=String(p),c=String(a),x=Number(n),k=Number(c);return!isNaN(x)&&!isNaN(k)&&n.trim()&&c.trim()?(x-k)*e:n.toLowerCase().localeCompare(c.toLowerCase(),void 0,{numeric:!0})*e})});function S(t){s.value.includes(t)?s.value=s.value.filter(e=>e!==t):s.value=[...s.value,t]}function N(){l.value=l.value==="asc"?"desc":"asc"}return(t,e)=>{const p=q("FormControl");return o(),f("div",K,[i("div",O,[w(p,{placeholder:"Search",modelValue:m.value,"onUpdate:modelValue":e[0]||(e[0]=a=>m.value=a),autocomplete:"off",class:"flex-1"},{prefix:V(()=>[w(r(Z),{class:"h-4 w-4 text-gray-400"})]),suffix:V(()=>[h.value?(o(),v(r(z),{key:0,class:"h-4 w-4 text-gray-600"})):D("",!0)]),_:1},8,["modelValue"]),i("button",{onClick:_(N,["stop"]),class:"flex h-7 w-7 items-center justify-center rounded border border-gray-300 bg-white hover:bg-gray-50",title:l.value==="asc"?"Sort descending":"Sort ascending"},[(o(),v(b(l.value==="asc"?r($):r(E)),{class:"h-4 w-4"}))],8,G)]),i("div",Q,[(o(!0),f(I,null,P(M.value.slice(0,50),(a,n)=>(o(),f("div",{key:a||n,class:"flex cursor-pointer items-center justify-between gap-2 rounded px-1 py-1.5 text-base hover:bg-gray-100",onClick:_(c=>S(a),["prevent","stop"])},[(o(),v(b(s.value.includes(a)?r(H):r(J)),{class:"h-4 w-4 text-gray-600"})),i("span",T,U(a),1)],8,R))),128))])])}}});export{H as S,ee as _,J as a};
