"""
Backend file for interfacing with online TV episode aggregators
This test backend is currently set up to use watchseries
"""

import html.parser
import re
import urllib.request

id = "watchseries"

SEARCH_URL = "http://www.watchseries.to/search/{}"
SHOW_URL = "http://www.watchseries.to/serie/{}" # e.g. how_i_met_your_mother

class searchParser(html.parser.HTMLParser):
	position = 0 # -1 -> nowhere, 1 -> in table, 2 -> in td, 3 -> in Link
	interest = 0
	results = {}
	def handle_starttag(self, tag, attrs):
		if tag == "table":
			self.position = 1
		elif tag == "td" and self.position == 1:
			for attr in attrs:
				if attr[0] == "style" and attr[1] == "padding-left: 10px;":
					self.position = 2
		elif tag == "a" and self.position == 2:
			# attrs shoudl be in the following form:
			# [('href', '/serie/how_i_met_your_mother'), ('title', 'How I Met Your Mother')]
			self.results[attrs[0][1][7:]] = attrs[1][1]
			self.position = 3

	def handle_endtag(self, tag):
		if tag == "a" and self.position == 3:
			self.position = 2
		elif tag == "td" and self.position == 2:
			self.position = 1
		elif tag == "table":
			self.position = 0

	def handle_data(self, data):
		if self.position > 2:
			print(self.position)
			print(data)
		if self.position == 4:
			self.results.append(data)

	def getResults(self):
		return self.results


def search(query):
	req = urllib.request.urlopen(SEARCH_URL.format(query))
	data = req.read().decode("utf-8")

	p = searchParser()
	p.feed(data)
	return p.getResults()

def getShow():
	# Ideally, getShow would return a list of lists of episode links
	pass

def getEpisode():
	pass
