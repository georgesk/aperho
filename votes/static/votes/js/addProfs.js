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
function delProf(el){
    var ligne=$(el).parents("tr")[0];
    var prof=$(ligne).find("td:eq(1)").text().trim();
    var barrette=$("#barretteCourante").text().trim();
    var csrf=$("#csrf").text().trim();
    $.post(
	"delProfBarrette",
	{
	       csrfmiddlewaretoken: csrf,
	       prof: prof,
	       barrette: barrette
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
    console.log("Édition de ", prof, salle, barrette, csrf);
}

