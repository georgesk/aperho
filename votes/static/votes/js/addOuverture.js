$(document).ready(function() {
    $( ".accordeon" ).accordion({
	collapsible: true,
	active: -1,
    });

    $.datepicker.regional['fr'] = {
	closeText: 'Fermer',
	prevText: '< préc',
	nextText: 'suiv >',
	currentText: 'Courant',
	monthNames: ['Janvier','Février','Mars','Avril','Mai','Juin',
		     'Juillet','Août','Septembre','Octobre','Novembre','Décembre'],
	monthNamesShort: ['Jan','Fév','Mar','Avr','Mai','Jun',
		     'Jul','Aoû','Sep','Oct','Nov','Déc'],
	dayNames: ['Dimanche','Lundi','Mardi','Mercredi','Jeudi',
		   'Vendredi','Samedi'],
	dayNamesShort: ['Dim','Lun','Mar','Mer','Jeu','Ven','Sam'],
	dayNamesMin: ['Di','Lu','Ma','Me','Je','Ve','Sa'],
	weekHeader: 'Sem',
	dateFormat: 'dd/mm/yy',
	firstDay: 1,
	isRTL: false,
	showMonthAfterYear: false,
	yearSuffix: ''
    };
    
    $.datepicker.setDefaults($.datepicker.regional.fr);
    $.timepicker.setDefaults($.timepicker.regional.fr);
    
    $( "#debut" ).datetimepicker({altField: "#debut_h"});
    $( "#fin" ).datetimepicker({altField: "#fin_h"});
});

/**
 * suppression d'une période d'AP
 * @param el un élément fils de la barrettela ligne du tableau
 **/
function delOuverture(el){
    var nom=$(el).parents('.uneouverture').first().find("th").first().text();
    var barrette=$("#barrette").val()
    var csrfmiddlewaretoken=$("form").first().find("input[name=csrfmiddlewaretoken]").first().val()
    var ajaxQuery=$.post(
	"delOuverture", {
	    nom: nom,
	    barrette: barrette,
	    csrfmiddlewaretoken: csrfmiddlewaretoken,
	},
	function(){
	    $("#message").html("Effacement de la période d'AP "+nom);
	    $( "#message" ).dialog(
		{
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
			},
		    ],
		}
	    )
	}
    ).fail(
	function(){alert("Échec de la suppression de "+nom);}
    );
}

/**
 * édition d'une période d'ouverture
 * @param el un élément fils de la barrette
 **/
function editOuverture(el){
    var ligne=$(el).parents('.uneouverture').first()
    var nom=ligne.find("th").first().text();
    var td=ligne.find("td");
    var debut=$(td[0]);
    var fin=$(td[1]);
    var debut_jour=debut.find(".jour").first().val();
    var debut_heure=debut.find(".heure").first().val();
    var fin_jour=fin.find(".jour").first().val();
    var fin_heure=fin.find(".heure").first().val();
    // on désactive la possibilité de créer une nouvelle ouverture
    $("#cno").css({display: "none"});
    // on rhabille le formulaire de création en formulaire d'édition
    $("#nb").text("Modification de la période "+nom);
    $("form").first().attr({action: "editOuverture"});
    $("#submit").val("Valider le changement");
    $("#nom").val(nom);
    $("#cacheNom").val(nom);
    $("#debut").val(debut_jour);
    $("#debut_h").val(debut_heure);
    $("#fin").val(fin_jour);
    $("#fin_h").val(fin_heure);
    // on scrolle
    var aTag = $(".uneouverture").last();
    $('html,body').animate({scrollTop: aTag.offset().top-60},'slow');
    return;
}
