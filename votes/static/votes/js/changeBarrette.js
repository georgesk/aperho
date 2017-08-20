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
    console.log(active)
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
        //height: 150,
        closeOnEscape: true,
        draggable: true,
        title: 'Choix de la barrette',
        buttons: {
            'OK': function () {
                //Handle flagdata JSON and send ot serverside

            },
            'Échap': function () {
                $('#dialog').dialog('close');
            }

        }
    });

}
