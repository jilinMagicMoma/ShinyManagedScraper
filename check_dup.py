

import sys

with open(sys.argv[1], 'r') as f:
	lines = f.readlines()
	
if len(lines) != len(set(lines)):
	print 'duplicate {}'.format(len(lines) - len(set(lines)))
else:
	print 'no dup'