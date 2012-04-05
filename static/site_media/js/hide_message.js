$().ready(function()
{
	$('div#success,#error').click(function()
	{
		$(this).slideUp('fast');
	})
});