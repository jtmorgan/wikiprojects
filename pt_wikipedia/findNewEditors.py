#! /home/jtmorgan/.local/bin/python
# I'm using a local copy of python because I was getting funny output from cron. You should probably use the default.
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

#initialize editing settings
# namespace not recognized: UnicodeEncodeError: 'ascii' codec can't encode character u'\xc3' in position 16: ordinal not in range(128)
wiki = wikitools.Wiki(settings.apiurl)
wiki.login(settings.username, settings.password)

#initialize logging
logging.basicConfig(filename='/home/jtmorgan/wikiprojects/pt_wikipedia/logs/invitations.log',level=logging.INFO) #no logs set up, yet

#initialize mysql
conn = MySQLdb.connect(host = 'sql-s2-user.toolserver.org', db = 'u_jtmorgan_wikiprojetos_p', read_default_file = '~/.my.cnf', use_unicode=1, charset="utf8" )

###GLOBAL VARIABLES AND TEMPLATES###
report_title = settings.rootpage + '/Reports#Daily_report' #localize to pt.wiki page
cursor = conn.cursor()
curtime = str(datetime.utcnow())
page_namespace = 'User_talk:' #localize
report_template = u'''==Daily Report==

===Active new editors===
Below is a list of editors who registered within the last 24 hours, have since made more than 2 edits, and were not blocked at the time the report was generated.
 
{| class="wikitable sortable plainlinks"
|-
! Editor #
! User name
! Edit count
! Contribs
! Already invited?
|-
%s
|}

'''

##FUNCTIONS##
def gatherSample():
#Grabs today's sample of new editors to invite. 
#You could easily run multiple queries to gather multiple different samples 
#Example: get BOTH brand new editors who have made at least 2 edits
#AND relatively new editors who have edited particular pages at least once.
	cursor.execute('''
	INSERT IGNORE INTO invited_medicina
		(user_id, user_name, user_registration, user_editcount, sample_date, invited, bot_invited, bot_skipped)
		SELECT user_id,
			user_name,
			user_registration,
			user_editcount,
			NOW(),
			0,
			0,
			0
			FROM ptwiki_p.user AS u
				WHERE user_registration > DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 1 DAY),'%s')
				AND user_editcount > 1
				AND user_id NOT IN 
					(SELECT ug_user FROM ptwiki_p.user_groups WHERE ug_group = 'bot')
						AND user_name NOT IN 
							(SELECT REPLACE(log_title,"_"," ") FROM ptwiki_p.logging 
								WHERE log_type = "block" 
									AND log_action = "block" 
									AND log_timestamp >  DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 2 DAY),'%s'))				
	''' % ('%Y%m%d%H%i%s', '%Y%m%d%H%i%s'))
	conn.commit()


def gatherTalkpageData():
#adds in the user talkpage ids for those new users who have talkpages
	cursor.execute('''
UPDATE invited_medicina AS i, (SELECT page_title, page_id, page_namespace, page_is_redirect FROM ptwiki_p.page WHERE page_namespace = 3 AND page_title IN (SELECT REPLACE(user_name, " ", "_") FROM invited_medicina WHERE DATE(sample_date) = DATE(NOW()))) AS p
	SET i.user_talkpage = p.page_id, i.ut_is_redirect = p.page_is_redirect
	WHERE DATE(i.sample_date) = DATE(NOW())
	AND i.user_talkpage IS NULL
	AND p.page_namespace = 3
	AND REPLACE(i.user_name, " ", "_") = p.page_title
	''')
	conn.commit()


def inviteCheck():
#checks to see if any of these potential invitees have been invited already
	cursor.execute('''
	UPDATE invited_medicina AS i, 
		(SELECT iv.user_talkpage FROM invited_medicina AS iv, ptwiki_p.pagelinks AS p 
			WHERE DATE(iv.sample_date) = DATE(NOW()) 
			AND iv.user_talkpage = p.pl_from 
			AND pl_title = "Projetos/Medicina") AS tmp 
		SET i.invited = 1 
			WHERE i.user_talkpage = tmp.user_talkpage
	''')
	conn.commit()
	
	
def buildReport():
	# builds output list for today's newcomer report
	cursor.execute('SELECT id, user_name, user_editcount, invited FROM invited_medicina WHERE date(sample_date) = date(NOW()) AND ut_is_redirect != 1')

	output = []
	rows = cursor.fetchall()
	for row in rows:
		number = row[0]
		user_name = unicode(row[1], 'utf-8')	
		user_editcount = row[2]
		invited = row[3]
		talk_page = '[[User_talk:%s|%s]]' % (user_name, user_name) #localize
		user_contribs = '[[Special:Contributions/%s|contribs]]' % user_name #localize
		table_row = u'''| %d
| %s
| %d
| %s
| %d
|-''' % (number, talk_page, user_editcount, user_contribs, invited)
		output.append(table_row)
	return output	


def publishReport(output):
# prints report to wiki
	try:
		#publish the report
		report = wikitools.Page(wiki, report_title)
		report_text = report_template % ('\n'.join(output),)
		report_text = report_text.encode('utf-8')
		print report_text
		print report_title
	# 	report.edit(report_text, section=1, summary="Automatic daily invitee report generated by [[User:HostBot|HostBot]].", bot=1) #localize
		#log the report
		count = len(output)
		logging.info('Updated daily report with ' + count + ' new editors at ' + curtime)
	except: #some error occurred
		logging.info('ERROR: Could not update daily report at ' + curtime)	


##MAIN##
#first, check if a sample has already been gathered for today
cursor.execute('SELECT * FROM invited_medicina WHERE DATE(sample_date) = DATE(NOW())')
rows = cursor.fetchall()
if rows:
	gatherTalkpageData()  #updates the db with the page_ids of new editors whose talk pages were created by the invite
	buildReport() #updates the report to show who has been invited and who has been skipped
else:
	gatherSample()
	gatherTalkpageData()
# 	inviteCheck() #hasn't been tested because we don't 
	output = buildReport()
	publishReport(output)

cursor.close()
conn.close()
	

