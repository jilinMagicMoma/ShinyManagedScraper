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

def info_dragger(soup, content):
	try:
		addr = soup('div', class_='StoreAddress')[0].text
		name = filter(lambda x: x!='', addr.split('\n'))[0]
		addr = ','.join(filter(lambda x: x!='', addr.split('\n'))[1:])
		store_finder = soup('div', class_='StoreFinderDetails')[0]
		col1 = store_finder('div', style="float:left;width:150px")[0]
		col2 = store_finder('div', style="float:right;width:150px")[0]
		col3 = store_finder('div', style="margin:0 165px")[0]
	except IndexError:
		with open('ttttt.html', 'w') as f:
			f.write(content)
		print 'wrote soup recorded'
		return None
	except None:#Exception as e:
		print e
		log_error('parsing_'+error_file, 'name parsing error: '+l)
		return None

	try:
		name, phone, addr, hours, pick_up_site, p_phone, pickup_hours, p_hours = '', '','','','','','',''
		info_tag = ['Store Hours', 'Store Phone', 'At This Location', 'Pharmacy Phone',
		 'Pharmacy Hours', 'Site to StoreSM Hours', 'Photo Center Phone',
		 'Vision Center Phone']
		data = {'Store name':name, 'Store Address':'addr', 'Store Phone':'', 'Store Hours':'', 'At This Location':'', 'Pharmacy Phone':'',
		 'Pharmacy Hours':'', 'Site to StoreSM Hours':'', 'Photo Center Phone':'',
		 'Vision Center Phone':'',}
		
		cur_tag = 'Unknown'
		test_data = []
		for td in col1('td')+col2('td')+col3('td'):
			if 'class' not in td.attrs:
				continue
			if 'BodyMBold' in td['class']:
				print td.text.encode('utf-8').__repr__()
				if td.text.strip() in info_tag:
					cur_tag = td.text.strip()
			elif 'BodyM' in td['class']:
				data[cur_tag] += td.text.strip() + ' '
			else:
				data[cur_tag] += td.text+' '
		for tag in info_tag:
			print tag + ' : ' + data[tag].encode('utf-8').__repr__()
		raw_input()

	except None:#Exception as e:
		print e
		log_error('parsing_'+error_file, 'detail parsing:'+l)
		return None
	return '\t\t\t'.join([name, addr, phone, hours, pick_up_site, pickup_hours, p_phone, p_hours]).encode('utf-8')
			
def parse():
	with open('walmart_store_links.txt', 'r') as f:
		if not os.path.isfile('walmart_data.txt'):
			with open('walmart_data.txt', 'w') as fp:
				fp.write('\t\t\t'.join(['name','addr','phone', 'hours', 'pickup site', 'pickup hours', 'pharmacy phone', 'pharmacy hours']))
		done_links = set()
		try:
			with open('walmart_done_links.txt', 'r') as f:
				done_links.update(map(lambda x: x.strip(), f.readlines()))
		except:
			pass
		for l in f:
			l = l.strip()
			if l in done_links:
				continue
			res = simple_request(l)
			if res is None:
				log_error('parsing_'+error_file, "open error: "+l)
			print l
			soup = BSoup(res.content, 'html5')
			data = info_dragger(soup, res.content)
			
			with open('walmart_data.txt', 'a') as fp:
				fp.write(data)
			with open('walmart_done_links.txt', 'a') as f:
				f.write(l+'\n')
			done_links.add(l)
			
		
if __name__ == '__main__':
	if len(sys.argv) > 1:
		parse()
	else:
		get_walmart_store_infomation()