$().ready(function()
{
	$('a.deal').each(function()
	{
	  	$(this).qtip(
	     {
	         content: $(this).attr('tip'), 
	         position:
	     	{
	     		corner:
	     		{
	                 tooltip: 'bottomRight',
	                 target: 'topLeft'
	              }
	     	},
	         style:
	         {
	         	name: 'dark',
	     		textAlign: 'center',
	     		padding: 5,
	     		width: 320,
	         	classes:
	            {
	     			content: 'tooltip_content_deal'
	            }            
	         } 
	     });
	});
});