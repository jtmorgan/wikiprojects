#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs, json
import wikipedia, catlib, pagegenerators
import logging, os
from time import sleep
import settings
import shelve
from datetime import datetime
from urllib import quote
from userlib import User

logging.basicConfig(filename='logs/bot.log',level=logging.INFO)

class Collector:
	def __init__(self, site, *categories):
		self.log = False
		self.categories = categories[0]
		self.site = site
		self.pages_set = set()
		self.editors = {}
		#self.folder = 'revisions/'
		self.bot_set = self.get_bot_list()

	def get_pages(self):
		'''Retorna as páginas de uma dada categoria: category'''
		#print type(self.categories)
		for c in self.categories:
			print c
			cat = catlib.Category(self.site, c)
			pages = pagegenerators.CategorizedPageGenerator(cat)
			for page in pages:
				if wikipedia.Page(self.site, page.title()).namespace() is 0:
					self.pages_set.add(page.title())

		DAO('pages').insert_list(list(self.pages_set))
		
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
				logging.info("Collector: Erro com página: " + page)
				print "Página não existe - 404"
				if self.log:
					print page
				return list()

			history = wpage.fullVersionHistory(revCount=200)

			if start_time is None:
				for h in history:
					if self.check_user(h[1]):
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
		db.insert_dict(structure)
		del db

	def check_user(self, username):
		u = User(self.site, username)
		if username is None or u.isAnonymous() or u.isBlocked():
			return False
		elif username in self.bot_set:
			return False
		#print username, "passed"
		return True

	def get_bot_list(self):
		if os.path.isfile('bot_list.db') is True:
			print "Bot list found: " + 'bot_list.db'
			return DAO('bot_list').get_list()
		else:
			bot_set = []
			cat = catlib.Category(self.site, u"!Robôs")
			pages = pagegenerators.CategorizedPageGenerator(cat)
			for page in pages:
				if wikipedia.Page(self.site, page.title()).namespace() is 2:
					bot_set.append(page.title().split(":")[1])
			print u"A Wikipedia possui ", len(bot_set), u" robôs"
			bots = DAO('bot_list')
			bots.insert_list(bot_set)
			del bots
			return bot_set

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
		for i, editor in enumerate(self.editors.get_editors()):
			self.send(editor, self.contact_users[i%len(self.contact_users)])
			sleep(1)

	def send(self, editor, contact):
		try:
			wpage = wikipedia.Page(self.site, self.user_discussion_page + quote(editor))
			message = wpage.get() + self.invite % (self.contact_template % (contact, contact, contact))
			print editor, self.invite % (self.contact_template % (contact, contact, contact))
			wpage.put(message, comment=settings.bot_comment)
			print editor, " convidado"
			self.editors.db[editor]['invited'] = True
			self.editors.db[editor]['invite_date'] = datetime.today()
			self.editors.db.sync()
		except Exception, e:
			print "Erro com o usuário ", editor
			logging.info("Invite: Erro ao convidar: " + editor)
			#wpage.put(message, comment=self.bot_comment)

class DAO:
	'''	Database layer	'''
	def __init__(self, dbname):
		self.dbname = dbname
		self.db = shelve.open(self.dbname+'.db', writeback=True)
		self.query_buffer = None

	def __del__(self):
		self.db.close()

	def insert_dict(self, structure):
		for key in structure:
			self.db[key.encode('utf-8')] = structure[key]
			print key, "inserted in db"
		self.db.sync()

	def insert_list(self, structure):
		self.db['pages'] = structure
		self.db.sync()

	def get_list(self):
		return self.db.items()

	def get_editors(self, threshold=1):
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
