#

from tool import simple_request
from tool import log_error
import geopy
import json
import os

key_workds=[]

def error(s):
	if not s.endswith('\n'):
		s += '\n'
	print s
	log_error('Dollar_general_error_log.txt', s)

def get_store_info(l):
	res = simple_request(l)
	if res is None:
		return None
	print l
	ks = key_workds+['locationName', 'countryCode', 'stateCode', 'city', 'address1', 'hours', 'postalCode', 'phoneNumber']
	data = {}
	for i in ks:
		data[i] = ''
	
	d = json.loads(res.content)
	for store in d['RESULTS']:
		store = store['store']
		for k in ks:
			try:
				info = store[k]
			except:
				print 'no {} info'.format(k)
			if type(info) == type(dict()):
				t = []
				for i in info:
					t.append(str(i)+' : '+str(info[i]))
				t = ';'.join(t)
				data[k] = t
			elif type(info) == type(list()):
				data[k] = ';'.join(info)
			else:
				data[k] = info
		
		d_collection = []
		for i in key_workds+['locationName', 'countryCode', 'stateCode', 'city', 'address1', 'hours', 'postalCode', 'phoneNumber']:
			d_collection.append(data[i])
		with open('Dollar_General_data.txt', 'a') as f:
			f.write('\t\t\t'.join(d_collection) + '\n')
		
	return True
	
with open('top_200_city.txt', 'r') as f:
	cities = map(lambda x: x.strip(), f.readlines())

k = raw_input("enter keywords to grab extra info(seperate by ','):  ")
key_workds += filter(lambda x: x!='', map(lambda x: x.strip(), k.split(',')))

if not os.path.isfile('Dollar_General_data.txt'):
	with open('Dollar_General_data.txt', 'w') as f:
		f.write('\t\t\t'.join((key_workds+['locationName', 'countryCode', 'stateCode', 'city', 'address1', 'hours', 'postalCode', 'phoneNumber']))+'\n')

done_links = set()
if os.path.isfile('Dollar_General_done_links.txt'):
	with open('Dollar_General_done_links.txt', 'r') as f:
		done_links.update(filter(lambda x: x!='', map(lambda x: x.strip(), f.readlines())))
import time
for city in cities:
	try:
		geo = geopy.Nominatim()
		c_g = geo.geocode(city)
		lat = c_g.latitude
		lon = c_g.longitude
	except:
		try:
			geo = geopy.Nominatim()
			c_g = geo.geocode(city)
			lat = c_g.latitude
			lon = c_g.longitude
		except:
			print ('geocode fail')
			continue
	l = ('http://www.dollargeneral.com/storeLocServ?operation=coSearch&'
	 'lat='+str(lat)+'&'
	 'lon='+str(lon)+'&numResults=100&mnlt='+str(lat-1)+
	 '&mxlt='+str(lat+1)+'&mnln='+str(lon-1)+'&mxln='+str(lon+1)+'&token=DGC&heavy=true')
	if get_store_info(l) is not None:
		done_links.add(l)
		with open('Dollar_General_done_links.txt', 'a') as f:
			f.write(l+'\n')
	