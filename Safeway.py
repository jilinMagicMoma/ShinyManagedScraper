#-*- coding: utf-8 -*-
import os
from tool import simple_request
from tool import log_error
from bs4 import BeautifulSoup as BSoup
from urllib import urlencode

postals = set()
with open('city_postal.txt', 'r') as f:
	postals.update(map(lambda x: x.strip().split('\t')[1], f.readlines()))
postals = sorted(list(postals))

if not os.path.isfile('Safeway_data.txt'):
	with open('Safeway_data.txt', 'w') as f:
		f.write('\t\t\t'.join(['country','state','city','zip code','name','address',
				               'phone','store hour','gas hour'])+'\n')
done_postal = set()
try:
	with open('Safeway_done_links.txt', 'r') as f:
		done_postal.update(map(lambda x: x.strip(), f.readlines()))
except IOError:
	pass
for postal in postals:
	if postal in done_postal:
		continue
	print postal
	
	l = 'http://hosted.where2getit.com/safeway/ajax?&'
	store_param = {'xml_request':('<request><appkey>5D7395E2-BFE9-11DE-B770-BEE374652C6E</appkey>'
	                        '<formdata id="locatorsearch"><events><where><eventstartdate><ge>now()</ge></eventstartdate>'
							'</where><limit>2</limit></events><dataview>store_default</dataview>'
							'<geolocs><geoloc><addressline>'+postal+'</addressline><longitude></longitude><latitude></latitude>'
							'</geoloc></geolocs><searchradius>100</searchradius><limit>2000</limit>'
							'<where><closed><distinctfrom>1</distinctfrom></closed><fuelparticipating>'
							'<distinctfrom>1</distinctfrom></fuelparticipating><bakery><eq></eq></bakery>'
							'<deli><eq></eq></deli><floral><eq></eq></floral><liquor><eq></eq></liquor>'
							'<meat><eq></eq></meat><pharmacy><eq></eq></pharmacy><produce><eq></eq></produce>'
							'<jamba><eq></eq></jamba><seafood><eq></eq></seafood><starbucks><eq></eq></starbucks>'
							'<video><eq></eq></video><fuelstation><eq></eq></fuelstation>'
							'<dryclean><eq></eq></dryclean><dvdplay_kiosk><eq></eq></dvdplay_kiosk>'
							'<coinmaster><eq></eq></coinmaster><wifi><eq></eq></wifi><bank><eq></eq></bank>'
							'<seattlesbestcoffee><eq></eq></seattlesbestcoffee>'
							'<beveragestewards><eq></eq></beveragestewards><photo><eq></eq></photo>'
							'<wu><eq></eq></wu><debi_lilly_design><eq></eq></debi_lilly_design></where></formdata>'
							'</request>')}
	'''
	gas_param = {'xml_request':('<request><appkey>5D7395E2-BFE9-11DE-B770-BEE374652C6E</appkey>'
								'<formdata id="locatorsearch"><events><where><eventstartdate><ge>now()</ge></eventstartdate></where>'
								'<limit>2</limit></events><dataview>store_default</dataview><geolocs><geoloc><addressline>'+postal+'</addressline>'
								'<longitude></longitude><latitude></latitude></geoloc></geolocs><searchradius>100</searchradius><limit>2000</limit>'
								'<where><closed><distinctfrom>1</distinctfrom></closed><fuelparticipating><distinctfrom></distinctfrom>'
								'</fuelparticipating><bakery><eq></eq></bakery><deli><eq></eq></deli><floral><eq></eq></floral>'
								'<liquor><eq></eq></liquor><meat><eq></eq></meat><pharmacy><eq></eq></pharmacy><produce><eq></eq></produce>'
								'<jamba><eq></eq></jamba><seafood><eq></eq></seafood><starbucks><eq></eq></starbucks>'
								'<video><eq></eq></video><fuelstation><eq>1</eq></fuelstation><dryclean><eq></eq></dryclean>'
								'<dvdplay_kiosk><eq></eq></dvdplay_kiosk><coinmaster><eq></eq></coinmaster><wifi><eq></eq></wifi><bank><eq></eq>'
								'</bank><seattlesbestcoffee><eq></eq></seattlesbestcoffee><beveragestewards><eq></eq></beveragestewards>'
								'<photo><eq></eq></photo><wu><eq></eq></wu><debi_lilly_design><eq></eq></debi_lilly_design></where></formdata>'
								'</request>')}
	gas_link = l+urlencode(gas_param) # not used in current version
'''
	store_link = l+urlencode(store_param)
	
	
	res = simple_request(store_link)
	if res is None:
		print 'error: {}'.format(postal)
		log_error('Safeway_error_log.txt', postal+'\n')
		continue
	
	soup = BSoup(res.content, 'xml')
	response = soup('response', code='1')
	if len(response) < 1:
		continue
	for poi in response[0]('poi'):
		data = {'country':'','state':'','city':'','zip code':'','name':'','address':'',
				'phone':'','store hour':'','gas hour':''}
		try:
			data['name'] = poi('name')[0].text
			data['country'] = poi('country')[0].text
			data['city'] = poi('city')[0].text
			data['state'] = poi('state')[0].text
			data['zip code'] = poi('postalcode')[0].text
			data['address'] = ','.join(filter(lambda x: x.strip() != '', [poi('address1')[0].text, poi('address2')[0].text]))
			data['phone'] = poi('phone')[0].text
			data['store hour'] = poi('storehours1')[0].text
			data['gas hour'] = poi('hoursgas')[0].text
		except Exception as e:
			log_error('Safeway_error_log.txt', 'content getting process: '+postal+'\n')
			continue
		for k in data:
			data[k] = data[k].strip()
			data[k] = data[k].replace('\t', ' ')
			data[k] = data[k].replace('\n', ' ')
			data[k] = data[k].replace(u'<br />', ' ')
			
		
		with open('Safeway_data.txt', 'a') as f:
			f.write('\t\t\t'.join([data['country'],data['state'],data['city'],data['zip code'],data['name'],data['address'],
				               data['phone'],data['store hour'],data['gas hour']]).encode('utf-8')+'\n')
	with open('Safeway_done_links.txt', 'a') as f:
		f.write(postal+'\n')
	done_postal.add(postal)
	
