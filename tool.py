import requests

def get_all_city_in_us():
	try:
		with open('all_city_in_us.txt', 'r') as f:
			cities = map(lambda x: x.strip(), f.readlines())
	except Exception as e:
		print 'failt to get all cities'
		return None
	return cities

def simple_request(l):
	try:
		res = requests.get(l)
		if not res.ok:
			return None
		return res
	except Exception as e:
		print 'failt to request {}\n'.format(l)
		return None

def log_error(error_file, msg):
	with open(error_file, 'a') as f:
		print msg
		f.write(msg + '\n')

def done_link_record(record_file, l):
	with open(record_file, 'a') as f:
		f.write(l+'\n')
