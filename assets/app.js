"use strict";
(function(){
  const form=document.getElementById("map-form");
  const error=document.getElementById("error");
  const output=document.getElementById("results");
  const exportButton=document.getElementById("export");
  let latest=null;

  function read(name,required){
    const input=document.getElementById(name);
    const raw=input.value.trim();
    if(!raw){
      if(required) throw new Error(input.dataset.label+" is required.");
      return null;
    }
    const value=Number(raw);
    if(!Number.isFinite(value)) throw new Error(input.dataset.label+" must be a finite number.");
    return value;
  }
  function calculate(sbp,dbp,hr,icp){
    if(sbp<=0) throw new Error("Systolic pressure must be greater than zero.");
    if(dbp<0||dbp>sbp) throw new Error("Diastolic pressure must be between 0 and systolic pressure.");
    if(hr!==null&&hr<=0) throw new Error("Heart rate must be greater than zero.");
    if(icp!==null&&icp<0) throw new Error("Intracranial pressure cannot be negative.");
    const map=dbp+(sbp-dbp)/3;
    const pp=sbp-dbp;
    const rpp=hr===null?null:hr*sbp;
    const cpp=icp===null?null:map-icp;
    if([map,pp,rpp,cpp].some(value=>value!==null&&!Number.isFinite(value))) {
      throw new Error("Measurements produce values outside the numeric range.");
    }
    return {sbp,dbp,hr,icp,map,pp,rpp,cpp};
  }
  function fmt(value){return value===null?"—":value.toFixed(1);}
  function show(result){
    document.getElementById("map-value").textContent=fmt(result.map);
    document.getElementById("pp-value").textContent=fmt(result.pp);
    document.getElementById("rpp-value").textContent=result.rpp===null?"—":result.rpp.toFixed(0);
    document.getElementById("cpp-value").textContent=fmt(result.cpp);
    document.getElementById("map-equation").textContent="MAP = "+fmt(result.dbp)+" + ("+fmt(result.sbp)+" − "+fmt(result.dbp)+") / 3";
    output.hidden=false;
    exportButton.disabled=false;
  }
  function update(){
    try{
      const result=calculate(read("sbp",true),read("dbp",true),read("hr",false),read("icp",false));
      latest=result; error.textContent=""; show(result);
    }catch(err){
      latest=null;output.hidden=true;exportButton.disabled=true;
      error.textContent=err.message;
    }
  }
  form.addEventListener("submit",function(event){event.preventDefault();update();});
  form.addEventListener("reset",function(event){
    event.preventDefault();
    ["sbp","dbp","hr","icp"].forEach(name=>{document.getElementById(name).value="";});
    latest=null;error.textContent="";output.hidden=true;exportButton.disabled=true;
  });
  exportButton.addEventListener("click",function(){
    if(!latest)return;
    const header=["sbp","dbp","hr","icp","map_mmhg","pulse_pressure_mmhg","rpp","cpp_mmhg"];
    const values=[latest.sbp,latest.dbp,latest.hr,latest.icp,latest.map,latest.pp,latest.rpp,latest.cpp];
    const contents=header.join(",")+"\r\n"+values.map(v=>v===null?"":String(Math.round(v*100)/100)).join(",")+"\r\n";
    const url=URL.createObjectURL(new Blob([contents],{type:"text/csv;charset=utf-8"}));
    const link=document.createElement("a");
    link.href=url;link.download="map-calculation.csv";document.body.append(link);link.click();link.remove();
    setTimeout(function(){URL.revokeObjectURL(url);},1000);
  });
  update();
})();
