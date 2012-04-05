$().ready(function()
{
	$('a.tip, span.tip, th.tip, td a[href][title],div a[href][title]').live('mouseover', function()
	{
		// Live bindings
		if (!$(this).data('qtip'))
		{
		  	$(this).qtip(
		     {
		         content: $(this).attr('tip'), 
		         position: { target: 'mouse' },
		         overwrite: false,
		         show:
		         {
		        	 solo: true,
		        	 ready: true
		         },
		         style:
		         {
		         	name: 'dark',
		     		textAlign: 'center',
		     		style: { width: { min: 105 } },
		         	classes:
		            {
		         		content: 'tooltip_content'
		            }            
		         } 
		     });
		}
	});
});