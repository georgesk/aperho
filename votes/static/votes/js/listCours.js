function effacerCours(c){
    $.get("delCours", {cours: c}, function(data){
	$("#dialog").html("Effacement du cours n° "+c);
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
			location.reload(); // on rafraîchit la page
		    }
		}
	    ]
	});
    });
}

