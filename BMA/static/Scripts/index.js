function loadHomePages(name, divName, loaderName){
    $(divName).hide();
    $(loaderName).show();
    $.ajax({
        url: name,
        success: function(result){
            $(divName).html(result);
            $(loaderName).fadeOut();
            $(divName).fadeIn(1000);
        }
    })
}

$(document).ready(function(){
    loadHomePages("pages/home", "#main", "#main-loader");
})