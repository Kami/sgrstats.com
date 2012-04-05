$.tablesorter.addParser(
{ 
    id: 'time_played', 
    is: function(s)
    { 
        return false; 
    }, 
    format: function(s)
    {
	    hours = parseInt(s.substring(0, s.indexOf('h')));
	    minutes = parseInt(s.substring(s.indexOf('h') + 2, s.indexOf('min')));
	    minutes_total = parseInt((hours * 60) + minutes);
	    
        return minutes_total;
    }, 
    type: 'numeric' 
});