import os
import requests
from tool import log_error
from bs4 import BeautifulSoup as BSoup

def error(s):
	if not s.endswith('\n'):
		s+='\n'
	print s
	log_error('Bestbuy_error_log.txt', s)


def get_best_buy_store_links():
	l = 'http://www.bestbuy.com/nex/store/search?code='
	with open('city_postal.txt') as f:
		postals = map(lambda x: x.strip(), f.readlines())
	postals = map(lambda x: x.split('\t')[1], postals)

	done_links = set()
	try:
		with open('bestbuy_done_links.txt', 'r') as f:
			done_links.update(map(lambda x: x.strip(), f.readlines()))
	except IOError:
		pass
	user_agent = {'User-agent': 'Mozilla/5.0'}
	for postal in postals:
		print postal
		try:
			res = requests.get(l+postal, headers=user_agent)
			if not res.ok:
				error('fail to open{}'.format(l+postal))
				continue
		except:
			error('fail to open{}'.format(l+postal))
			continue
			
		soup = BSoup(res.content, 'html5')
		try:
			content_div = soup('div', id='store_locator_left_nav')[0]
		except IndexError:
			continue
		store_links = []
		for a in content_div('a', target='new'):
			if 'href' in a.attrs:
				store_links.append(a.get('href'))
		
		with open('bestbuy_store_links.txt', 'a') as f:
			f.write('\n'.join(store_links)+'\n')
		
		with open('bestbuy_done_links.txt', 'a') as f:
			f.write(l+postal+'\n')
		done_links.add(l+postal)
def modi(s):
	s = s.strip()
	s = s.replace('\t', ' ')
	s = s.replace('\n', ' ')
	
	return s
def get_best_but_store_detail(link):
	user_agent = {'User-agent': 'Mozilla/5.0'}
	try:
		res = requests.get(link, headers= user_agent)
		if not res.ok:
			return None
	except Exception as e:
		return  None
	
	soup = BSoup(res.content, 'html5')
	data = {'country':'US','state':'','city':'','zip code':'','name':'','address':'','phone':'',
			         'store hour':'','email':'','service':[],'trade_in':''}
	
	name_h1 = soup('h1', id='site_title')[0]
	data['name'] = name_h1('a')[0].text
	addr_div = soup('div', rel='v:adr')[0]
	data['address'] = addr_div('span', property='v:street-address')[0].text
	data['city'] = addr_div('span', property='v:locality')[0].text
	data['state'] = addr_div('span', property='v:region')[0].text
	data['zip code'] = addr_div('span', property='v:postal-code')[0].text
	data['phone'] = addr_div('span', typeof='v:Tel v:Home')[0].text
	
	try:
		data['email'] = addr_div('a', rel='v:email')[0].text
	except Exception as e:
		print 'no email found'
	
	try:
		left_div = soup('div', class_='column left')[0]
		trade_in_img = left_div('img', alt='Trade-in Policy')[0]
		trade_in_p = trade_in_img.next.next
		if trade_in_p.name == 'p' and trade_in_p.text != '':
			data['trade_in'] = trade_in_p.text
	except Exception as e:
		print 'No trade in info found'
	
	service_div = soup('div', class_='store_services')[0]
	for ul in service_div('ul'):
		for li in ul('li'):
			data['service'].append(li.text)
	data['service'] = ','.join(data['service'])
	hour_ul = soup('ul', id='store_hours')[0]
	tag_about = ['#storehours_mon', '#storehours_tue', '#storehours_wed', 
	 '#storehours_thu', '#storehours_fri', '#storehours_sat',
	 '#storehours_sun']
	
	for about in tag_about:
		li = hour_ul('li', about=about)[0]
		data['store hour'] += 'wed: '+li('span', class_='open')[0].text + ' - ' + li('span', class_='close')[0].text
	
	
	return [data['country'], data['state'], data['city'], data['zip code'], data['name'],
			data['address'], data['phone'], data['store hour'], data['email'], data['service'],
			data['trade_in']
			]
			
	
		
if __name__ == '__main__':
	if not os.path.isfile('Best Buy.txt'):
		with open('Best Buy.txt', 'w') as f:
			f.write('\t\t\t'.join(['country','state','city','zip code','name','address','phone',
			         'store hour','email','service','trade_in'])+'\n')
	if not os.path.isfile('bestbuy_store_links.txt'):
		get_best_buy_store_links()
	
	with open('bestbuy_store_links.txt', 'r') as f:
		store_links = map(lambda x: x.strip(), f.readlines())
		
	done_links = set()
	try:
		with open('bestbuy_done_links.txt', 'r') as f:
			done_links.update(map(lambda x: x.strip(), f.readlines()))
	except:
		pass
	
	for link in store_links:
		if link in done_links:
			continue
		print link
		try:
			data = get_best_but_store_detail(link)
		except:
			error('to be reviewed: {}'.format(link))
			continue
		if data is None:
			error('fail to connect: {}'.format(link))
			continue
		with open('Best Buy.txt', 'a') as f:
			f.write('\t\t\t'.join(data).encode('utf-8')+'\n')
		with open('bestbuy_done_links.txt', 'a') as f:
			f.write(link+'\n')
		done_links.add(link)

