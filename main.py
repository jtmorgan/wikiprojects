#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bot_lib import Collector
from bot_lib import Invite
from wikipedia import Site
from datetime import datetime
from bot_lib import DAO

site = Site('pt', 'wikipedia')
categorias = ['Medicina']
medicina = Collector(site, categorias)
editores = medicina.get_editors()

to_invite = []

for editor in editores:
	if editores[editor] > 1:
		to_invite.append(editor)
medicina.save(to_invite, "to_invite")
invite = Invite(site)
l = invite.load_editors('revisions/to_invite.json')