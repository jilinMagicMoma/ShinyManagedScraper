import json
import os
import re
from tool import simple_request
from tool import log_error
from bs4 import BeautifulSoup as BSoup
import pickle

def error(s):
	if not s.strip().endswith('\n'):
		s += '\n'
	print s
	log_error('Sears_error_log.txt', s)

def info_process(s):
	s = s.strip()
	s = s.replace('\t', ' ')
	s = s.replace('\n', ' ')
	s = s.replace(u'\u2013', ' ')
	s = ' '.join(filter(lambda x: x!='', s.split()))
	
	return s
	
def get_store_detail(l):
	res = simple_request(l)
		
	if res is None:
		error('Request Fail: {}'.format(l))
		return None
	
	content = res.content
	json_string = re.findall(r'angular.callbacks._3[(](.*)[)];', content)
	if len(json_string) == 0:
		error('No info found: {}'.format(l))
		return None
	json_string = json_string[0]
	d = json.loads(json_string)

	d = d['showstorelocator']
	
	if 'getstorelocator' not in d.keys():
		error('Server got no info for {}'.format(l))
		return None
	d = d['getstorelocator']
	d = d['storelocations']
	d = d['storelocation']
#['country','state','city','zip code','name',
# 'address','phone','store hour','service']		
	
	for store in d:
		data = {'country':'','state':'','city':'','zip code':'','name':'',
			'address':'','phone':'','store hour':'','service':[]}
		try:
			data['country'] = info_process(store['storeaddress']['country'])
			data['state']   = info_process(store['storeaddress']['state'])
			data['city']    = info_process(store['storeaddress']['city'])
			data['address'] = info_process(store['storeaddress']['streetaddress'])
			data['zip code'] = info_process(store['storeaddress']['zipcode'])
		except:
			print 'no address found'
		try:
			data['name'] = store['storename']
		except:
			print 'no store name found'
		
		try:
			data['phone'] = store['storephones']['storephone']
		except:
			print 'no phone number found'
		
		try:
			for service in store['storeservices']['storeservice']:
				data['service'].append(info_process(service['servicename']))
		except KeyError:
			print 'no service info found {}'.format(data['name'])
		data['service'] = ','.join(data['service'])
		
		try:
			store_number = store['storenumber']
			l = 'http://www.searsauto.com/stores/'+store_number
			
			res = simple_request(l)
			if res is not None:
				soup = BSoup(res.content, 'html5')
				time_table = soup('div', itemtype='http://schema.org/LocalBusiness')[0]
				time = {}
				for div in time_table('div', itemprop='openingHours'):
					time[div['content'].split()[0]] = div('div', class_='time')[0].text
				for i in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
					data['store hour'] += i+' '+ info_process(time[i].strip())+';'
			else:
				l = ('http://www.sears.com/stores/'+store['storeaddress']['fullstatename'].lower().replace(' ', '-')+
					'/'+data['city'].lower().replace(' ', '-')+'/'+store_number+'.html')
				res = simple_request(l)
				if res is None:
					error('fail to get hours: {}'.format(l))
				else:
					soup = BSoup(res.content, 'html5')
					time_table = soup('table', class_='divTable')[0]
					for tr in time_table('tr', itemprop='openingHoursSpecification'):
						data['store hour'] += info_process(tr.text)+';'
		except:
			print 'no hour found'

		#data = {'country':'','state':'','city':'','zip code':'','name':'',
		#	'address':'','phone':'','store hour':'','service':[]}
		print ('\t\t\t'.join([data['country'], data['state'], data['city'], data['zip code'], data['name'],
			   data['address'], data['phone'], data['store hour'], data['service']]).encode('utf-8')+'\n')
		with open('Sears.txt', 'a') as f:
			f.write('\t\t\t'.join([data['country'], data['state'], data['city'], data['zip code'], data['name'],
			   data['address'], data['phone'], data['store hour'], data['service']]).encode('utf-8')+'\n')
		
	
#country,state,city,zip code,name,address,phone,store hour,service

if __name__ == '__main__':
	with open('top_200_city_postal.txt', 'r') as f:
		postals = map(lambda x: x.strip(), f.readlines())
	if not os.path.isfile('Sears.txt'):
		with open('Sears.txt', 'w') as f:
			f.write('\t\t\t'.join(['country','state','city','zip code','name',
				'address','phone','store hour','service'])+'\n')
	done_links = set()
	if os.path.isfile('Sears_done_links.txt'):
		with open('Sears_done_links.txt', 'r') as f:
			done_links.update(map(lambda x: x.strip(), f.readlines()))
	
	for postal in postals:
		print postal
		city, postal = postal.split('\t')[0], postal.split('\t')[1]
		l = ('http://webservices.sears.com/shcapi/v2/sears/jsonp/'
			 'storeInformation/zip/'+postal+'?appID=jmeter_test&'
			 'authID=abcdefg$$$$$$$$123456789&mileRadius=100&callback=angular.callbacks._3'
			)
		get_store_detail(l)
		done_links.add(l)
		with open('Sears_done_links.txt', 'a') as f:
			f.write(l+'\n')
			