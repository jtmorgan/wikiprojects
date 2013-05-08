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

import MySQLdb

conn = MySQLdb.connect(host = 'db67.pmtpa.wmnet', db = 'jmorgan', read_default_file = '~/.my.cnf', use_unicode=1, charset="utf8" )

cursor = conn.cursor()

#gets all questions from between 1 and 2 weeks ago
cursor.execute('''
SELECT talkpage_id, rev_id, rev_user_text, rev_comment
	from jmorgan.stw_wp_discussion_sample AS q
	where q.`code` IS NOT NULL AND `ignore` IS NULL
''')

#gets all questioner responses, host answers, and first answer date
rows = cursor.fetchall()
for row in rows:
	page = row[0]
	rev = row[1]
	user = row[2]
	user = MySQLdb.escape_string(user)
	comment = row[3]
	com_sub = comment[:-12]
	com_sub.strip()
# 	com_sub = "/* " + com_sub + " */"
	com_sub = MySQLdb.escape_string(com_sub)
	print com_sub

	cursor.execute ('''
			INSERT INTO stw_wp_disc_self_response (talkpage_id, parent_rev, resp_id, resp_user, resp_user_text, resp_comment, resp_timestamp) SELECT rev_page, %s, rev_id, rev_user, rev_user_text, rev_comment, rev_timestamp FROM enwiki.revision WHERE rev_page = %s AND rev_id > %s AND rev_comment LIKE '%s' AND rev_user_text = "%s" and rev_minor_edit = 0
			''' % (rev, page, rev, com_sub + "%", user))
	conn.commit()

cursor.close()
conn.close()


