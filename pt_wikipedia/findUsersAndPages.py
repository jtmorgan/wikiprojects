#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    WikiProject - Code to search and select user to WikiProject
    Copyright (C) 2012, 2013 - Jonas Xavier

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 2
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
'''

import json, urllib
import wikipedia, catlib, pagegenerators
from datetime import datetime
import json

#Global
archive_file = 'editors.csv'
main_category = "Medicina"
site = wikipedia.Site("pt", "wikipedia")
start_time = datetime.strptime('2013-01-01', "%Y-%m-%d")
bot_dict = ['bot', 'Bot', 'BOT', 'bOt', 'boT', 'b0t', 'BOThe', 'BoT']

def check_user(user_name):
	'''
	Return True for human and registered user
	'''
	if user_name.count('.') >= 3:
		return False
	
	for bot in bot_dict:
		if user_name.endswith(bot):
			return False

	#otherwise
	return True

def get_pages(category, recurse=0):
	'''Retorna as páginas de uma dada categoria: category'''
	page_set = set()
	cat = catlib.Category(site, category)

	pages = pagegenerators.CategorizedPageGenerator(cat, recurse)

	for page in pages:
		if wikipedia.Page(site, page.title()).namespace() is 0:
			page_set.add(page.title())
			#print page.title()
	return page_set

def get_history_users(page_title, start_time=None):
	'''Get the revision history for a given page,
	returns users list with:
		-- User
		-- Data/Timestamp
	It's possible to select users based on edit timestamp,
	just giving a start_time value in timestamp syntax.
	'''

	page_title = page_title.replace(" ", "_")

	try:
		wpage = wikipedia.Page(site, page_title)
	except Exception, e:
		print "Página não existe - 404"
		print page_title
		return set()

	history = wpage.fullVersionHistory()
	users_list = []

	if start_time is None:	
		for h in history:
			if check_user(h[1]):
				users_list.append(h[1])
	else:
		for h in history:
			if start_time <= datetime.strptime(h[0][0:10], "%Y-%m-%d") and check_user(h[1]):
				users_list.append(h[1])

	return users_list

def save_editors(users_doc, toJSON=True):
	import codecs

	f = codecs.open(archive_file, 'w', 'utf-8')
	f.writelines(json.dumps(users_doc))
	f.close()

def main():
	pages_set = get_pages(main_category)
	users_global = {}

	for page in pages_set:
		users_list = get_history_users(page)
		for user in users_list:
			try:
				users_global[user] += 1
			except Exception, e:
				users_global[user] = 1
	
	for u in users_global:
		print u, users_global[u]
	users_global.articles = page_set
	save_data(users_global)

if __name__ == "__main__":
	try:
		main()
	finally:
		wikipedia.stopme()