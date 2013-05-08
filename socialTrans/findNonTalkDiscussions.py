import csv
import sys
import re

# message_list = []


# #gets the text of the section
# def getSectionText(rev_sec):
# 	usock = urllib2.urlopen(difftext_url % (rev_sec[0], rev_sec[1], rev_sec[1], rev_sec[2]))
# 	text = usock.read()
# 	usock.close()
# 	soup = bss(text)
# 	msg = soup.api.query.pages.page.revisions.rev
# 	content = msg.string
# 	content = content.strip()
# 	
# 	return content
# 
# #formats the message as a title, body tuple and removes whitespace
# def format_message(txt, item):
# # 	global message_list
# 	title = re.match("\=\=(.*?)\=\=", txt)
# 	ttl = title.group(1)
# 	ttl = ttl.strip()	
# 	txt = re.sub("\=\=(.*?)\=\=", "", txt)
# 	txt = MySQLdb.escape_string(txt)		
# # 	title = ''
# # 	f = txt.readline()
# # 	for index, line in enumerate(f):
# # 		if line.startswith('=='):
# # 			title = txt[index]
# # 	txt = ''.join(f)
# 	item.append(ttl)
# 	item.append(txt)
# 	
# 	return item
# 
# #writes a new line of data to the csv
# def writeline(data, writer, i):
# 	try:
# # 		for i in range(len(message_list)):
# 		writer.writerow( (i, data[0], data[1], data[2], data[3], data[4], data[5], data[6]) )
# 	except ValueError:
# 		writer.writerow( (i, "error!") )

talkers = ['WT:', 'Wikipedia_talk:', 'Talk:', 'discussion', 'discuss', 'Discussion', 'comment']
		
##MAIN##
e = open(sys.argv[1], 'rt')
f = open(sys.argv[2], 'wt')
reader = csv.reader(e)
writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
writer.writerow( ('ID','WikiProject', 'Talkpage id', 'Revision', 'User id', 'Code', 'Title', 'Message') )
for row in reader:
# 	print row[7]
	has_talk = False
	if "REQ-DISCUSSION" in row:
		for x in talkers:
			if x in row[6] or x in row[7]:
				has_talk = True
# 				print "has talk"
		if not has_talk:
			writer.writerow(row)
			print row
	else: pass			

e.close()
f.close()    				
		

# i = 1
# f = open(sys.argv[2], 'wt')
# writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
# writer.writerow( ('ID','WikiProject', 'Talkpage id', 'Revision', 'User id', 'Code', 'Title', 'Message') )
# for item in revision_list:
# 	message_text = getSectionText(rev_section)
# 	message_text = message_text.encode('utf-8')
# 	print message_text
# 	rev_data = format_message(message_text, item)
# 	writeline(rev_data, writer, i)
# 	i+=1
# # 	message_list.append(rev_data, writer)
# #printing the csv
# 
# 
# 
# # print open(sys.argv[1], 'rt').read()
# f.close()
# cursor.close()
# conn.close()
# 
# 
# def copySectionText(sections, url, string):
# 	global guest_profiles
# 	for sec in sections:
# 		usock = urllib2.urlopen(url % (string, sec))
# 		txt = usock.readlines()
# 		usock.close()
# 		del txt[0]
# 		feature = True
# 		for index, line in enumerate(txt):
# 			if line.startswith('|image='):
# 				if len(txt[index]) < 9:
# 					feature = False	
# 			if line.startswith('}}'):
# 				txt[index] = '}}<br/>'
# 		txt = ''.join(txt)
# 		if feature:
# 			guest_profiles.append(txt)
# 
# skip_templates = ['uw-vandalism4', 'uw-socksuspect', 'Socksuspectnotice', 'Uw-socksuspect', 'sockpuppetry', 'Teahouse', 'uw-cluebotwarning4', 'uw-vblock', 'uw-speedy4'] # strings from templates on user talk pages that mean editor should not be invited. Localize.
# 
# def talkpageCheck(user, headers):
# #checks to see if the user's talkpage has any templates that would necessitate skipping
# 	skip = False
# 	try:
# 		tp = wikitools.Page(wiki, 'page_namespace:' + user[0])
# 		pagetxt = unicode(tp.getWikiText(), 'utf8')
# 		for template in skip_templates:
# 			if template in pagetxt:
# 				skip = True
# 		allowed = allow_bots(pagetxt, settings.username)
# 		if not allowed:
# 			skip = True		
# 	except:
# 		logging.info('Invite to ' + user + ' failed on talkpageCheck ' + curtime)
# 	return skip
# 
# 
# def allow_bots(text, user):
# #checks for exclusion compliance, per http://en.wikipedia.org/wiki/Template:Bots
# 	return not re.search(r'\{\{(nobots|bots\|(allow=none|deny=.*?' + user + r'.*?|optout=all|deny=all))\}\}', text, flags=re.IGNORECASE)