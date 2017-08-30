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
    /*********************************************************************
     * Il faut récupérer les nouvelles descriptions et la nouvelle durée *
     *********************************************************************/
    $("#dialog").empty()
    var t  =$("<table>",{border:"1", "class": "joli"});
    var tr =$("<tr>")
	.append($("<td>").text("Description courte :")
	       )
	.append($("<td>").append(
	    $("<input>",{
		type: "text",
		id: "dCourte",
		value: dCourte,
	    }).css({margin: "1em", width: "38em",})
	));
    t.append(tr);
    var ta=
    tr=$("<tr>")
	.append($("<td>").text("Description longue :")
	       )
	.append($("<td>").append(
	    $("<textarea>",{
		id: "dLongue",
		rows: "4",
		cols: "60",
	    }).css({margin: "1em",}).text(dLongue)
	));
    t.append(tr);
    tr =$("<tr>")
	.append($("<td>").text("Durée (1 ou 2 heures) :")
	       )
	.append($("<td>").append(
	    $("<input>",{
		type: "text",
		id: "duree",
		value: duree,
	    }).css({margin: "1em",})
	));
    t.append(tr);
    
    $("#dialog").append(t);
    $('#dialog').dialog({
        autoOpen: true,
        width: 750,
	modal:true,
        closeOnEscape: true,
        draggable: true,
        title: 'Édition de cours',
        buttons: {
            'OK': function () {
		var dCourte = $("#dCourte").val();
		var dLongue = $("#dLongue").val();
		var duree = $("#duree").val();
		majCours(csrf, cours_id, backLocation, dCourte, dLongue, duree);
                $('#dialog').dialog('close');
            },
            'Échap': function () {
                $('#dialog').dialog('close');
            }

        }
    });
}

/**
 * met à jour les données d'un cours
 * @param csrf le token pour pouvoir POSTer
 * @param cours_id l'identifiant d'un cours
 * @param backLocation la page à réafficher après l'édition
 * @param dCourte description courte
 * @param dLongue description longue
 * @param duree la durée
 **/
function majCours(csrf, cours_id, backLocation, dCourte, dLongue, duree){
    $.post("majCours",
	   {
	       csrfmiddlewaretoken: csrf,
	       cours_id: cours_id,
	       backLocation: backLocation,
	       dCourte: dCourte,
	       dLongue: dLongue,
	       duree: duree,
	   },
	   function(data){
	       if (data.ok=="ok"){
		   location.assign(backLocation);
	       } else{
		   alert(data.message);
	       }
	   }
	  ).fail(
	      function(){
		  alert("Échec : problème de communication");
	      }
	  );
}
