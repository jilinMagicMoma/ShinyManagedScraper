import urllib
import sys
import os
import re

from bs4 import BeautifulSoup as BSoup
from tool import get_all_city_in_us
from tool import simple_request
from tool import log_error
from urlparse import urljoin

error_file = 'walmart_error_log.txt'
def get_walmart_store_infomation():
	
	for city in get_all_city_in_us():
		l = 'http://www.walmart.com/storeLocator/ca_storefinder_results.do?'
		print city
		params = {'serviceName':'',
				  'rx_title'   :'com.wm.www.apps.storelocator.page.serviceLink.title.default',
				  'rx_dest'    :'%2Findex.gsp',
				  'sfrecords'  :'50',
				  'sfsearch_single_line_address':city}
		
		l = l+urllib.urlencode(params)
		print 

		res = simple_request(l)
		if res is None:
			log_error(error_file, l)
			continue
		soup = BSoup(res.content, 'html5')
		
		link_divs = soup('div', class_='storeDescription')
		links = []
		for div in link_divs:
			try:
				link = urljoin(l, div.h3.a.get('href'))
			except Exception as e:
				continue
			links.append(link)
		
		with open('walmart_store_links.txt', 'a') as f:
			f.write('\n'.join(links))

def info_process(s):
	for i in range(len(s)):
		s[i] = s[i].strip()
		s[i] = s[i].replace(u'\xe2\x80\xa2', '')
		s[i] = s[i].replace('\n', ' ')
		s[i] = ' '.join(filter(lambda x: x!= '', s[i].split()))
	return s
			
def info_dragger(l):
	flg = False
	for i in xrange(5):
		res = simple_request(l)
		if res is None:
			return None
		soup = BSoup(res.content, 'html5')
		try:
			addr = soup('div', class_='StoreAddress')[0].text
			name = filter(lambda x: x!='', addr.split('\n'))[0]
			addr = ','.join(filter(lambda x: x!='', addr.split('\n'))[1:])
			store_finder = soup('div', class_='StoreFinderDetails')[0]
			col1 = store_finder('div', style="float:left;width:150px")[0]
			col2 = store_finder('div', style="float:right;width:150px")[0]
			col3 = store_finder('div', style="margin:0 165px")[0]
			flg = True
			break
		except IndexError:
			print 'retry'
			continue
		except None:#Exception as e:
			print e
			return None
	if not flg:
		return None
	try:
		info_tag = ['Store Phone', 'Store Hours', 'At This Location', 'Site to StoreSM Hours', 
		'Pharmacy Phone', 'Pharmacy Hours', 'Photo Center Phone',
		 'Vision Center Phone']
		data = {'Store name':name, 'Store Address':'addr', 'Store Phone':'', 'Store Hours':'', 'At This Location':'', 'Pharmacy Phone':'',
		 'Pharmacy Hours':'', 'Site to StoreSM Hours':'', 'Photo Center Phone':'',
		 'Vision Center Phone':'',}
		
		cur_tag = 'Unknown'
		test_data = []
		for td in col1('td')+col2('td')+col3('td'):
			if 'class' in td.attrs and 'BodyMBold' in td['class']:
				if td.text.strip() in info_tag:
					cur_tag = td.text.strip()
			elif td.text.strip() != '':
				data[cur_tag] += td.text.strip() + ' '
		store_data = [name, addr]
		for tag in info_tag:
			store_data.append(data[tag])
		store_data = info_process(store_data)

	except None:#Exception as e:
		print e
		return None
	return store_data
			
def parse():
	with open('filtered_walmart_store_links.txt', 'r') as f:
		links = sorted(list(set(map(lambda x: x.strip(), f.readlines()))))
	if not os.path.isfile('walmart_data.txt'):
		tag_name = ['store name','store addr','store phone', 
					 'business hours', 'pickup site', 
					 'pickup hours', 'pharmacy phone', 
					 'pharmacy hours', 'Photo Center Phone', 'Vision Center Phone']
		with open('walmart_data.txt', 'w') as fp:
			fp.write('\t\t\t'.join(tag_name) + '\n')
	done_links = set()
	try:
		with open('walmart_done_links.txt', 'r') as fp:
			done_links.update(map(lambda x: x.strip(), fp.readlines()))
	except:
		pass
	for l in links:
		l = l.strip()
		if l in done_links:
			continue
		print l
		data = info_dragger(l)
		if data is not None:
			with open('walmart_data.txt', 'a') as f:
				f.write('\t\t\t'.join(data).encode('utf-8')+'\n')
			with open('walmart_done_links.txt', 'a') as f:
				f.write(l+'\n')
			done_links.add(l)
		else:
			print 'fail'
			log_error('parsing_'+error_file, 'detail parsing:'+l)
			
		
if __name__ == '__main__':
	if len(sys.argv) > 1:
		parse()
	else:
		get_walmart_store_infomation()