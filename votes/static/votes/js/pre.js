
/**
 * crée et soumet un formulaire pour supprimer une préinscription.
 */
function delPreInscription(pre_id){
    var form = document.createElement("form");
    form.setAttribute("method", "post");
    form.setAttribute("action", "");

    var csrf=$("input[name='csrfmiddlewaretoken']").first().clone();
    csrf.appendTo(form);
    var hiddenField = document.createElement("input");
    hiddenField.setAttribute("type", "hidden");
    hiddenField.setAttribute("name", "delPre");
    hiddenField.setAttribute("value", ""+pre_id);
    form.appendChild(hiddenField);
    document.body.appendChild(form);
    form.submit();
}
