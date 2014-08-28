

import sys

with open(sys.argv[1], 'r') as f:
	lines = f.readlines()
	
if len(lines) != len(set(lines)):
	print 'duplicate {}'.format(len(lines) - len(set(lines)))
else:
	print 'no dup'
	

new_lines = []
for i in lines:
	if i not in new_lines:
		new_lines.append(i)
		
with open('dup_filtered.txt', 'w') as f:
	f.write(''.join(new_lines))