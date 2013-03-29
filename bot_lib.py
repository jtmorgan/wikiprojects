#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs, json
import wikipedia, catlib, pagegenerators
import logging
from time import sleep
import settings
import shelve
from datetime import datetime
from urllib import quote

class Collector:
	def __init__(self, site, *categories):
		self.log = False
		self.categories = categories
		self.site = site
		self.pages_set = set()
		self.editors = {}
		self.folder = 'revisions/'

	def get_pages(self):
		'''Retorna as páginas de uma dada categoria: category'''

		for category in self.categories:
			#print category, type(category), len(category)
			print category
			cat = catlib.Category(self.site, category[0])

			pages = pagegenerators.CategorizedPageGenerator(cat)
			for page in pages:
				if wikipedia.Page(self.site, page.title()).namespace() is 0:
					self.pages_set.add(page.title())
		return list(self.pages_set)

	def get_editors(self, start_time=None):
		'''Get the revision history for a given page,
		returns users list with:
			-- User
			-- Data/Timestamp
		It's possible to select users based on edit timestamp,
		just giving a start_time value in timestamp syntax.
		'''

		if len(self.pages_set) is 0:
			self.get_pages()

		for page in self.pages_set:
			page = page.replace(" ", "_")
			if self.log:
				print "Get history for: ", page
			try:
				wpage = wikipedia.Page(self.site, page)
			except Exception, e:
				print "Página não existe - 404"
				if self.log:
					print page
				return list()

			history = wpage.fullVersionHistory()

			if start_time is None:
				for h in history:
					if self.check_user(h[1]) is True:
						if self.editors.has_key(h[1]):
							self.editors[h[1]]['counter'] += 1
							self.editors[h[1]]['edits'].append(datetime.strptime(h[0][0:10], "%Y-%m-%d"))
						else:
							self.editors[h[1]] = {'counter' : 1, 'invited' :  False, 'edits' : list()}
							self.editors[h[1]]['edits'].append(datetime.strptime(h[0][0:10], "%Y-%m-%d"))
			else:
				for h in history:
					if (start_time <= datetime.strptime(h[0][0:10],
					 "%Y-%m-%d") and self.check_user(h[1])):
						if self.editors.has_key(h[1]):
							self.editors[h[1]]['counter'] += 1
							self.editors[h[1]]['edits'].append(datetime.strptime(h[0][0:10], "%Y-%m-%d"))
						else:
							self.editors[h[1]] = {'counter' : 1, 'invited' :  False, 'edits' : list()}
							self.editors[h[1]]['edits'].append(datetime.strptime(h[0][0:10], "%Y-%m-%d"))
			del history
		return self.editors

	def save(self, structure, name):
		print "Salvando: ", name.encode('utf-8')
		db = DAO(name.encode('utf-8'))
		db.insert(structure)
		del db

	def check_user(self, username):
		'''	Return True for human and registered user '''
		bot_dict = ['bot', 'Bot', 'BOT', 'bOt', 'boT', 'b0t', 'BOThe', 'BoT']
		if username is None or username.count('.') >= 3:
			return False
		for bot in bot_dict:
			if username.endswith(bot):
				return False
		return True

	def load_editors(self, dbname):
		db = DAO(dbname.encode('utf-8'))
		self.editors = db.get_editors()
		del db

class Invite:
	def __init__(self, site, editors):
		assert len(editors) > 0, "Nenhum editor foi passado"
		self.editors = editors
		self.site = site
		self.invite = settings.invite_msg
		self.user_discussion_page = settings.user_discussion_page
		self.bot_comment = settings.bot_comment

	def __init__(self, site, filename):
		self.contact_users = settings.contact_users
		self.contact_template = settings.contact_template
		self.filename = filename
		self.editors = DAO(filename)
		self.site = site
		self.invite = settings.invite_msg
		self.user_discussion_page = settings.user_discussion_page
		self.bot_comment = settings.bot_comment

	def inviter(self):
		self.editors.db.writeback = True

		for i, editor in enumerate(self.editors.get_editors()):
			self.send(editor, self.contact_users[i%len(self.contact_users)])
			sleep(1)

	def send(self, editor, contact):
		try:
			#wpage = wikipedia.Page(self.site, self.user_discussion_page + quote(editor))
			#message = wpage.get() + self.invite % (self.contact_template % (contact, contact, contact))
			print editor, self.invite % (self.contact_template % (contact, contact, contact))
			self.editors.db[editor]['invited'] = True
			self.editors.db.sync()
		except Exception, e:
			print "Erro com o usuário ", editor
			raise e
			#wpage.put(message, comment=self.bot_comment)
		
class DAO:
	'''	Database layer	'''
	def __init__(self, dbname, action="W"):
		self.dbname = dbname
		if action is "R":
			self.db = shelve.open(self.dbname+'.db', "r")
		else:
			self.db = shelve.open(self.dbname+'.db', "w")
		self.query_buffer = None

	def __del__(self):
		self.db.close()

	def insert(self, structure):
		for key in structure:
			self.db[key.encode('utf-8')] = structure[key]
		self.db.sync()

	def get_editors(self, threshold=3):
		print "Searching editors with at least " + str(threshold) + " editions"
		if self.query_buffer is not None:
			if raw_input(
				"Query buffer not empty, continue? [y/n]") is "n":
				print "Query is not empty!"
				#return None

		self.query_buffer = []

		for key in self.db:
			if self.db[key]['counter'] >= threshold and not self.db[key]['invited']:
				self.query_buffer.append(key)

		print len(self.query_buffer), "para convidar"
		return self.query_buffer