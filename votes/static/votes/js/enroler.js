/**
 * fonctions pour la page "enroler"
 **/

function enroler(){
    var eleve=$("#eleve").val();
    var cours0val=$("#cours0").val();
    var cours1val=$("#cours1").val();
    var re=/.*(\d)h .*/;
    var duree=0;
    var match=re.exec(cours0val); if (match) duree+=parseInt(match[1]);
     match=re.exec(cours1val); if (match) duree+=parseInt(match[1]);
    if (eleve=="" || duree !=2) return;
    var wait=$("<div class='wait'><center><img alt='wait' src='/static/votes/img/Songbird_Icon_Spinner1.gif'style='position: fixed; top:40%;'/></center></div>")
    $("body").append(wait);
    var re = /^.*\((\S*)\)$/;
    var uid=eleve.match(re)[1];
    var id0=cours0val.match(re)[1];
    var m1=cours1val.match(re);
    if (m1) id1=m1[1]; else id1=-1;
    var csrf=$("#csrf").val();
    console.log("inscrire dans le cours :", id0, id1, uid);
    var url="/votes/enroleEleveCours"
    $.post(url,
	   { cours: id0, cours2: id1, uid: uid, csrfmiddlewaretoken: csrf}
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
		      var uri="/votes/enroler?"+encodeURI(
			  "c0="+id0+"&c1="+id1
		      );
		      document.location=uri;
		  },
	      }).html(data.msg);
	  }
		).fail(function(data){
		    alert("Erreur : "+data.status+" "+data.statusText+" "+url);
		}
		      ).always(
			  function(){$(".wait").remove();}
		      );
}
