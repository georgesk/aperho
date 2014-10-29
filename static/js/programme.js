 $(function() { /* fonction déclenchée au démarrage d'une page */
     $( "#tabs" ).tabs(); /* activation des onglets s'il y en a */
});

/**
 * Supprime les groupes de la session, permet de recommencer avec d'autres
 **/
function reset(){
    var form=$("<form>",{
	method: "post", 
	action: "index",
	id: "resetForm",
    });
    form.append($("<input>",{type: "hidden", name: "call", value: "reset"}));
    form.append($("<p>").text("Confirmez bien que vous voulez recommencer à zéro !"));
    var dialog=$("<div>");
    $("body").append(dialog);
    dialog.append(form);
    dialog.dialog({
	title: "Dernière chance avant la remise à zéro", 
	modal: true,
	buttons: [
	    {text: "Échappement", 
	     click: function(){$( this ).dialog( "close" );}
	    },
	    {text: "OK", 
	     click :function(){$("#resetForm").submit();}
	    },
	],
    });
}

/**
 * supprime un élève d'un groupe et rappelant la page 
 * avec des paramètres ad hoc
 * @param e l'identifiant numérique d'un élève
 * @param i le numéro du groupe où il est
 **/
function supprimeEleve(e, i){
    if (i > 0){
	/* quand un élève est inscrit dans un groupe, alors il ne sera */
	/* pas supprimé, mais déplacé dans le groupe des non-inscrits  */
	var form=$("<form>",{method: "post", action: "index#tabs-"+i, style: "display: none;"});
	form.append($("<input>",{name: "eleveId", value: e}));
	form.append($("<input>",{name: "groupe", value: i}));
	form.append($("<input>",{name: "call", value: "delete"}));
	$("body").append(form);
	form.submit();
    } else {
	/* si l'élève est non-inscrit, un garde-fou est nécessaire */
	var form=$("<form>",{method: "post", 
			     action: "index#tabs-0",
			     id: "supprimeForm"
			    });
	form.append($("<input>",{type: "hidden", name: "eleveId", value: e}));
	form.append($("<input>",{type: "hidden", name: "groupe", value: i}));
	form.append($("<input>",{type: "hidden", name: "call", value: "delete"}));
	form.append($("<p>").text("Veuillez confirmer l'effacement définitif"))
    var dialog=$("<div>");
	$("body").append(dialog);
	dialog.append(form);
	dialog.dialog({
	    title: "Dernière chance avant l'effacement", 
	    modal: true,
	    buttons: [
		{text: "Échappement", 
		 click: function(){$( this ).dialog( "close" );}
		},
		{text: "OK", 
		 click :function(){$("#supprimeForm").submit();}
		},
	    ],
	});
    }
}

/**
 * supprime un élève d'un groupe et rappelant la page 
 * avec des paramètres ad hoc
 * @param e l'identifiant numérique d'un élève
 * @param i le numéro du groupe où il est
 * @param max le numéro maxi du groupe d'AP possible
 * @param nom nom de l'élève
 * @param titres liste des titres des groupes
 **/
function deplaceEleve(e, i, max, nom, titres){
    var form=$("<form>",{method: "post", action: "index#tabs-"+i,});
    form.append($("<input>",{type: "hidden", name: "eleveId", value: e}));
    form.append($("<input>",{type: "hidden", name: "groupe", value: i}));
    var select=$("<select>",{name: "dest", size: max});
    for (var j=0; j < max+1; j++){
	if (parseInt(j) != parseInt(i)){
	    var option=$("<option>",{value: j});
	    if (j==0) option.text("non inscrits");
	    else option.text(""+j+" - "+titres[j]);
	    select.append(option);
	}
    }
    form.append($("<p>").text("Déplacer "+nom+" vers le groupe : "));
    form.append(select);
    form.append($("<br>"));
    form.append($("<input>",{type: "hidden", name: "call", value: "change"}));
    form.append($("<input>",{type: "submit", value: "OK"}));
    var dialog=$("<div>");
    dialog.append(form);
    $("body").append(dialog);
    dialog.dialog({title: "Choisir le groupe d'arrivée", modal: true, width: 800});
}

/**
 * crée un nouvel élève et le place dans le groupe des non-inscrits
 **/
