// scripts nécessaires à la page addEleves
// jQuery est défini dans ce contexte, ansi que jQuery-UI

function voirClasse(c){
    $.get("listClasse", {classe: c}, function(data){
	$("#dialog").html(data.eleves);
	$( "#dialog" ).dialog({
	    autoOpen: true,
	    modal: true,
	    buttons: [
		{
		    text: "OK",
		    icons: {
			primary: "ui-icon-heart"
		    },
		    click: function() {
			$( this ).dialog( "close" );
		    }
		}
	    ]
	});
    });
}

function effacerClasse(c){
    $.get("delClasse", {classe: c}, function(data){
	$("#dialog").html("Effacement de "+c);
	$( "#dialog" ).dialog({
	    autoOpen: true,
	    modal: true,
	    buttons: [
		{
		    text: "OK",
		    icons: {
			primary: "ui-icon-heart"
		    },
		    click: function() {
			$( this ).dialog( "close" );
			location.assign("addEleves"); // on recharge la page
		    }
		}
	    ]
	});
    });
}

/**
 * met à jour les élèves de la base de données, d'après les classes
 * exisitant dans la barrette b
 * @param b le nom d'une barrette
 **/
function majKwartz(b){
    $.get("majElevesKwartz", {barrette: b,}, function(data){
	$("#dialog").html("Les classes ont été mises à jour");
	$( "#dialog" ).dialog({
	    autoOpen: true,
	    modal: true,
	    buttons: [
		{
		    text: "OK",
		    icons: {
			primary: "ui-icon-heart"
		    },
		    click: function() {
			$( this ).dialog( "close" );
			location.assign("addEleves"); // on recharge la page
		    }
		}
	    ]
	});
    }).fail(
	function(){
	    alert('something went wrong');
	}
    );
}

