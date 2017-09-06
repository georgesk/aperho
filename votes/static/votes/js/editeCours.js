$(document).ready(function() {
    var pdi=$("#id_public_designe_initial");
    var pdn=$("#id_public_designe");
    // force la boîte à cocher visible à la valeur du champ invisible
    pdn.prop("checked", pdi.val()=="True");

    // diminue la largeur des champs numériques
    $("#id_duree").css({width: "50px"});
    $("#id_capacite").css({width: "50px"});
});

/**
 * écrase les données de formation à l'aide de celles qui sont cachées dans des
 * DIVs voisines de l'élément el
 **/
function editFormation(el){
    var tr=$(el).parents("tr").first();
    var titre=tr.find(".titre").first().text();
    var contenu=tr.find(".contenu").first().text();
    $("#id_titre").val(titre);
    $("#id_contenu").val(contenu);
}

/**
 * Supprime une ancienne Formation de la base de données et l'efface de la
 * fenêtre
 **/
function delFormation(el){
    var td=$(el).parents("td").first();
    var formation_id=td.find(".formation_id").first().text();
    var csrf=$("input[name=csrfmiddlewaretoken]").first().val();
    var ajaxReq=$.post(
	"delFormation",
	{
	    csrfmiddlewaretoken: csrf,
	    formation_id: formation_id,
	},
	function(data){
	    if (data.ok!="ok"){
		avertissement(data.message);
	    } else {
		var tr=td.parents("tr").first();
		tr.remove();
	    }
	},
    ).fail(
	function(data){
	    avertissement("erreur de communication")
	}
    );
}


function avertissement(msg){
    $( "#message" ).empty();
    $( "#message" ).attr({title: "Avertissement",});
    $( "#message" ).html(msg);
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
