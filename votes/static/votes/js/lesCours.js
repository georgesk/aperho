// scripts spécifiques à lesCours.html


/**
 * édite les données d'un cours
 * @param csrf le token pour pouvoir POSTer
 * @param cours_id l'identifiant d'un cours
 * @param backLocation la page à réafficher après l'édition
 * @param dCourte description courte
 * @param dLongue description longue
 * @param duree la durée
 **/
function editCours(csrf, cours_id, backLocation, dCourte, dLongue, duree){
    console.log("GRRRR", csrf, cours_id, backLocation)
    /*********************************************************************
     * Il faut récupérer les nouvelles descriptions et la nouvelle durée *
     *********************************************************************/
    $("#dialog").empty()
    var t  =$("<table>",{border:"1", "class": "joli"});
    var tr =$("<tr>")
	.append($("<td>").text("Description courte :")
	       )
	.append(
	    $("<input>",{
		type: "text",
		name: "dCourte",
		value: dCourte,
	    })
	);
    t.append(tr);
    
    $("#dialog").append(t);
    $('#dialog').dialog({
        autoOpen: true,
        width: 550,
	modal:true,
        closeOnEscape: true,
        draggable: true,
        title: 'Édition de cours',
        buttons: {
            'OK': function () {
		var nouvelleSalle = $("#newSalle").val();
		changeSalle(prof, barrette, salle, nouvelleSalle, csrf);
                $('#dialog').dialog('close');
            },
            'Échap': function () {
                $('#dialog').dialog('close');
            }

        }
    });
}

