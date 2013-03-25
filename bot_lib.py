#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs, json
import wikipedia, catlib, pagegenerators
import sqlite3 as sql
import logging
from time import sleep

class DAO:
	'''	Database layer	'''
	def __init__(self):
		self.db_schema = "CREATE TABLE editors(editor_name varchar(15) PRIMARY KEY,edit_count INTEGER, invited BOOLEAN);"
		self.db_name = "editors"
		self.db = sql.connect(self.db_name + ".db")
		self.c = self.db.cursor()

	def insert_editors(self, editors):
		for key, editor in editors:
			self.c.execute("INSERT INTO "+self.db_name+" values(?, ?, ?)",  (key, editor, 0))
		print "Inserting editors data"

	def get_editors(self):
		self.c.execute("SELECT editor_name FROM " + self.db_name + 
			"WHERE invited=0")
		editors_raw = self.c.fetchall()
		editors = []
		for editor in editors:
			editors.append(editor)
		return editors

class Collector:
	def __init__(self, site, *categories):
		self.log = False
		self.categories = categories
		self.site = site
		self.pages_set = set()
		self.editors = {}
		self.folder = 'revisions/'
		self.db = DAO()

	def get_pages(self):
		'''Retorna as páginas de uma dada categoria: category'''

		for category in self.categories:
			#print category, type(category), len(category)
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
				return set()

			history = wpage.fullVersionHistory()
			self.save(history, "history_" + page)
			editors_list = []

			if start_time is None:
				for h in history:
					if self.check_user(h[1]) is True:
						try:
							self.editors[h[1]] += 1
						except Exception, e:
							self.editors[h[1]] = 1
			else:
				for h in history:
					if (start_time <= datetime.strptime(h[0][0:10],
					 "%Y-%m-%d") and self.check_user(h[1])):
						try:
							self.editors[h[1]] += 1
						except Exception, e:
							self.editors[h[1]] = 1
			del history
		return self.editors

	def save(self, structure, filename):
		f = codecs.open(self.folder + filename + ".json", 'w', 'utf-8')
		f.writelines(json.dumps(structure))
		f.close()

	def check_user(self, username):
		'''	Return True for human and registered user '''
		bot_dict = ['bot', 'Bot', 'BOT', 'bOt', 'boT', 'b0t', 'BOThe', 'BoT']
		if username is None or username.count('.') >= 3:
			return False
		for bot in bot_dict:
			if username.endswith(bot):
				return False
		return True

	def feed_db(self):
		self.db.insert_editors(self.editors)

class Invite:
	def __init__(self, site, editors):
		assert len(editors) > 0, "Nenhum editor foi passado"
		self.editors = editors
		self.site = site
		self.invite = u'{{subst:convite-medicina|~~~~}}'
		self.user_discussion_page = u'Usuário(a)_Discussão:'
		self.bot_comment = u'Edição automática de teste feita pelo wikiprojetosbot :)'

	def __init__(self, site, filename):
		self.editors = []
		self.filename = filename
		self.site = site
		self.invite = u'{{subst:convite-medicina|~~~~}}'
		self.user_discussion_page = u'Usuário(a)_Discussão:'
		self.bot_comment = u'Edição automática de teste feita pelo wikiprojetosbot :)'

	def inviter(self):
		for editor in self.editors:
			wpage = wikipedia.Page(self.site, self.user_discussion_page + editor)
			message = wpage.get() + self.invite
			wpage.put(message, comment=self.bot_comment)
			
			#wait 3 second to send next invite and don't overload server
			sleep(3)

	def load_editors(self, filename):
		editors = codecs.open(filename, 'r', 'utf-8')
		editors = editors.readlines()
		self.editors = editors
		return json.loads(editors[0])

	def load_editors(self):
		editors = codecs.open(self.filename, 'r', 'utf-8')
		editors = editors.readlines()
		self.editors = editors
		return json.loads(editors[0])