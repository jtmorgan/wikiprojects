#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bot_lib import Invite
from wikipedia import Site
from datetime import datetime
import settings

site = Site('pt', 'wikipedia')

print "Buscando editores"
convite = Invite(site, "editores")
convite.inviter()