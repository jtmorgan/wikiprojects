#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bot_lib import Collector
from bot_lib import Invite
from wikipedia import Site
from datetime import datetime
#from bot_lib import DAO
import settings

site = Site('pt', 'wikipedia')
categorias = settings.categorias
medicina = Collector(site, categorias)

editores = medicina.get_editors(settings.start_time)

print "Editores encontrados: ", len(editores)
#editores = medicina.load_editors()
medicina.save(editores, "editores")
