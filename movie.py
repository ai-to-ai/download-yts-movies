from twisted.internet import reactor
import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.http import FormRequest
import re
from itemadapter import ItemAdapter

import schedule
import time
from datetime import date
import csv

import openpyxl

# class CustomExporter(XlsxItemExporter):
#     def __init__(self, file, **kwargs):
#         super().__init__(file, include_header_row=False, **kwargs)

class MovieScrapy(scrapy.Spider):
	name="Movie"
	base_url = "https://www.ytx.ms"

	page_num = 1
	limit = 1024

	custom_settings={
		"ITEM_PIPELINES": {
			'__main__.CSVPipeline': 100
			},
		"CONCURRENT_REQUESTS":32,
		# "DOWNLOADER_MIDDLEWARES" : {
		# 	'__main__.CustomProxyMiddleware': 350,
		# 	'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 400,
		# }
	}

	# url = "https://www.pfizer.com/Privacy#:~:text=We%20collect%20information%20about%20you,with%20your%20inquiries%20and%20purchases"
	# url = "https://privacycenter.instagram.com/policies/uso/?entry_point=ig_help_center_ccpa_redirect"
	url = "https://yts.mx/browse-movies"
	HEADERS = {
	    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
	                  'Chrome/105.0.0.0 Safari/537.36 OPR/91.0.4516.95',
	    'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
	    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
	              'application/signed-exchange;v=b3',
	    'Accept-Encoding': 'gzip',
	    'Referer': 'https://www.google.com/',
	    'Upgrade-Insecure-Requests': '1'
	}

	def start_requests(self):

		yield scrapy.Request(url=self.url,callback=self.parse_page)

	def parse_page(self, response):
		# print("page_num: ",self.page_num)
		exist = response.xpath('//*[@class="browse-movie-title"]/@href').get(default = "NA")

		movie_links = response.xpath('//a[@class="browse-movie-title" and not(span)]/parent::div/parent::div/a[@class="browse-movie-link"]/@href').getall()
		
		for movie_link in movie_links:
			yield scrapy.Request(url=movie_link, callback=self.parse_movie)

		if exist != "NA":
			self.page_num = self.page_num + 1
			url = self.url + "?page="+str(self.page_num)
			yield scrapy.Request(url=url,callback=self.parse_page)


		# movie_link = response.xpath('//*[@class="browse-movie-link"]/@href').get()
		# yield scrapy.Request(url=movie_link, callback=self.parse_movie)

	def parse_movie(self, response):
		# print(response.text)
		print('')
		item = Item()

		magnet_titles = response.xpath('//a[@rel="nofollow" and contains(@href, "magnet")]/@title').getall()
		
		magnet_link = ""
		for index, title in enumerate(magnet_titles):
			try:
				result = re.search(r'\d+p',title)
				resol = result.group()[0:-1]
				resol = int(resol)
				if resol >= self.limit:
					magnet_link = response.xpath('//a[@rel="nofollow" and contains(@href, "magnet")]/@href').getall()[index]
					item['magnet'] = magnet_link
					yield item
			except:
				pass

		if magnet_link == "":
			magnet_link = response.xpath('//a[@rel="nofollow" and contains(@href, "magnet")]/@href').get(default="")
			item['magnet'] = magnet_link
			yield item

class CSVPipeline(object):
	header = ['magnet']
	f = None
	write = None
	def open_spider(self, spider):

		file_date = today = date.today().isoformat()
		filename = 'magnet.csv'
		self.f = open(filename, 'w',newline='')
		self.writer = csv.writer(self.f)
		self.writer.writerow(self.header)

	def process_item(self, item, spider):
		adapter = ItemAdapter(item)
		row = [adapter['magnet']]
		self.writer.writerow(row)
		return item
	def close_spider(self, spider):
		self.f.close()

class Item(scrapy.Item):
    # define the fields for your item here like:
    magnet = scrapy.Field()

def start_crawl():
	print("Start Crawling...")
	configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
	runner = CrawlerRunner()
	d = runner.crawl(MovieScrapy)
	d.addBoth(lambda _: reactor.stop())
	reactor.run()

start_crawl()


