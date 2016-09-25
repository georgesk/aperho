/**
 * Fonctions à appeler pour vérifier que les cours demandés
 * par un étudiant sont compatibles avec les règles
 **/

function check(n){
    alert("changement d'état d'une case à cocher (cours n° "+n+")");
    var ok=false; // approuve/n'approuve pas le changement
    if (!ok){ // on désapprouve.
	var cb=$("#cours_"+n)[0];
	cb.checked=!cb.checked; // retour en arrière
    }
}
