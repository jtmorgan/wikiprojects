import MySQLdb
import csv
import sys
import urllib2
import re
from BeautifulSoup import BeautifulSoup as bs

wiki = wikitools.Wiki(settings.apiurl)
wiki.login(settings.username, settings.password)

conn = MySQLdb.connect(host = 'db67.pmtpa.wmnet', db = 'jmorgan', read_default_file = '~/.my.cnf', use_unicode=1, charset="utf8" )
cursor = conn.cursor()


difftext_url = u'http://en.wikipedia.org/w/index.php?diff=%s&diffonly=1'

# message_list = []

# gets the revision's we're interested in checking
def getRevisions():
	cursor.execute("SELECT rev_id FROM stw_wp_discussion_sample_2006 limit 20")

	rev_list = []
	rows = cursor.fetchall()
	for row in rows:
		rev = str(row[0])
		print rev	
		rev_list.append(rev)
	return rev_list

#gets the sections on the page at the given revision
def checkForNewSection(item):
	print item
	newSec = True
	url = difftext_url % item
	print url
	
	usock = urllib2.urlopen(url)
	text = usock.read()
	usock.close()
	soup = bs(text)
	check = soup.findAll('td','diff-addedline')
	checklist = [str(i) for i in check]
	print checklist
	if any('==' in s for s in checklist):
		newSec = False 
	return newSec
		
##MAIN##
revision_list = getRevisions()
print revision_list
for item in revision_list:
	newSec = checkForNewSection(item)
	if not newSec:
		print ("this is not a new section: " + item)
		

cursor.close()
conn.close()