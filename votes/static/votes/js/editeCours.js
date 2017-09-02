$(document).ready(function() {
    if("{{avertissement}}".length > 0){
	$( "#message" ).empty();
	$( "#message" ).attr({title: "Avertissement",});
	$( "#message" ).html("{{avertissement|safe}}");
	$( "#message" ).dialog({
	    modal: true,
	    buttons: [
		{
		    text: "OK",
		    click: function() {
			$( this ).dialog( "close" );
		    }
		}
	    ]
	});
    }

    var pdi=$("#id_public_designe_initial");
    var pdn=$("#id_public_designe");
    // force la boîte à cocher visible à la valeur du champ invisible
    pdn.prop("checked", pdi.val()=="True");

    // diminue la largeur des champs numériques
    $("#id_duree").css({width: "50px"});
    $("#id_capacite").css({width: "50px"});
});

