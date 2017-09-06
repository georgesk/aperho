// scripts spécifiques à addProfs.html

function addProf(csrf, barrette){
    $.post("addUnProf",
	   {
	       csrfmiddlewaretoken: csrf,
	       prof: $("#prof").val(),
	       salle: $("#salle").val(),
	       matiere: $("#matiere").val(),
	       barrette: barrette
	   },
	   function(data){
	       if (data.ok=="ok"){
		   location.assign("addProfs");
	       } else {
		   alert(data.message);
	       }
	   }
	  ).fail(
	      function(){
		  alert("Échec : problème de communication");
	      }
	  );
}


/**
 * Désinscrit un prof d'une barrette
 **/
function changeSalle(prof, barrette, salle, nouvelleSalle,
		     matiere, nouvelleMatiere, csrf){
    $.post(
	"changeSalle",
	{
	    csrfmiddlewaretoken: csrf,
	    prof: prof,
	    barrette: barrette,
	    salle: salle,
	    nouvelleSalle: nouvelleSalle,
	    matiere: matiere,
	    nouvelleMatiere: nouvelleMatiere,
	},
	function(data){
	    if (data.ok=="ok"){
		location.assign("addProfs");
	    }
	},
    ).fail(
	      function(){
		  alert("Échec : problème de communication");
	      }
    );
}

/**
 * édite les données d'un prof dans la barrette courante
 **/
function editProf(el){
    var ligne=$(el).parents("tr")[0];
    var prof=$(ligne).find("td:eq(1)").text().trim();
    var salle=$(ligne).find("td:eq(2)").text().trim();
    var matiere=$(ligne).find("td:eq(3)").text().trim();
    var barrette=$("#barretteCourante").text().trim();
    var csrf=$("#csrf").text().trim();
    /*************************************
     * Il faut récupérer la nouvelle salle
     *************************************/
    $("#dialog").empty()
    $("#dialog").html(
	"<table> \
           <tr> \
	     <td> \
	       Salle : \
	     </td> \
	     <td> \
	       <input type='text' placeholder='à renseigner' \
                id='newSalle' value='"+salle+"'/> \
	     </td> \
	   </tr> \
           <tr> \
	     <td> \
	       Matière : \
	     </td> \
	     <td> \
	       <input type='text' placeholder='à renseigner' \
                id='newMatiere' value='"+matiere+"'/> \
	     </td> \
	   </tr> \
         </table>"
    );
    $('#dialog').dialog({
        autoOpen: true,
        width: 550,
	modal:true,
        //height: 150,
        closeOnEscape: true,
        draggable: true,
        title: 'Choix de la salle pour '+prof,
        buttons: {
            'OK': function () {
		var nouvelleSalle = $("#newSalle").val();
		var nouvelleMatiere =$("#newMatiere").val();
		changeSalle(prof, barrette, salle, nouvelleSalle,
			    matiere, nouvelleMatiere, csrf);
                $('#dialog').dialog('close');
            },
            'Échap': function () {
                $('#dialog').dialog('close');
            }

        }
    });
}

/**
 * Suppression d'un prof d'une barrette
 **/
function delProf(el){
    var ligne=$(el).parents("tr")[0];
    var prof=$(ligne).find("td:eq(1)").text().trim();
    var barrette=$("#barretteCourante").text().trim();
    var csrf=$("#csrf").text().trim();

    var ajaxQuery=$.post(
	"delProfBarrette", {
	    prof: prof,
	    barrette: barrette,
	    csrfmiddlewaretoken: csrf,
	},
	function(data){
	    alert(data.message);
	    if (data.ok=="ok"){
		location.assign("addProfs");
	    }
	}
    ).fail(
	function(){alert("Échec de la suppression de "+prof);}
    );
}

/**
 * quand on quitte le champ de saisie de nom de prof, on regarde
 * si le prof est déjà dans la base et si c'est le cas, on met à jour
 * les autres champs
 **/
function chargeProf(el){
    var nomPrenom=$(el).val();
    var csrf=$("#csrf").text();
    $.post(
	"chargeProf",
	{ nomPrenom: nomPrenom, csrfmiddlewaretoken: csrf},
	function(data){
	    if (data.ok=="ok"){
		$("#matiere").val(data.matiere);
		$("#salle").val(data.salle);
	    }
	}
    ).fail(
	function(){alert("Problème de communication");}
    );

}

