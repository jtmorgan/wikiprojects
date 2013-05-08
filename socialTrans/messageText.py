import MySQLdb
import csv
import sys
import urllib2
import re
from BeautifulSoup import BeautifulStoneSoup as bss

conn = MySQLdb.connect(host = 'db67.pmtpa.wmnet', db = 'jmorgan', read_default_file = '~/.my.cnf', use_unicode=1, charset="utf8" )
cursor = conn.cursor()

##global variables and output templates
diffsec_url = u'http://en.wikipedia.org/w/api.php?action=parse&pageid=%s&oldid=%s&prop=sections&format=xml'

difftext_url = u'http://en.wikipedia.org/w/api.php?action=query&prop=revisions&pageids=%s&rvprop=content&rvstartid=%s&rvendid=%s&rvlimit=1&rvsection=%s&format=xml'

# message_list = []

# gets the hosts who are nn the breakroom, and newly active from the database table
def getRevisions():
	cursor.execute('''
		SELECT
		page_title, talkpage_id, rev_id, rev_user, `code`
		FROM stw_wp_discussion_sample
		where `code` is not null
		and `code` != "INVALID";
		''')

	rev_list = []
	rows = cursor.fetchall()
	for row in rows:
		page_title = row[0]
		page = row[1]
		revision = row[2]
		user = row[3]
		coded_as = row[4]
		rev_list.append([page_title, page, revision, user, coded_as])
	
	return rev_list

#gets the sections on the page at the given revision
def getSectionNumbers(item):
	page_secs = []
	usock = urllib2.urlopen(diffsec_url % (item[1], item[2]))
	sections = usock.read()
	usock.close()
	soup = bss(sections, selfClosingTags = ['s'])
	for x in soup.findAll('s'):
		try:
			page_secs.append(int(x['index']))
		except ValueError:	
			continue
	return page_secs

#gets the text of the section
def getSectionText(rev_sec):
	usock = urllib2.urlopen(difftext_url % (rev_sec[0], rev_sec[1], rev_sec[1], rev_sec[2]))
	text = usock.read()
	usock.close()
	soup = bss(text)
	msg = soup.api.query.pages.page.revisions.rev
	content = msg.string
	content = content.strip()
	
	return content

#formats the message as a title, body tuple and removes whitespace
def format_message(txt, item):
# 	global message_list
	title = re.match("\=\=(.*?)\=\=", txt)
	ttl = title.group(1)
	ttl = ttl.strip()	
	txt = re.sub("\=\=(.*?)\=\=", "", txt)
	txt = MySQLdb.escape_string(txt)		
# 	title = ''
# 	f = txt.readline()
# 	for index, line in enumerate(f):
# 		if line.startswith('=='):
# 			title = txt[index]
# 	txt = ''.join(f)
	item.append(ttl)
	item.append(txt)
	
	return item

#writes a new line of data to the csv
def writeline(data, writer, i):
	try:
# 		for i in range(len(message_list)):
		writer.writerow( (i, data[0], data[1], data[2], data[3], data[4], data[5], data[6]) )
	except ValueError:
		writer.writerow( (i, "error!") )
		
##MAIN##
revision_list = getRevisions()
i = 1
f = open(sys.argv[1], 'wt')
writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
writer.writerow( ('ID','WikiProject', 'Talkpage id', 'Revision', 'User id', 'Code', 'Title', 'Message') )
for item in revision_list:
	page_sections = getSectionNumbers(item)
	page_sections.sort(reverse=True)
	max_section = page_sections[0]
	rev_section = [item[1], item[2], max_section]
	message_text = getSectionText(rev_section)
	message_text = message_text.encode('utf-8')
	print message_text
	rev_data = format_message(message_text, item)
	writeline(rev_data, writer, i)
	i+=1
# 	message_list.append(rev_data, writer)
#printing the csv



# print open(sys.argv[1], 'rt').read()
f.close()
cursor.close()
conn.close()