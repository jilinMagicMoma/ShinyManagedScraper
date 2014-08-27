import os
import json
import re
from tool import simple_request
from tool import log_error
from urllib import urlencode
from urlparse import urljoin

city_list = []
with open('50_city_in_us.txt', 'r') as f:
	for line in f:
		c_name, postal, state = line.strip().split('\t')
		city_list.append((c_name, state))

if not os.path.isfile('The Home Depot.txt'):
	with open('The Home Depot.txt', 'w') as f:
		f.write('\t\t\t'.join(['name', 'store#', 'address', 'phone', 'store hour','manager'])+'\n')
		
for city, state in city_list:
	params =   (('callback', 'angular.callbacks._e'),
			('searchParams', '{"radius":100,"sourceAppId":"storefinder","truckRental":false,"penskeRental":false,"propane":false,"toolRental":false,"keyCutting":false,"freeWifi":false,"maxMatches":30,"address":"'+city+', '+state+', USA "}')
			)
	main_link = 'http://www.homedepot.com/StoreFinder/findStores?'

	link = main_link + urlencode(params)
	res = simple_request(link)
	if res is None:
		log_error('home_depot_error_log.txt', link)
		continue
	print city, state
	try:
		info = re.findall(r'angular.callbacks._e[(](.*)[)]', res.content)[0]
		info = json.loads(info)
		for store in info['stores']:
			addr = '{},{},{},{}'.format(store['address'], store['city'], store['state'], store['country'])
			phone = store['phoneNumber']
			manager = store['manager']
			services = []
			for service in store['services']:
				services.append(service['value'])
			services = ','.join(services)
			hours = store['formattedStoreHours']
			name = store['storeName']
			store_id = str(store['storeID'])
			with open('The Home Depot.txt', 'a') as f:
				f.write('\t\t\t'.join([name, store_id, addr, phone, hours, services, manager]).encode('utf-8')+'\n')	
	except Exception as e:
		log_error('home_depot_error_log.txt', link)
		continue