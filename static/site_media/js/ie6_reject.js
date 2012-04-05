$().ready(function()
{
	$.reject(
	{
		reject:
		{
			all: false,
			msie5: true,
			msie6: true
		},
		display: ['firefox', 'chrome', 'opera', 'safari'],
		imagePath: '/site_media/images/browsers/'
	});  
});