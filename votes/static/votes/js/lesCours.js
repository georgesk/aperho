// scripts spécifiques à lesCours.html


/**
 * édite les données d'un cours
 * @param csrf le token pour pouvoir POSTer
 * @param cours_id l'identifiant d'un cours
 * @param backLocation la page à réafficher après l'édition
 **/
function editCours(csrf, cours_id, backLocation){
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
		name: "dCourte",
		value: dCourte,
	    }).css({margin: "1em", width: "38em",})
	));
    t.append(tr);
    var ta="";
    try {
	ta=decodeURI(dLongue);
    }
    catch(err) {ta=dLongue;}
    tr=$("<tr>")
	.append($("<td>").text("Description longue :")
	       )
	.append($("<td>").append(
	    $("<textarea>",{
		id: "dLongue",
		name: "dLongue",
		rows: "4",
		cols: "60",
	    }).css({margin: "1em",}).text(ta)
	));
    t.append(tr);
    tr =$("<tr>")
	.append($("<td>").text("Durée (1 ou 2 heures) :")
	       )
	.append($("<td>").append(
	    $("<input>",{
		type: "text",
		id: "duree",
		name: "duree",
		value: duree,
	    }).css({margin: "1em",})
	));
    t.append(tr);
    tr =$("<tr>")
	.append($("<td>").text("capacité (±18 élèves) :")
	       )
	.append($("<td>").append(
	    $("<input>",{
		type: "text",
		id: "capacite",
		name:  "capacite",
		value: capacite,
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
		var capacite = $("#capacite").val();
		majCours(csrf, cours_id, backLocation, dCourte, dLongue, duree, capacite);
                $('#dialog').dialog('close');
            },
            'Échap': function () {
                $('#dialog').dialog('close');
            }

        }
    });
}

/**
 * édite les données d'un cours
 * @param csrf le token pour pouvoir POSTer
 * @param cours_id l'identifiant d'un cours
 * @param backLocation la page à réafficher après l'édition
 * @param dCourte description courte
 * @param dLongue description longue
 * @param duree la durée
 * @param capacite la capacité en élèves
 **/
function editCours0(csrf, cours_id, backLocation, dCourte, dLongue, duree, capacite){
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
		name: "dCourte",
		value: dCourte,
	    }).css({margin: "1em", width: "38em",})
	));
    t.append(tr);
    var ta="";
    try {
	ta=decodeURI(dLongue);
    }
    catch(err) {ta=dLongue;}
    tr=$("<tr>")
	.append($("<td>").text("Description longue :")
	       )
	.append($("<td>").append(
	    $("<textarea>",{
		id: "dLongue",
		name: "dLongue",
		rows: "4",
		cols: "60",
	    }).css({margin: "1em",}).text(ta)
	));
    t.append(tr);
    tr =$("<tr>")
	.append($("<td>").text("Durée (1 ou 2 heures) :")
	       )
	.append($("<td>").append(
	    $("<input>",{
		type: "text",
		id: "duree",
		name: "duree",
		value: duree,
	    }).css({margin: "1em",})
	));
    t.append(tr);
    tr =$("<tr>")
	.append($("<td>").text("capacité (±18 élèves) :")
	       )
	.append($("<td>").append(
	    $("<input>",{
		type: "text",
		id: "capacite",
		name:  "capacite",
		value: capacite,
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
		var capacite = $("#capacite").val();
		majCours(csrf, cours_id, backLocation, dCourte, dLongue, duree, capacite);
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
 * @param capacite la capacité en élèves
 **/
function majCours(csrf, cours_id, backLocation, dCourte, dLongue, duree, capacite){
    $.post("majCours",
	   {
	       csrfmiddlewaretoken: csrf,
	       cours_id: cours_id,
	       backLocation: backLocation,
	       dCourte: dCourte,
	       dLongue: encodeURI(dLongue),
	       duree: duree,
	       capacite: capacite,
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

/**
 * modifie un attribut dans un élément, selon la valeur du booléen trigger
 * @param el l'élément à toucher
 * @param trigger un booléen
 * @param attrib nom de l'attribut à mettre
 * @param valFalse valeur à attribuer si trigger est faux
 * @param valTrue valeur à attribuer si trigger est vrai
 **/
function changeattribut(el,trigger, attrib, valFalse, valTrue){
    var element=$(el);
    if(trigger){
	element.attr(attrib, valTrue);
    } else {
	element.attr(attrib, valFalse);
    }
}

/**
 * signale qu'on ne peut pas éditer un cours pendant la période
 * d'ouverture des inscriptions et empêche le submit d'aller au bout
 * @param tabou vaut 'True' quand on ne peut pas.
 **/
function interditCoursOuvert(tabou){
    if(tabou=="True"){
	$("#dialog").empty();
	$("#dialog").text("On ne peut pas modifier le contenu d'un cours d'AP pendant la période des inscriptions")
	$('#dialog').dialog({
            autoOpen: true,
            width: 750,
	    modal:true,
            closeOnEscape: true,
            draggable: true,
            title: 'Interdiction',
            buttons: {
		'OK': function () {
                    $('#dialog').dialog('close');
		},
            }
	});
	return false;
    } else {
	return true;
    }
}

/**
 * désinscrit un élève et appelle la page d'enrolement
 * en pré-positionnant l'élève et deux cours
 * @param eleveUid l'uid (prenom.nom) d'un élève
 * @param barrette une barrette par sa clé primaire
 * @param ouverture une ouverture par sa clé primaire
 * @param csrf un csrf middleware token
 **/
function editeInscriptions(eleveUid, barrette, ouverture, csrf){
    var f = $("<form>",{method: 'post', action: '/votes/enroler'});
    f.append($("<input>",{type:'hidden', name: 'uid', value: eleveUid,}));
    f.append($("<input>",{type:'hidden', name: 'barrette', value: barrette,}));
    f.append($("<input>",{type:'hidden', name: 'ouverture', value: ouverture,}));
    f.append($("<input>",{type:'hidden', name: 'csrfmiddlewaretoken', value: csrf,}));
    $("body").append(f);
    f.submit();
		      
}

/**
 * réinscrit un groupe d'élèves comme dans la période précédente
 * ce qui est utile pour les formations à public désigné
 * @param coursId identifiant d'un cours
 * @param ouvertureId identifiant d'une ouverture des votes pour l'AP
 **/
function reinscription(coursId, ouvertureId, csrf){
    $.post("/votes/reinscription",
	   {
	       csrfmiddlewaretoken: csrf,
	       cours_id: coursId,
	       ouverture_id: ouvertureId,
	   },
	   function(data){
	       if (data.ok=="ok"){
		   alert(data.message);
		   location.assign("/votes/lesCours");
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
