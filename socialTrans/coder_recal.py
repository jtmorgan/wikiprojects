import MySQLdb
import csv
import sys

conn = MySQLdb.connect(host = 'db67.pmtpa.wmnet', db = 'jmorgan', read_default_file = '~/.my.cnf', use_unicode=1, charset="utf8" )
cursor = conn.cursor()

codes = {'FYI':0,'INVITATION':2,'REQ-COORD-ART':4,'REQ-COORD-NONART':6,'REQ-DISCUSSION':8,'REQ-INFO':10,'REQ-MONITOR':12,'REQ-OPINION':14,'REQ-OTHER':16,'REQ-OTHER-PEOPLE':18,'REQ-PEER-REVIEW':20,'REQ-TASKS':22}

def getRevisions():
	cursor.execute('''
SELECT tp.csie_code_text AS code1, tmp.code2 FROM `stw_all_2006_coded_tp_data` AS tp, (SELECT csie_code_text AS code2, rev_id FROM `stw_all_2006_coded_tp_data` WHERE csi_user = 4 AND valid_codes = 2 and coders = 2 AND csie_code_text NOT IN ("HARD", "INVALID")) AS tmp WHERE tmp.rev_id = tp.rev_id AND tp.csi_user = 5 AND csie_code_text NOT IN ("HARD", "INVALID")
		''')

	rev_list = []
	rows = cursor.fetchall()
	for row in rows:
		coder1 = row[0]
		coder2 = row[1]
		rev_list.append((coder1, coder2))

	return rev_list


#writes a new line of data to the csv
def writeline(revision_list, writer):
	i = 1
	for rev in revision_list:
		csv_row = [0] * 24
		coder1 = rev[0]
		coder2 = rev[1]
		csv_row[codes[coder1]] = 1
		csv_row[codes[coder2]+i] = 1
		print csv_row
		writer.writerow( tuple(csv_row) )

	print open(sys.argv[1], 'rt').read()

# 	try:
# # 		for i in range(len(message_list)):
# 		writer.writerow( (i, data[0], data[1], data[2], data[3], data[4], data[5], data[6]) )
# 	except ValueError:
# 		writer.writerow( (i, "error!") )

##MAIN##
revision_list = getRevisions()
i = 1
f = open(sys.argv[1], 'wt')
writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
writeline(revision_list, writer)



# writer.writerow( ('c1_FYI','WikiProject', 'Talkpage id', 'Revision', 'User id', 'Code', 'Title', 'Message') )
# for item in revision_list:
# 	page_sections = getSectionNumbers(item)
# 	page_sections.sort(reverse=True)
# 	max_section = page_sections[0]
# 	rev_section = [item[1], item[2], max_section]
# 	message_text = getSectionText(rev_section)
# 	message_text = message_text.encode('utf-8')
# 	print message_text
# 	rev_data = format_message(message_text, item)
# 	writeline(rev_data, writer, i)
# 	i+=1
# 	message_list.append(rev_data, writer)
#printing the csv



# print open(sys.argv[1], 'rt').read()
f.close()
cursor.close()
conn.close()