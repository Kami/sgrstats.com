function highlight(elemId)
{
    var elem = $(elemId);
    
    elem.css("backgroundColor", "#1A1A1A"); // hack for Safari
    elem.animate({ backgroundColor: '#ffffaa' }, 1500);
    setTimeout(function(){$(elemId).animate({ backgroundColor: "#1A1A1A" }, 3000)},1000);
}