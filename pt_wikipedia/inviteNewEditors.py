#! /home/jtmorgan/.local/bin/python
# I'm using a local copy of python because I was getting funny cron output on toolserver. You should probably use the default one.

# Copyright 2013 Jtmorgan

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import MySQLdb
import wikitools
import settings
from datetime import datetime
import logging
from random import choice
import urllib2 as u2
import urllib
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8') #this may be necessary to avoid username charencoding errors

#initialize editing settings
wiki = wikitools.Wiki(settings.apiurl)
wiki.login(settings.username, settings.password)

#initialize logging
logging.basicConfig(filename='/home/jtmorgan/wikiprojects/pt_wikipedia/logs/invitations.log',level=logging.INFO) #no logs set up, yet

#log in to mysql
conn = MySQLdb.connect(host = 'sql-s2-user.toolserver.org', db = 'u_jtmorgan_wikiprojetos_p', read_default_file = '~/.my.cnf', use_unicode=1, charset="utf8" )


##GLOBAL VARIABLES##
cursor = conn.cursor()
curtime = str(datetime.utcnow())
page_namespace = 'User_talk:'
report_title = settings.rootpage + '/Reports#Daily_report' #localize to pt.wiki page
headers = { 'User-Agent' : 'YourBotName (http://yourRepository.com/path/to/codebase; yourname@email.com)' } #user agent header for API request
invite_list = [] #users who received an invitation
skip_list = [] #users who were skipped
curHosts = ['Rosiestep','Jtmorgan','SarahStierch','Ryan Vesey','Writ Keeper','Doctree','Osarius','Hajatvrc','Nathan2055','Benzband','Theopolisme','TheOriginalSoni'] #list of editors whose names will appear on the template. Localize.
skip_templates = ['uw-vandalism4', 'uw-socksuspect', 'Socksuspectnotice', 'Uw-socksuspect', 'sockpuppetry', 'Teahouse', 'uw-cluebotwarning4', 'uw-vblock', 'uw-speedy4'] # strings from templates on user talk pages that mean editor should not be invited. Localize.
invite_template = u'{{subst:Wikipedia:Teahouse/HostBot_Invitation|personal=I hope to see you there! [[User:%s|%s]] ([[w:en:WP:Teahouse/Hosts|I\'m a Teahouse host]])%s}}' #localize


##FUNCTIONS##
def getUsernames():
#gets a list of today's editors to invite
	cursor.execute('SELECT user_name, user_id FROM u_jtmorgan_wikiprojetos_p WHERE DATE(sample_date) = DATE(NOW()) AND invited = 0 AND ut_is_redirect != 1')
	rows = cursor.fetchall()
	return rows


def talkpageCheck(user, headers):
#checks to see if the user's talkpage has any templates that would necessitate skipping
	skip = False
	try:
		tp = wikitools.Page(wiki, 'page_namespace:' + user[0])
		pagetxt = unicode(tp.getWikiText(), 'utf8')
		for template in skip_templates:
			if template in pagetxt:
				skip = True
		allowed = allow_bots(pagetxt, settings.username)
		if not allowed:
			skip = True		
	except:
		logging.info('Invite to ' + user + ' failed on talkpageCheck ' + curtime)
	return skip


def allow_bots(text, user):
#checks for exclusion compliance, per http://en.wikipedia.org/wiki/Template:Bots
	return not re.search(r'\{\{(nobots|bots\|(allow=none|deny=.*?' + user + r'.*?|optout=all|deny=all))\}\}', text, flags=re.IGNORECASE)


def inviteUsers():
#invites guests		
	for user in invite_list:
		host = choice(curHosts) #selects a host to personalize the invite from curHosts[]
		invite_title = page_namespace + user[0]
		invite_page = wikitools.Page(wiki, invite_title)
		invite_text = invite_template % (host, host, '|signature=~~~~')
		invite_text = invite_text.encode('utf-8')
		print invite_text
		print invite_title
# 		try:
# 			invite_page.edit(invite_text, section="new", sectiontitle="== {{subst:PAGENAME}}, you are invited to the Teahouse ==", summary="Automatic invitation to visit [[WP:Teahouse]] sent by [[User:HostBot|HostBot]]", bot=1) #localize
# 		except:
# 			logging.info('Invite to ' + user[0] + ' failed on inviteUsers at ' + curtime)
# 			continue
# 		try:
# 			cursor.execute('''UPDATE u_jtmorgan_wikiprojetos_p SET invited = 1, bot_invited = 1, WHERE user_id = %d ''', (user[1],))
# 			conn.commit()	
# 		except UnicodeDecodeError:
# 			logging.info('Invite to ' + user[0] + ' failed on invite db update due to UnicodeDecodeError at ' + curtime)
# 			continue

			
def recordSkips():
#records the users who were skipped
	for skipped in skip_list:
		try:
# 			skipped = MySQLdb.escape_string(skipped)
			cursor.execute('''UPDATE u_jtmorgan_wikiprojetos_p SET bot_skipped = 1 WHERE user_id= %d ''', (skipped[1],))
			conn.commit()
		except:
			logging.info('Invite to ' + skipped[0] + ' failed on skip db update at ' + curtime)
			continue
	

##MAIN##
rows = getUsernames()
for row in rows:
	user = (row[0], row[1])
	if row[1] is not None: #what is this?
		skip = talkpageCheck(user, headers)
		if skip:
			skip_list.append(user)
	else:		
		invite_list.append(user)
inviteUsers()
recordSkips()	

# print ("invited: ", invite_list)
# print ("skipped: ", skip_list)	

cursor.close()
conn.close()
