#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
os.system('PYTHONPATH=$PYTHONPATH:~/apps/pywikipedia/')
os.system('export PYTHONPATH')
'''

from bot_lib import Collector
from bot_lib import Invite
from wikipedia import Site
from datetime import datetime
from bot_lib import DAO
import settings

site = Site('pt', 'wikipedia')
categorias = settings.categorias
medicina = Collector(site, categorias)

editores = medicina.get_editors()

print "Editores encontrados: ", len(editores)
#editores = medicina.load_editors()
medicina.save(editores, "editores")