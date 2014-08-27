import os
import pickle
from bs4 import BeautifulSoup as BSoup
from tool import simple_request
from tool import log_error
from urlparse import urljoin

main_locator_page = 'http://www.walgreens.com/storelistings/storesbystate.jsp?requestType=locator'
def get_state_links():
	res = simple_request(main_locator_page)
	if res is None:
		log_error('Walgreens_error_log.txt', main_locator_page)
		return None
	soup = BSoup(res.content, 'html5')
	
	links = {}
	for a in soup('a', title='Click to see all the cities'):
		link = a.get('href')
		links[link[-2:]] = urljoin(main_locator_page, link)
	return links

def get_city_links(state_links):
	city_links = []
	for state_abbr in state_links:
		print state_abbr
		link = state_links[state_abbr]
		res = simple_request(link)
		if res is None:
			log_error('Walgreens_error_log.txt', link)
			continue
		soup = BSoup(res.content, 'html5')
		content_div = soup('div', class_='padLt25px mrgRt25px padTop20px')[0]

		for a in content_div('a', class_='no_underline'):
			info = a.text.strip()
			if info == '':
				continue
			if info.split(',')[-1].strip() == state_abbr:
				city_links.append((info.split(',')[0], urljoin(main_locator_page, a.get('href'))))
	return city_links

def get_store_link(city_links):
	store_links = []
	for link_pair in city_links:
		city = link_pair[0]
		link = link_pair[1]
		print city
		res = simple_request(link)
		if res is None:
			log_error('Walgreens_error_log.txt', link)
			continue
		soup = BSoup(res.content, 'html5')
		content_div = soup('div', class_='padLt25px mrgRt25px padTop20px')[0]
		for p in content_div('p', class_='float-left wid300 nopad'):
			for a in p('a', class_='no_underline'):
				store_links.append((city, urljoin(main_locator_page,a.get('href'))))
	return store_links

def get_store_detail(store_link):
	city = store_link[0]
	store_link = store_link[1]
	res = simple_request(store_link)
	if res is None:
		return None
	
	name,address,phone,store_hour,store_id,pharmacy_hour='','','','','',''
	
	soup = BSoup(res.content, 'html5')
	try:
		content_div = soup('div', class_='mrgRt20px brdBtmSld')[0]
	except:
		return None # content div is the basis for data grabbing in this script
	
	try:
		name = content_div('p', class_='float-left def_txt padBtm10px headtitle2')[0].text
	except:
		pass
	try:
		address += content_div('p', itemprop='streetAddress')[0].text+' '
	except:
		pass
	try:
		address += content_div('span', itemprop='addressLocality')[0].text + ' '
	except:
		pass
	try:
		address += content_div('span', itemprop='addressRegion')[0].text + ' '
	except:
		pass
	try:
		address += content_div('span', itemprop='postalCode')[0].text
	except:
		pass
	try:
		phone = content_div('p', itemprop='telephone')[0].text
	except:
		pass
	try:
		store_id = filter(lambda x: x.text.strip().startswith('Store #:'), content_div('p', class_='nopad'))
		store_id = store_id[0].text.split(':')[-1]
	except:
		pass
	try:
		time_div = soup('div', class_='padTop10px wid350 float-left')[0]
		day_p = time_div('p', class_='nopad wid55 float-left')
		hour_p = time_div('p', class_='nopad wid100 float-left')
		
		for i in range(len(day_p)):
			store_hour += day_p[i].text.strip() + ' : '+hour_p[i].text.strip() +'; '
	except Exception as e:
		pass
	try:
		pharmacy_div = soup('div', class_='padTop20px wid370 float-left')[0]
		day_p = pharmacy_div('p', class_='nopad wid55 float-left')
		hour_p = pharmacy_div('p', class_='nopad wid100 float-left')
		
		for i in range(len(day_p)):
			pharmacy_hour += day_p[i].text.strip() + ' : ' + hour_p[i].text.strip() + '; '
	except:
		pass
	
	return [name,address,phone,store_hour,store_id,pharmacy_hour, city]
	
if __name__ == '__main__':
	if os.path.isfile('walgreens_state_link.pickle'):
		with open('walgreens_state_link.pickle', 'r') as f:
			links = pickle.load(f)
	else:
		links = get_state_links()
		with open('walgreens_state_link.pickle', 'w') as f:
			pickle.dump(links, f)
	
	if os.path.isfile('walgreens_city_link.pickle'):
		with open('walgreens_city_link.pickle', 'r') as f:
			links = pickle.load(f)
	else:
		links = get_city_links(links)
		with open('walgreens_city_link.pickle', 'w') as f:
			pickle.dump(links, f)
	
	if os.path.isfile('walgreens_store_link.pickle'):
		with open('walgreens_store_link.pickle', 'r') as f:
			links = pickle.load(f)
	else:
		links = get_store_link(links)
		with open('walgreens_store_link.pickle', 'w') as f:
			pickle.dump(links, f)
	
	done_links = set()
	if os.path.isfile('Walgreens_done_links.txt'):
		with open('Walgreens_done_links.txt', 'r') as f:
			done_links.update(map(lambda x: x.strip(), f.readlines()))
	if not os.path.isfile('Walgreens.txt'):
		with open('Walgreens.txt', 'w') as f:
			f.write('\t\t\t'.join(['name','address','phone','store hour','store#','pharmacy hour', 'city'])+'\n')
	links = sorted(list(set(links)))
	for link in links:
		print link[0]
		if link[1] in done_links:
			continue
		info = get_store_detail(link)
		if info is None:
			print 'error:',link
			log_error('Walgreens_error_log.txt', link[1])
			continue
		with open('Walgreens.txt', 'a') as f:
			f.write('\t\t\t'.join(info).encode('utf-8')+'\n')
		with open('Walgreens_done_links.txt', 'a') as f:
			f.write(link[1]+'\n')
		done_links.add(link[1])
	
	
	
				