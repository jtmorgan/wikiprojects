#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
	Author: Jxavier - jxavier@wikimedia.org
	License: GPLv2

	Description: Script to search for editors which edited one of the given pages, at file pages.txt
'''

import json
import urllib

#shared resources
server = "http://pt.wikipedia.org/w/"
time_init = '20060501000000'
getter = urllib.URLopener()
users_list = []
bots_dict = ['bot', 'Bot', 'boT', 'BOT']

try:
	f = open('pages.txt')
except Exception, e:
	try:
		import sys
		f = open(sys.argv[1])
	except Exception, e:
		print "Passe um arquivo com os artigos, por favor"
		raise e
	print sys.argv[1]

def check_user(user_name):
	for term in bots_dict:
		if user_name.endswith(term):
	 		return False
	return True

def get_history(page_title):
	'''It uses API for request revisions from a @page_title, for "users" and "anons"

	Check https://www.mediawiki.org/wiki/API for Documentation and Examples       
	'''

	page_title = page_title.replace(' ', '_')
	url = server + 'api.php?action=query&prop=revisions&rvlimit=20&titles=%s&rvprop=user&format=json' % (page_title)
	print url
	try:
		data = getter.open(url)
		rev = json.loads(data.readlines()[0])
		data.close()
		#Test if there's a page with given name
		if rev['query']['pages'].keys()[0] == '-1':
			print "Error 404 - page"
			return
	except Exception, e:
		print "Nao foi possivel buscar o dado"
		return

	#Return the revision part from JSON
	return rev['query']['pages'][rev['query']['pages'].keys()[0]]['revisions']

def rank_users():
	# List all editors, non-anon, which edited one of the given pages
	for page in f:
		page = page.replace('\n', '')
		hist = get_history(page)
		for rev in hist:
			#Exclude anon users
			if not "anon" in rev.keys() and check_user(rev['user']):
				users_list.append(rev['user'])
	f.close()

	#Count edit per user
	users_set = set(users_list)
	users_counter = {}
	for user in users_set:
		print user, users_list.count(user)
		users_counter[user] = users_list.count(user)
	#print "\n", users_counter
rank_users()