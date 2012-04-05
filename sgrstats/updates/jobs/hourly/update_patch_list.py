"""
5 minutes latest patch release notes update job.

Fetches the list of new SGR updates and patches and
saves it into the database.
"""

import re

from lxml import html, etree
from updates.models import Update
from django_extensions.management.jobs import HourlyJob

class Job(HourlyJob):
    help = "Fetch and update update latest patch list"

    def execute(self):
        new_threads = fetch_thread_urls()
        fetch_and_save_new_threads_content(new_threads)
        
def fetch_thread_urls():
    """ Fetches and returns URLs for new threads (the ones which are not already in the database)
    in reverse order (older first). """

    FORUM_URL = 'http://forums.stargateworlds.com'
    FORUM_ID = '494'
    
    try:
        url = '%s/forumdisplay.php?f=%s' % (FORUM_URL, FORUM_ID)
        content = html.parse(url).getroot()
    except IOError:
        return
    
    thread_urls = content.xpath('//tbody[@id="threadbits_forum_494"]/tr/td/div/a[starts-with(@id, "thread_title_")]/@href')
    threads = [(int(url.split('&t=')[1]), '%s/%s' % (FORUM_URL, url)) for url in thread_urls]
    
    old_thread_ids = Update.objects.all().values_list('thread_id', flat = True)
    new_thread_urls = [thread[1] for thread in threads if thread[0] not in old_thread_ids]
    
    return list(reversed(new_thread_urls))
    
def fetch_and_save_new_threads_content(thread_urls = None):
    """ Saves new thread updates into the database. """
    
    if not thread_urls:
        return
    
    for url in thread_urls:
        try:
            content = html.parse(url).getroot()
        except IOError:
            return
        
        id = url.split('&t=')[1]
        title = content.xpath('//div[@class="smallfont"]/strong')[0].text
        
        if title.lower().find('patch notes') == -1:
            continue
        
        body = etree.tostring(content.xpath('//div[starts-with(@id, "post_message_")]')[0], with_tail = False)
        source = re.sub(r's=.*?&', '', url)
        
        update = Update(title = title, body = body, thread_id = id, source = source)
        update.save()
