"""
Backend file for interfacing with online TV episode aggregators
This test backend is currently set up to use watchseries
"""

import re
import urllib.request

id = "watchseries"

SEARCH_URL = "http://www.watchseries.to/search/{}"
SHOW_URL = "http://www.watchseries.to/serie/{}" # e.g. how_i_met_your_mother
EPISODE_URL = "http://www.watchseries.to/episode/{}.html" # e.g. how_i_met_your_mother_s1_e1
VIDEO_AD_URL = "http://www.watchseries.to/open/cale/{}.html" # e.g. 1289651

SEARCH_RE = re.compile(r"\<a href=\"/serie/(.+?)\" title=\"(.+?)\"\>")
SHOW_RE = re.compile(r"\<a href=\"/episode/(.+?)\.html\"\>") # the_mentalist_s1_e1



def search(query):
	results = {}

	req = urllib.request.urlopen(SEARCH_URL.format(query))
	data = req.read().decode("utf-8")

	for m in SEARCH_RE.finditer(data):
		results[m.group(1)] = m.group(2)

	return results


def getShow(showID): # showID -> e.g. how_i_met_your_mother
	results = []

	req = urllib.request.urlopen(SHOW_URL.format(showID))
	data = req.read().decode("utf-8")

	SHOWNAME_RE = re.compile(r"{}_s(\d+)_e\d+".format(showID))

	for m in SHOW_RE.finditer(data):
		match = SHOWNAME_RE.search(m.group(1))
		season = int(match.group(1))
		if len(results) < season:
			results.append([m.group(1)])
		else:
			results[season - 1].append(m.group(1))

	return results

def getEpisode():
	pass
