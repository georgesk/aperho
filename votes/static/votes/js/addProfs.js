// scripts spécifiques à addProfs.html

function addProf(csrf, barrette){
    $.post("addUnProf",
	   {
	       csrfmiddlewaretoken: csrf,
	       prof: $("#prof").val(),
	       salle: $("#salle").val(),
	       barrette: barrette
	   },
	   function(data){
	       alert(data.message);
	       if (data.ok=="ok"){
		   location.assign("addProfs");
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
function changeSalle(prof, barrette, salle, nouvelleSalle, csrf){
    $.post(
	"changeSalle",
	{
	    csrfmiddlewaretoken: csrf,
	    prof: prof,
	    barrette: barrette,
	    salle: salle,
	    nouvelleSalle: nouvelleSalle,
	},
	function(data){
	    alert(data.message);
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
 * en fait le seul degré de liberté, c'est sa salle !
 **/
function editProf(el){
    var ligne=$(el).parents("tr")[0];
    var prof=$(ligne).find("td:eq(1)").text().trim();
    var salle=$(ligne).find("td:eq(2)").text().trim();
    var barrette=$("#barretteCourante").text().trim();
    var csrf=$("#csrf").text().trim();
    /*************************************
     * Il faut récupérer la nouvelle salle
     *************************************/
    $("#dialog").empty()
    $("#dialog").append(
	$("<span>").css({"margin-right": "1ex"}).text("Nouvelle salle :")
    ).append(
	$("<input>",{
	    type: "text",
	    placeholder: "à renseigner",
	    id:"newSalle"
	})
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
		changeSalle(prof, barrette, salle, nouvelleSalle, csrf);
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
