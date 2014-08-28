
import geopy
import json
import os
from tool import simple_request
from tool import log_error

def error(s):
	if not s.strip().endswith('\n'):
		s += '\n'
	print s
	log_error('Macy_error_log.txt',s)

def get_Store_detail(l):
		res = simple_request(l)
		if res is None:
			error('fail to connect {}'.format(l))
			return None
		info_dict = json.loads(res.content)
		
		try:
			stores = info_dict['stores']['store']
		except KeyError:
			error('no store tag found in returned json')
			return None
		
		for store in stores:
			data = {'country':'','state':'','city':'','zip code':'',
					'name':'','address':'','phone':'','store hour':'','features':''}
			data['country'] = store['address']['countryCode']
			data['state']   = store['address']['state']
			data['city']    = store['address']['city']
			data['zip code'] = store['address']['zipCode']
			data['address'] = ','.join([store['address']['line1'], store['address']['line2'],
							  store['address']['line3']])
			data['name'] = store['name']
			try:
				data['phone'] = store['phoneNumber']
			except:
				print 'no phone'
				pass
			try:
				data['features'] = ','.join(store['features']['feature'])
			except:
				print 'no features'
				pass
			for hour in store['schedule']['workingHours']:
				try:
					data['store hour'] += hour['operationDate']+':'+hour['openTime']+'-'+hour['closeTime']+';'
				except:
					pass
			with open("Macy's.txt", 'a') as f:
				f.write('\t\t\t'.join([data['country'], data['state'], data['city'], data['zip code'], data['address'],
						 data['name'], data['phone'], data['features']]) +'\n')

if __name__ == '__main__':
	if not os.path.isfile("Macy's.txt"):
		with open("Macy's.txt", 'w') as f:
			f.write('\t\t\t'.join(['country', 'state', 'city', 'zip code', 'address', 'name', 'phone', 'features'])+'\n')
							 
	done_links = set()
	if os.path.isfile('macy_done_links.txt'):
		with open("macy_done_links.txt", 'r') as f:
			done_links.update(map(lambda x: x.strip(), f.readlines()))
	
	with open('top_200_city.txt', 'r') as f:
		cities = map(lambda x: x.strip(), f.readlines())

	for city in cities:
		print city
		lat, lon = '',''
		try:
			geo = geopy.Nominatim()
			g = geo.geocode(city)
			lat, lon = g.latitude, g.longitude
		except:
			try:
				geo = geopy.GoogleV3()
				g = geo.geocode(city)
				lat, lon = g.latitude, g.longitude
			except:
				error('geo not found of {}'.format(city))
				continue

		l = ('http://www1.macys.com/api/store/v2/stores?'
			 'latitude='+str(lat)+'&longitude='+str(lon))
		get_Store_detail(l)
		done_links.add(city)
		with open('macy_done_links.txt', 'a') as f:
			f.write(city+'\n')