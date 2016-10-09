/**
 * fonctions pour la page "enroler"
 **/

function enroler(){
    var eleve=$("#eleve").val();
    var cours=$("#cours").val();
    var cours2=$("#cours2").val();
    var re = /.*\((\S*)\)/;
    var uid=eleve.match(re)[1];
    console.log("inscrire dans le cours :", cours, uid);
    var url="/votes/enroleEleveCours"
    $.get(url,
	  { cours: cours, cours2: cours2, uid: uid, }
	 ).done(function(data){
	     console.log(data, data.msg);
	      $("#dialog").dialog({
		  title: "Résultat",
		  width: 400,
		  buttons: [
		      {
			  text: "OK",
			  click: function() {
			      $( this ).dialog( "close" );
			  }
		      }
		  ],
		  beforeClose: function(event, ui){
		      $("#eleve").val("");
		      location.reload();
		  },
	      }).html(data.msg);
	  }).fail(function(data){
	      alert("Erreur : "+data.status+" "+data.statusText+" "+url);
	  });
}
