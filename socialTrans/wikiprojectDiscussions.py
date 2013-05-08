#! /usr/bin/env python

# Copyright 2012 Jtmorgan
 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import MySQLdb

conn = MySQLdb.connect(host = 'db67.pmtpa.wmnet', db = 'jmorgan', read_default_file = '~/.my.cnf', use_unicode=1, charset="utf8" )
cursor = conn.cursor()

#as of 2/4/2013, this has been updated for the 2006 sample
cursor.execute('''
SELECT
talkpage_id
from jmorgan.stw_currently_active_wikiprojects
where 2006_sample = 1;
''')

wp_list = []

rows = cursor.fetchall()
for row in rows:
	wp_list.append(str(row[0]))


for item in wp_list:
	proj = item
# 	print proj
	cursor.execute(''' 
	insert into jmorgan.stw_wp_discussion_sample_2006 
	(page_title, page_id, talkpage_id, rev_id, rev_timestamp, rev_user, rev_user_text, rev_comment) 	
			select page_title,
			page_id, 
			rev_page, 
			rev_id, 
			rev_timestamp,
			rev_user, 
			rev_user_text,
			rev_comment 
			from enwiki.revision as r, 
			jmorgan.stw_currently_active_wikiprojects as w 
				where r.rev_id between 64376695 and 145330963
				and r.rev_page = %s 
				and r.rev_page = w.talkpage_id 
				and r.rev_comment not like "%s"
				and r.rev_comment not like "" 
				and r.rev_user not in 
					(select ug_user from enwiki.user u, enwiki.user_groups g where u.user_id = g.ug_user and g.ug_group = "bot") 
			order by rand() limit 20;
	''' % (proj, "/*%"))
	conn.commit()

# 	data = cursor.fetchall()
# 	print data


# i = iter(wp_list)
# cursor.execute('''
# insert into jmorgan.currently_active_wp_discussion_sample 
# 	(page_title, talkpage_id, rev_id, rev_user, rev_comment) 
# 		select page_title, 
# 		rev_page, 
# 		rev_id, 
# 		rev_user, 
# 		rev_comment 
# 		from enwiki.revision as r, 
# 		jmorgan.currently_active_wikiprojects as w 
# 			where r.rev_id > 440031144 
# 			and r.rev_page = %s 
# 			and r.rev_page = w.talkpage_id 
# 			and r.rev_comment like "%new section" 
# 			and r.rev_user not in 
# 				(select ug_user from enwiki.user u, enwiki.user_groups g where u.user_id = g.ug_user and g.ug_group = "bot") 
# 		order by rand() limit 20;
# ''') % wp_list[i]
# conn.commit()

cursor.close()
conn.close()
	

