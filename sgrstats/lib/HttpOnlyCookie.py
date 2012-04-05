"""
HTTPONLY cookie middleware
http://www.loggly.com/2010/04/securing-your-web-application-with-httponly-cookies-or-how-apache-org-and-atlassian-could-have-been-secured/
"""
import sgrstats.settings as settings

class HttpOnlyCookieMiddleware:
	
	def process_response(self, request, response):
		scn = 'sessionid'
		
		if response.cookies.has_key(scn):
			response.cookies[scn]['httponly'] = True
		return response