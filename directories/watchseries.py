"""
Backend file for interfacing with online TV episode aggregators
This backend is for watchseries
"""

import re
import urllib.parse
import urllib.request

id = "watchseries"

SEARCH_URL = "http://www.watchseries.to/search/{}"
SHOW_URL = "http://www.watchseries.to/serie/{}" # e.g. how_i_met_your_mother
EPISODE_URL = "http://www.watchseries.to/episode/{}.html" # e.g. how_i_met_your_mother_s1_e1
VIDEO_AD_URL = "http://www.watchseries.to/open/cale/{}.html" # e.g. 1289651

SEARCH_RE = re.compile(r"\<a href=\"/serie/(.+?)\" title=\"(.+?)\"\>")
SHOW_RE = re.compile(r"\<a href=\"/episode/(.+?)\.html\"\>") # the_mentalist_s1_e1

EPISODE_LINK_RE = re.compile(r"\<a target=\"_blank\" href=\"/open/cale/(\d+)\.html\" class=\"buttonlink\" title=\"(.+?)\"")
VIDEO_LINK_RE = re.compile(r"\<a href=\"(.+?)\" class=\"myButton\"\>")

def search(query):
	results = {}

	req = urllib.request.urlopen(SEARCH_URL.format(query))
	data = req.read().decode("utf-8")

	for m in SEARCH_RE.finditer(data):
		results[m.group(1)] = m.group(2)

	return results


def getShow(showID): # showID -> how_i_met_your_mother
	showID = urllib.parse.quote(showID)
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

	results[0] = results[0][1:]

	return results

def resolveLink(linkID): # linkID -> 1289651
	req = urllib.request.urlopen(VIDEO_AD_URL.format(linkID))
	data = req.read().decode("utf-8")

	# <a href="http://daclips.in/ealrjx6zvcnt" class="myButton">
	match = VIDEO_LINK_RE.search(data)
	return match.group(1)

def getEpisode(episodeID): # episodeID -> how_i_met_your_mother_s2_e12
	episodeID = urllib.parse.quote(episodeID)
	results = {}
	hostlinks = []

	req = urllib.request.urlopen(EPISODE_URL.format(episodeID))
	data = req.read().decode("utf-8")

	# <a target="_blank" href="/open/cale/1190676.html" class="buttonlink" title="daclips.in"
	for m in EPISODE_LINK_RE.finditer(data):
		source = m.group(2)
		linkID = int(m.group(1))
		if source in results:
			results[source].append(linkID)
		else:
			results[source] = [linkID]

	return results


	