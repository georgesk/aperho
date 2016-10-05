// scripts nécessaires à la page addEleves
// jQuery est défini dans ce contexte, ansi que jQuery-UI

function voirClasse(c){
    $("#dialog").html("on veut voir "+c);
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
}

function effacerClasse(c){
    alert("on veut effacer "+c);
}

