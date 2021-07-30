/**
 * script pour rassembler des colonnes partageant le même en-tête
 **/


var t;            /* la table */
var headers;      /* les en-têtes */
var firstDataLine /* première ligne de données */
var uniqueHeaders = new Object();

function init(){
    t = document.querySelector("table");
    headers = document.querySelectorAll("th");
    headers.forEach(function(item, index){
	if (! (item.innerText in uniqueHeaders))
	    uniqueHeaders[item.innerText]=[item];
	else
	    uniqueHeaders[item.innerText].push(item);
    });
    firstDataLine = t.querySelector("td").parentElement;
    var tbody = t.firstElementChild;
    var newLine = document.createElement("tr");
    var repeat = 0;
    headers.forEach(function(item, index){
	var len = uniqueHeaders[item.innerText].length;
	if (repeat == 0) {
	    repeat = len;
	    var td = document.createElement("td");
	    var num = uniqueHeaders[item.innerText].indexOf(item);
	    td.setAttribute("colspan", len);
	    if (len == 1){
		td.innerText ="Hello " + len;
	    } else {
		td.innerText ="Collapse " + len;
	    }
	    newLine.append(td);
	    repeat -= 1;
	} else {
	    repeat -= 1;
	}
    });
    tbody.insertBefore(newLine, firstDataLine);
    console.log(firstDataLine);
    console.log(uniqueHeaders);
}

window.onload = init;
