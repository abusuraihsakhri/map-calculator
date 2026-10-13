"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const vm=require("node:vm");
const ids=["map-form","error","results","export","sbp","dbp","hr","icp",
  "map-value","pp-value","rpp-value","cpp-value","map-equation"];
const elements=Object.fromEntries(ids.map(id=>[id,{
  value:"",textContent:"",hidden:true,disabled:true,dataset:{label:id},
  handlers:{},addEventListener(name,fn){this.handlers[name]=fn;}
}]));
elements.sbp.value="120";elements.dbp.value="80";elements.hr.value="72";
const dom={getElementById(id){if(!(id in elements))throw new Error("Missing DOM id "+id);return elements[id];}};
vm.runInNewContext(fs.readFileSync("assets/app.js","utf8"),{
  document:dom, Number, Math, Error, String, URL:{}, Blob:class{},setTimeout
});
assert.equal(elements["map-value"].textContent,"93.3");
assert.equal(elements["pp-value"].textContent,"40.0");
assert.equal(elements["rpp-value"].textContent,"8640");
assert.equal(elements["cpp-value"].textContent,"—");
assert.equal(elements.results.hidden,false);
elements.sbp.value="70";
elements["map-form"].handlers.submit({preventDefault(){}});
assert.equal(elements.results.hidden,true);
assert.match(elements.error.textContent,/Diastolic pressure must be between/);
elements.sbp.value="120";elements.hr.value="";
elements["map-form"].handlers.submit({preventDefault(){}});
assert.equal(elements["rpp-value"].textContent,"—");
elements.icp.value="10";
elements["map-form"].handlers.submit({preventDefault(){}});
assert.equal(elements["cpp-value"].textContent,"83.3");
elements["map-form"].handlers.reset({preventDefault(){}});
assert.equal(elements.sbp.value,"");
assert.equal(elements.results.hidden,true);
console.log("Browser calculation smoke tests passed");
