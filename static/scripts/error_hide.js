setTimeout(
    function(){
    elements = document.getElementsByClassName('error_alert');
    for(let el = 0; el < elements.length;el+=1) {
        elements[el].hidden = true;
}}, 3000);