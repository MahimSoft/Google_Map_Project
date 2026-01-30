$('#CodeHead').innerHTML = "Code for custom Fonts and CSS File:";

var divs=`<div class="b_fontNikosh2 text-black-50">জালালাবাদ গ্যাস টি এ্যান্ড ডি সিস্টেম লিঃ</div>
<div class="b_fontekush text-body">জালালাবাদ গ্যাস টি এ্যান্ড ডি সিস্টেম লিঃ</div>
<div class="b_fontkero text-danger">জালালাবাদ গ্যাস টি এ্যান্ড ডি সিস্টেম লিঃ</div>
<div class="b_fontmadon text-dark">জালালাবাদ গ্যাস টি এ্যান্ড ডি সিস্টেম লিঃ</div>
<div class="b_fontNikosh2 text-info">জালালাবাদ গ্যাস টি এ্যান্ড ডি সিস্টেম লিঃ</div>
<div class="b_fontpadmo bg-secondary text-light">জালালাবাদ গ্যাস টি এ্যান্ড ডি সিস্টেম লিঃ</div>
<div class="b_fontSejuti text-muted ">জালালাবাদ গ্যাস টি এ্যান্ড ডি সিস্টেম লিঃ</div>
<div id="digital7_01" class="digital7 text-primary text-break"></div>
<div id="digital7_02" class="digital7 text-danger text-break"></div>
<div class="b_fontpadmo text-secondary">জালালাবাদ গ্যাস টি এ্যান্ড ডি সিস্টেম লিঃ</div>
<div class="b_fontekush text-success">জালালাবাদ গ্যাস টি এ্যান্ড ডি সিস্টেম লিঃ</div>
<div class="b_fontkero text-warning">জালালাবাদ গ্যাস টি এ্যান্ড ডি সিস্টেম লিঃ</div>
<div class="b_fontmadon bg-warning text-dark">জালালাবাদ গ্যাস টি এ্যান্ড ডি সিস্টেম লিঃ</div>
<div class="b_fontNikosh2 bg-secondary text-white-50">জালালাবাদ গ্যাস টি এ্যান্ড ডি সিস্টেম লিঃ</div>
<div id="eidMubarak01" class="b_fonteid bg-dark text-warning text-break"></div>
<div id="eidMubarak02" class="b_fonteid text-secondary text-break"></div>`

var mainDiv=$('#demo')
mainDiv.className = ("fs-3");
mainDiv.innerHTML=divs;

$("#demo1").innerHTML=`<pre id="txtFormated" class="fs-6"></pre>`;
$("#txtFormated").innerHTML=  populateCode("./Fonts/fonts.js", '#txtFormated');

var AllChars1 = [];
for (var i=97; i<123; i++){
    AllChars1.push(String.fromCharCode(i));
    }

var AllChars2 = [];
for (var i=32; i<127; i++){
  AllChars2.push(String.fromCharCode(i));
    }

var AllChars3 = "";
for (var i=32; i<127; i++){
  AllChars3 += String.fromCharCode(i);
    }

var AllChars4 = "";
for (var i=97; i<123; i++){
    AllChars4 += String.fromCharCode(i);
    }

$("#digital7_01").innerHTML=AllChars3;
$("#digital7_02").innerHTML=AllChars4;
$("#eidMubarak01").innerHTML=AllChars3;
$("#eidMubarak02").innerHTML=AllChars4;