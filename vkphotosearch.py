#!/usr/bin/python3
# vkphotosearch.py
# Version: 1.0
# License: Apache License Version 2.0
# Author: Georgii Starostin
# E-mail: blackdiverx@gmail.com
# Site: https://BlackDiver.net
import argparse
from urllib.request import urlopen
from urllib.request import urlretrieve
import math
import time
import os
import sys
import time
from calendar import timegm
# Функция преобразования даты в Unixtime
def convert_date(date, type):
	if type == True:
		date = '00-00-00-'+date+'GMT'
	if type == False:
		date = '23-59-59-'+date+'GMT'
	return timegm(time.strptime(date,'%H-%M-%S-%d-%m-%Y%Z'))
# Функция создания поискового запроса
def url_data(lat,long,radius,offset,count,fromdate,todate):
	url = 'https://api.vk.com/method/photos.search.xml?lat='+str(lat)+'&long='+str(long)+'&count='+str(count)+'&radius='+str(radius)+'&offset='+str(offset)
	if fromdate != None:
		url+='&start_time='+str(convert_date(fromdate, True))
	if todate != None:
		url+='&end_time='+str(convert_date(todate, False))
	return url
# Функция поиска фотографий и пользователей
def photo_search(lat,long,radius,badusers):
	count = 1
	res = []
	url = url_data(lat,long,radius,0,1,fromdate,todate)
	data = urlopen(url)
	import xml.etree.ElementTree as ET
	tree = ET.parse(data)
	photos_count = int(tree.findall('count')[0].text)
	iterations = math.ceil(photos_count/1000)
	for i in range(0,iterations):
		count = 1000
		offset = i*1000
		print('Search Photo. Iteration: '+str(i+1)+' of '+str(iterations))
		url = url_data(lat,long,radius,offset,count,fromdate,todate)
		data = urlopen(url)
		tree = ET.parse(data)
		photo_id = tree.findall('src_big')
		vk_id = tree.findall('owner_id')
		for i, element in enumerate(photo_id):
			if badusers == False:
				b_user = vk_id[i].text
				if b_user[0] != '-':
					row = [vk_id[i].text,photo_id[i].text]
					res.append(row)
			else:
				row = [vk_id[i].text,photo_id[i].text]
				res.append(row)
				
	return res
# Процедура сохранения списка найденных пользователей
def users_txt(res, folder):
	f = open(folder+'/users.csv', 'w')
	for i, el in enumerate(res):
		f.write(res[i][0] + '\n')
	f.close()
# Процедура закачки найденных фотографий
def download_photos(res,folder,s):
	for i, el in enumerate(res):
		filename = res[i][0]+'_'+res[i][1].rsplit('/',1)[1]
		print('Download '+filename+' ('+str(i+1)+' of '+str(len(res))+')')
		if s == True:
			if os.path.exists(folder+'/'+res[i][0]):
				urlretrieve(res[i][1], folder+'/'+res[i][0]+'/'+filename)
			else:
				os.makedirs(folder+'/'+res[i][0])
				urlretrieve(res[i][1], folder+'/'+res[i][0]+'/'+filename)
		else:
			urlretrieve(res[i][1], folder+'/'+filename)
# Процедура запуска программы
def run(lat,long,radius,fromdate,todate,badusers,u,d,s):
	res=photo_search(lat,long,radius,badusers)
	folder = 'Report-'+time.strftime("%d-%m-%Y-%H-%M-%S")
	os.makedirs(folder)
	if u == True:
		users_txt(res, folder)
	if d == True:
		download_photos(res,folder,s)

if __name__ == '__main__':
	# Получение параметров из командной строки
	parser = argparse.ArgumentParser()
	parser.add_argument('-lat', type=float, help='Latitude (Example: 55.7538528)')
	parser.add_argument('-long', type=float, help='Longitude (Example: 37.6196378)')
	parser.add_argument('-radius', type=int, default=50, help='Radius (Default: 50m)')
	parser.add_argument('-fromdate', default=None, help='Search photos from date (Example: 05-06-2017)')
	parser.add_argument('-todate', default=None, help='Search photos to date (Example: 05-06-2017)')
	parser.add_argument('-badusers', action='store_true', default=False, help='Include deleted users')
	parser.add_argument('-u', action='store_true', default=False, help='Save users ID into CSV')
	parser.add_argument('-d', action='store_true', default=False, help='Download user photos')
	parser.add_argument('-s', action='store_true', default=False, help='Save user photos in separated folders')
	args =  parser.parse_args()
	lat = args.lat # Широта
	long = args.long # Долгота
	radius = args.radius # Радиус
	fromdate = args.fromdate # С какой даты искать
	todate = args.todate # По какую дату искать
	badusers = args.badusers # Учитывать удаленных и заблокированных пользователей
	u = args.u # Сохранять список найденных пользователей
	d = args.d # Скачивать фотографии
	s = args.s # Сортировать фотографии по папкам
	if (lat == None) or (long == None) or (u == False and d == False):
		print('Parameters missing')
		parser.print_help()
		sys.exit(0)
	run(lat,long,radius,fromdate,todate,badusers,u,d,s)