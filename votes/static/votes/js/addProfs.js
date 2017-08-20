// scripts spécifiques à addProfs.html

function addProf(csrf){
    console.log($("#prof").val()+" "+$("#salle").val()+" "+ csrf);
    $.post("addUnProf",
	   {
	       csrfmiddlewaretoken: csrf,
	       prof: $("#prof").val(),
	       salle: $("#salle").val(),
	   },
	   function(){
	       alert($("#prof").val()+" est inscrit(e)")
	       location.assign("addProfs");
	   }
	  ).fail(
	      function(){
		  alert("l'inscription a échoué");
	      }
	  );
}
