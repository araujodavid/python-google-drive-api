'''
Script to check the difference between the contents of two files.
'''
import sys
import json

path_file_1 = sys.argv[1]
path_file_2 = sys.argv[2]

file = open(path_file_1, encoding='utf-8')

data_file_1 = json.load(file)

file.close()

file = open(path_file_2, encoding='utf-8')

data_file_2 = json.load(file)

file.close()

list_names_1 = list()
list_names_2 = list()

with open('list_files_names_1.txt', 'w') as files_names_1:
	for attr, value in data_file_1.items():
		list_names_1.append(value)
		files_names_1.write('%s\n' % value)

with open('list_files_names_2.txt', 'w') as files_names_2:
    for attr, value in data_file_2.items():
    	list_names_2.append(value)
    	files_names_2.write('%s\n' % value)

# asymmetric difference
def asy_diff(list1, list2):
	return list(set(list1) - set(list2))

# symmetric difference
def sym_diff(list1, list2):
	return list(set(list1).symmetric_difference(set(list2)))


diff_1_to_2 = asy_diff(list_names_1, list_names_2)
diff_2_to_1 = asy_diff(list_names_2, list_names_1)

with open('diff_admin_academy.txt', 'w') as diff_file_1_to_2:
    for value in diff_1_to_2:
    	diff_file_1_to_2.write('%s\n' % value)

with open('diff_academy_admin.txt', 'w') as diff_file_2_to_1:
    for value in diff_2_to_1:
    	diff_file_2_to_1.write('%s\n' % value)