function creeEleve(){
    var form=$("<form>",{method: "post", action: "index#tabs-0",});
    var table=$("<table>");
    var tr=$("<tr>"); table.append(tr);
    var td=$("<td>").text("Nom"); tr.append(td);
    td=$("<td>").append($("<input>",{type: "text", name: "nom"})); tr.append(td);
    tr=$("<tr>"); table.append(tr);
    td=$("<td>").text("Prénom"); tr.append(td);
    td=$("<td>").append($("<input>",{type: "text", name: "prenom"})); tr.append(td);
    tr=$("<tr>"); table.append(tr);
    td=$("<td>").text("Classe"); tr.append(td);
    td=$("<td>").append($("<input>",{type: "text", name: "classe"})); tr.append(td);
    form.append(table);
    form.append($("<input>",{type: "hidden", name: "call", value: "newEleve"}));
    form.append($("<input>",{type: "Submit", value: "Valider"}))
    var dialog=$("<div>");
    dialog.append(form);
    $("body").append(dialog);
    dialog.dialog({title: "Création d'un nouvel élève", modal: true, width: 800});
}

/**
 * Crée un nouveau groupe : demande le titre et la salle
 **/
function creeGroupe(){
   var form=$("<form>",{method: "post", action: "index#tabs-special"});
    form.append($("<p>").text("Nouveau titre"));
    form.append($("<input>",{name: "titre"}));
    form.append($("<p>").text("Nouvelle salle"));
    form.append($("<input>",{name: "salle"}));
    form.append($("<input>",{type: "hidden", name: "call", value: "creeGroupe"}));
    form.append($("<input>",{type: "Submit", value: "Valider"}))
    var dialog=$("<div>");
    dialog.append(form);
    $("body").append(dialog);
    dialog.dialog({title: "Changement de titre", modal: true, width: 800});
}

/**
 * Change le titre du groupe numéro i
 * @param i numéro du groupe
 * @param ancien ancien titre
 **/
function changeTitre(i, ancien){
   var form=$("<form>",{method: "post", action: "index#tabs-"+i});
    form.append($("<input>",{type: "hidden", name: "i", value: i}));
    form.append($("<p>").text("Nouveau titre"));
    form.append($("<input>",{name: "titre", value: ancien}));
    form.append($("<input>",{type: "hidden", name: "call", value: "changeTitre"}));
    form.append($("<input>",{type: "Submit", value: "Valider"}))
    var dialog=$("<div>");
    dialog.append(form);
    $("body").append(dialog);
    dialog.dialog({title: "Changement de titre", modal: true, width: 800});
}

/**
 * Change la salle du groupe numéro i
 * @param i numéro du groupe
 * @param ancien ancienne salle
 **/
function changeSalle(i, ancien){
   var form=$("<form>",{method: "post", action: "index#tabs-"+i});
    form.append($("<input>",{type: "hidden", name: "i", value: i}));
    form.append($("<p>").text("Nouvelle salle"));
    form.append($("<input>",{name: "salle", value: ancien}));
    form.append($("<input>",{type: "hidden", name: "call", value: "changeSalle"}));
    form.append($("<input>",{type: "Submit", value: "Valider"}))
    var dialog=$("<div>");
    dialog.append(form);
    $("body").append(dialog);
    dialog.dialog({title: "Changement de salle", modal: true, width: 800});
}

/**
 * Suppression d'un groupe
 * @param titres liste des titres de groupe
 **/
function supprimeGroupe(titres){
    var form=$("<form>",{method: "post", action: "index#tabs-special"});
    var select=$("<select>",{name: "dest", size: 10});
    for (var j=0; j < titres.length; j++){
	var option=$("<option>");
	option.text(titres[j]);
	select.append(option);
    }
    form.append($("<p>").text("Choix du groupe :"));
    form.append(select);
    form.append($("<br>"));
    form.append($("<input>",{type: "hidden", name: "call", value: "supprimeGroupe"}));
    form.append($("<input>",{type: "submit", value: "OK"}));
    var dialog=$("<div>");
    dialog.append(form);
    $("body").append(dialog);
    dialog.dialog({title: "Supprimer un groupe", modal: true, width: 800});
}

/**
 * provoque la génération d'un fichier PDF
 **/
function makeODF(){
    var form=$("<form>",{method: "post", action: "index#tabs-1", style: "display: none;"});
    form.append($("<input>",{name: "call", value: "makeODF"}));
    $("body").append(form);
    form.submit();
}
