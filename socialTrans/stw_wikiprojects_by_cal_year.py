#! /usr/bin/env python2.7
# Copyright 2013 Jtmorgan

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
conn = MySQLdb.connect(host = 'db67.pmtpa.wmnet', db = 'enwiki', read_default_file = '~/.my.cnf', use_unicode=1, charset="utf8" )
cursor = conn.cursor()

#GLOBAL VARIABLES
# years = [2012, 2011, 2010, 2009, 2008, 2007, 2006, 2005, 2004, 2003, 2002]
years = [2012]

start_date = "20%s0101"
end_date = "20%s1231"

#QUERIES
first_edit_query = '''select min(rev_id), min(rev_timestamp) from enwiki.revision as r, enwiki.page as p where r.rev_page = p.page_id and p.page_namespace in (4,5) and p.page_title like "%s%%"
'''

update_start_query = '''UPDATE jmorgan.stw_all_wikiprojects SET pfirst_rev = %d, pfr_timestamp = %s WHERE project = "%s" AND ppage_is_redirect = 0
'''

project_page_query = '''SELECT project, ppage_id, substr(pfr_timestamp, 1, 4) FROM jmorgan.stw_all_wikiprojects WHERE ppage_is_redirect = 0
'''

activity_query = '''INSERT IGNORE INTO jmorgan.stw_active_wikiprojects_by_cal_year
SELECT "%s", %d, tmp.revs, tmp.first_rev, tmp.last_rev, %d, %d
		FROM (SELECT min(rev_id) as first_rev, max(rev_id) as last_rev, count(rev_id) as revs
	FROM enwiki.revision AS r, enwiki.page AS p
         WHERE (p.page_title = "%s" OR p.page_title LIKE "%s/%%")
         AND p.page_namespace IN (4,5)
         AND r.rev_timestamp BETWEEN "%s000000" AND "%s000000"
         AND p.page_id = r.rev_page
         AND rev_user NOT IN (SELECT ug_user
          FROM enwiki.user_groups
          WHERE ug_group = 'bot')
          AND r.rev_user_text NOT LIKE "%%Bot" AND r.rev_user_text NOT LIKE "%%bot")
          AS tmp'''


def getProjectList(cursor):
	projs = []
	cursor.execute(project_page_query)
	rows = cursor.fetchall()
	for row in rows:
		proj = (row[0], row[1], int(row[2]))
# 		proj = row[0]
		projs.append(proj)

	return projs


def getProjectFirstEdits(cursor, projects):
	for project in projects:
		cursor.execute(first_edit_query % (project,))
		row = cursor.fetchone()
		first_rev = row[0]
		first_time = row[1]
		cursor.execute(update_start_query % (first_rev, first_time, project))
		conn.commit()

def getProjectActivity(i, start_date, end_date, years, cursor, projects, activity_query):
	"""
	gets the edits per project & them into a db table
	"""
	split_start = start_date % (str(years[i])[-2:])
	split_end = end_date % (str(years[i])[-2:])
	for project in projects:
		if project[2] <= years[i]:
			cursor.execute(activity_query % (project[0], project[1], years[i], years[i], project[0], project[0], split_start, split_end))
			conn.commit()
		else:
			continue

#MAIN
projects = getProjectList(cursor)
# getProjectFirstEdits(cursor, projects)


i = 0
while i < len(years):
	getProjectActivity(i, start_date, end_date, years, cursor, projects, activity_query)
	i += 1
cursor.close()
conn.close()


