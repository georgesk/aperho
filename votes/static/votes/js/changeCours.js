/**
 * Fonctions à appeler pour vérifier que les cours demandés
 * par un étudiant sont compatibles avec les règles
 * @param n un numéro de cours de la base de données
 * @param dialog (vrai par défault) : affichage d'un dialogue de feedback
 * @return la durée des cours cochés (il faut deux heures)
 **/

function check(n, dialog){
    if (dialog===undefined){
	dialog=true;
    }
    var ok=true; // approuve/désapprouve le changement
    var msg="";
    var c_0_1=$("[data-class=cours_0_1]:checked");
    var c_1_1=$("[data-class=cours_1_1]:checked");
    var c_0_2=$("[data-class=cours_0_2]:checked");
    var c_checked=$("table input:checkbox:checked");
    if (c_0_1.length+c_0_2.length > 1){
	ok=false;
	msg="ERREUR  : deux cours demandés commencent à la première heure";
    }
    if (c_1_1.length+c_0_2.length > 1){
	ok=false;
	msg="ERREUR  : deux cours demandés commencent à la deuxième heure";
    }
    var duree=2*c_0_2.length+c_0_1.length+c_1_1.length;
    if (duree < 2){
	// msg="Une heure a été choisie. Il faut en choisir une deuxième.";
	msg="";
    }
    if (duree > 2){
	ok=false;
	msg="ERREUR : on ne peut pas choisir plus de deux heures de cours"
    }
    var formations=[];
    for (var i=0; i< c_checked.length; i++){
	var f=$(c_checked[i]).attr("data-formation");
	if (formations.indexOf(f)>=0){
	    ok=false;
	    msg="ERREUR  : deux cours choisis ne peuvent pas être identiques";
	} else {
	    formations.push(f);
	}
    }
    if (dialog && msg.length > 0) message(msg);
    if (!ok){ // on désapprouve.
	var cb=$("#cours_"+n)[0];
	cb.checked=!cb.checked; // retour en arrière
    }
    return duree;
}

/**
 * présente un message dans un dialogue modal à l'aide de jQuery
 * @param msg le message à montrer
 * @param reload faux par défaut, oblige à recharger la page à la fermeture
 **/
function message(msg, reload){
    if (reload===undefined) reload=false;
    var closeFunction=function(){};
    if (reload){
	closeFunction=function(){
	    window.location.reload();
	}
    }
    var d = $("#dialog");
    d.html("<p>"+msg+"</p>");
    d.dialog({
	title: "Information",
	resizable: false,
	height: "auto",
	width: 400,
	modal: true,
	buttons: {
	    OK: function() {
		$( this ).dialog( "close" );
	    }
	}
    }).bind('dialogclose', function(event, ui) { closeFunction(); });;
}

/**
 * validation des cours qui sont cochés
 **/
function valideCours(){
    var inscriptions=$("fieldset.orientation input:checked");
    if (inscriptions.length < 1){
	message("Aucune séance d'information sur l'orientation en première n'a été choisie. Cochez au moins une des cases en haut de cette page.");
    } else {
	var duree=check(0,false);
	if (duree != 2){
	    message("La durée des cours sélectionnés n'est pas de deux heures. Modifiez la sélection.");
	} else {
	    var url="/votes/addInscription";
	    var classesChoisies=[];
	    var checked=$("table input:checked");
	    for(var i=0; i < checked.length; i++){
		classesChoisies.push(parseInt($(checked[i]).attr("name").replace("cours_","")));
	    }
	    var inData={
		uid: $("#etudiantUid").val(),
		classes: classesChoisies.join(":"),
		orientations: $('fieldset.orientation input:checkbox:checked').
		    map(function() {
			return this.value;
		    }).get().join(":"),
	    };
	    var successFunction=function(data){
		if (data.ok){
		    message("OK ; "+data.message, /*reload*/ true);
		} else {
		    message("Échec ; "+data.message);
		}
	    };
	    var failFunction=function(data){
		message("Erreur de traitement (/vote/addInscription). " + JSON.stringify(data));
	    };
	    $.get(url, inData)
		.done(successFunction)
		.fail(failFunction);
	}
    }
}

/**
 * annulation de tous les cours d'un utilisateur
 * sauf les cours à public désigné
 **/
function annuleCours(){
    // décoche toutes les cases qu'on a le droit de décocher
    var cases=$("table input:checked:enabled").prop( "checked", false );;
    var url="/votes/addInscription";
    var inData={
	uid: $("#etudiantUid").val(),
	classes: "",
	orientations: "",
    };
    var successFunction=function(data){
	if (data.ok){
	    message("OK ; "+data.message, /*reload*/ true);
	} else {
	    message("Échec ; "+data.message);
	}
    };
    var failFunction=function(data){
	message("Erreur de traitement (/vote/addInscription). " + JSON.stringify(data));
    };
    $.get(url, inData)
	.done(successFunction)
	.fail(failFunction);
}

