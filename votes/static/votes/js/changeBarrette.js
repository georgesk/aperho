/**
 * bibliothèque permettant de changer de barrette à l'aide d'un dialogue
 * jquery
 **/

/**
 * changement de barrettes
 * @param possibilites une liste de barrettes possibles
 * @param active le rang de la possibilité active
 **/
function changebarrette(possibilites, active){
    // vide le dialogue et y place des boutons radio
    $("#dialog").empty();
    for(var i=0; i < possibilites.length; i++){
	var input=$("<input>",{type: "radio", name: "barrette"});
	$("#dialog").append(input);
	// active le bon bouton
	if(i==active) {
	    input.prop("checked", true);
	}
	$("#dialog").append(
	    $(document.createTextNode(possibilites[i]))
	).append(
	    $("<br>")
	);
    }
    // crée le dialogue jquery et le rend modal
    $('#dialog').dialog({
        autoOpen: true,
        width: 550,
	modal:true,
        //height: 150,
        closeOnEscape: true,
        draggable: true,
        title: 'Choix de la barrette',
        buttons: {
            'OK': function () {
		var nouvelleBarrette = $("#dialog input:checked")[0].nextSibling.nodeValue;
		window.location.assign("/?nouvelleBarrette="+nouvelleBarrette);
            },
            'Échap': function () {
                $('#dialog').dialog('close');
            }

        }
    });

}

/**
 * met à jour l'annuaire au complet
 **/
function majAllAnnuaire(){
    // vide le dialogue
    $("#dialog").empty();
    var p=$("<p>");
    $("#dialog").append(p);
    var wait=$("<div class='wait'><center><img alt='wait' src='/static/votes/img/Songbird_Icon_Spinner1.gif'style='position: fixed; top:40%;'/></center></div>")
    $("body").append(wait);
    $.get(
	"/votes/majElevesKwartz?barrette=all",
	function(data){
	    $('#dialog').dialog({
		"create": function( event, ui ) {p.text(data.message)},
		autoOpen: true,
		width: 550,
		modal:true,
		//height: 150,
		closeOnEscape: true,
		draggable: true,
		title: "Mise à jour de l'annuaire",
		buttons: {
		    'OK': function () {
			$('#dialog').dialog('close');
		    }

		}
	    });
	}
    ).always(
	function(){$(".wait").remove();}
    );
}
