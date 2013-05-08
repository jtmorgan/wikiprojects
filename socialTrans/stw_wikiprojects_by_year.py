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
years = [2012, 2011, 2010, 2009, 2008, 2007, 2006, 2005, 2004, 2003, 2002]
# years = [2010, 2009]

split_date = "20%s0718"

#QUERIES
range_query = '''select s.start_date, e.end_date
					from (select min(rev_id) as start_date from enwiki.revision where rev_timestamp LIKE "%s%%") as s, (select max(rev_id) as end_date from enwiki.revision where rev_timestamp LIKE "%s%%") as e'''

activity_query_old = '''INSERT INTO jmorgan.stw_active_wikiprojects_by_year
SELECT tmp.project, tmp.edits, tmp.redirect, %d, %d, %d, %d
		FROM (SELECT SUBSTRING_INDEX(page_title, '/', 1) AS project,
       SUM((SELECT COUNT(*)
         FROM enwiki.revision
         WHERE page_id = rev_page
         AND rev_id BETWEEN %d AND %d
         AND rev_user NOT IN
          (SELECT ug_user
          FROM enwiki.user_groups
          WHERE ug_group = 'bot')
         AND rev_user NOT IN
          (SELECT user_name
          FROM enwiki.user
          WHERE user_name IN ('%%bot', '%%Bot'))
       )) AS edits,
       (SELECT page_is_redirect
       FROM page
       WHERE page_namespace = 4
       AND page_title = project) AS redirect
       FROM enwiki.page
WHERE (page_title LIKE 'WikiProject\_%%'
  OR page_title LIKE 'WikiAfrica')
AND page_namespace BETWEEN 4 AND 5
AND page_is_redirect = 0
GROUP BY project) AS tmp
WHERE tmp.edits >= 365'''

activity_query = '''INSERT INTO jmorgan.stw_active_wikiprojects_by_year
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

# activity_query = '''INSERT INTO jmorgan.stw_active_wikiprojects_by_year
# SELECT "%s", %d, tmp.revs, tmp.first_rev, tmp.last_rev, %d, %d
# 		FROM (SELECT min(rev_id) as first_rev, max(rev_id) as last_rev, count(rev_id) as revs
# 	FROM enwiki.revision AS r, enwiki.page AS p
#          WHERE (p.page_title = "%s" OR p.page_title LIKE "%s/%%")
#          AND p.page_namespace IN (4,5)
#          AND r.rev_timestamp BETWEEN "%s000000" AND "%s000000"
#          AND p.page_id = r.rev_page
#          AND rev_user NOT IN (SELECT ug_user
#           FROM enwiki.user_groups
#           WHERE ug_group = 'bot')
#           AND r.rev_user_text NOT LIKE "%%Bot" AND r.rev_user_text NOT LIKE "%%bot")
#           AS tmp'''


project_page_query = '''SELECT project, ppage_id, substr(pfr_timestamp, 1, 4) FROM jmorgan.stw_all_wikiprojects WHERE ppage_is_redirect = 0
'''
project_page_query_2 = '''SELECT project, ppage_id, substr(pfr_timestamp, 1, 4) FROM jmorgan.stw_all_wikiprojects WHERE ppage_is_redirect = 0 and project in (select a.page_title from jmorgan.stw_currently_active_wikiprojects as a, jmorgan.stw_all_wikiprojects as y where y.ppage_is_redirect = 0 and y.project = a.page_title and  a.page_title not in (select distinct project from jmorgan.stw_active_wikiprojects_by_year))'''

project_page_query_3 = '''SELECT project, ppage_id, substr(pfr_timestamp, 1, 4) FROM jmorgan.stw_all_wikiprojects WHERE project not like "WikiProject%%"'''

project_page_query_4 = '''SELECT project FROM jmorgan.stw_all_wikiprojects WHERE project not like "WikiProject%%"'''

first_edit_query = '''select min(rev_id), min(rev_timestamp) from enwiki.revision as r, enwiki.page as p where r.rev_page = p.page_id and p.page_namespace in (4,5) and p.page_title like "%s%%"
'''

update_start_query = '''UPDATE jmorgan.stw_all_wikiprojects SET pfirst_rev = %d, pfr_timestamp = %s WHERE project = "%s" AND ppage_is_redirect = 0
'''

def getProjectActivity_old(i, split_date, years, cursor, range_query, activity_query):
	"""
	gets the edits per project & them into a db table
	"""
	split_start = split_date % (str(years[i])[-2:])
	split_end = split_date % (str(years[i-1])[-2:])
	cursor.execute(range_query % (split_start, split_end))
	row = cursor.fetchone()
	start_rev = row[0]
	end_rev = row[1]
	cursor.execute(activity_query % (start_rev, end_rev, years[i], years[i-1], start_rev, end_rev))
	conn.commit()

def getProjectList(cursor):
	projs = []
	cursor.execute(project_page_query_3)
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

def getProjectActivity(i, split_date, years, cursor, projects, activity_query):
	"""
	gets the edits per project & them into a db table
	"""
	split_start = split_date % (str(years[i])[-2:])
	split_end = split_date % (str(years[i-1])[-2:])
	for project in projects:
		if project[2] <= years[i-1]:
			cursor.execute(activity_query % (project[0], project[1], years[i], years[i-1], project[0], project[0], split_start, split_end))
			conn.commit()
		else:
			continue

#MAIN
projects = getProjectList(cursor)
# getProjectFirstEdits(cursor, projects)


i = 1
while i < 11:
	getProjectActivity(i, split_date, years, cursor, projects, activity_query)
	i += 1
cursor.close()
conn.close()


