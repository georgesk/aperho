$(document).ready(function() {
    var pdi=$("#id_public_designe_initial");
    var pdn=$("#id_public_designe");
    // force la boîte à cocher visible à la valeur du champ invisible
    pdn.prop("checked", pdi.val()=="True");

    // ajuste la case "mixte" et la visibilité des saveurs
    if ($("#mixte").val()=="True"){
	$("#id_mix").prop("checked", true);
	$("#saveurs").hide();
    } else {
	$("#id_mix").prop("checked", false);
	$("#saveurs").show();
	verifieSaveurs();
    }
    $("#id_mix").click(function(){$('#saveurs').toggle(1000); verifieSaveurs();});
    // accroche une vérification aux cases à cocher des saveurs
    // si on décoche la saveur, la ventilation est mise à jour.
    for(var i=1; i<6; i++){
	$("#id_actif_"+i).click(function(j){
	    return function(){
		$("#id_ventilation_"+j).val(0);
		verifieSaveurs();
	    }
	}(i));
    }

    // diminue la largeur des champs numériques
    $("#id_duree").css({width: "50px"});
    $("[name^=ventilation_]").css({width: "50px"});
    $("#id_capacite").css({width: "50px"});
});

/**
 * S'assure que le total des saveurs cochées donne bien l'effectif total
 **/
function verifieSaveurs(){
    if ($("#mix").prop("checked")) return; // pas de vérification si c'est mixte
    var effectif = parseInt($("#id_effectif_total").val())
    var oneChecked=false; // est-ce qu'une saveur au moins est cochée ?
    for (var i=1; i < 6; i++){
	if ($("#id_actif_"+i).prop("checked")){
	    oneChecked=true;
	    break;
	}
    }
    // si aucune case n'est cochée, toutes doivent l'être
    if (! oneChecked){
	for (var i=1; i < 6; i++){
	    $("#id_actif_"+i).prop("checked", true);
	}
    }
    var t=0;
    for (var i=1; i < 6; i++){
	var vent=$("#id_ventilation_"+i);
	var v = parseInt(vent.val());
	if(isNaN(v)) vent.val(0); else t+=v;
    }
    while (t < effectif){
	for (var i=1; i < 6; i++){
	    var vent=$("#id_ventilation_"+i);
	    var v = parseInt(vent.val());
	    if (t < effectif && $("#id_actif_"+i).prop("checked")){
		vent.val(v+1);
		t+=1;
	    }
	}
    }
    while (t > effectif){
	for (var i=1; i < 6; i++){
	    var vent=$("#id_ventilation_"+i);
	    var v = parseInt(vent.val());
	    if (v > 0 && t > effectif && $("#id_actif_"+i).prop("checked")){
		vent.val(v-1);
		t-=1;
	    }
	}
    }
}

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
