"""
watch-tv - watch some TV pulled from various online sources
"""

# Included stuff
from flask import Flask
from flask import render_template
from flask import request

import datetime
import html
import importlib
import json
import pkgutil
import re
import urllib.parse
import urllib.request


# Custom stuff
from config import *

import directories
import video_hosts

app = Flask(__name__)
directoryList = []
vidHostList = []


defaultArt = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASwAAADICAMAAABlASxnAAAABGdBTUEAALGPC/xhBQAAAAFzUkdCAK7OHOkAAAASUExURczMzFVVVf7+/qmpqX19feXl5WEFUTsAAAKCSURBVHja7dztTuMwEAVQJ2O//ytvSRGULWQnacJKmXN+IRUqceU7jfPR1gAAAAAAAAAAAAAAAAAAgNr6Sb97SZFPoMewtNKxjqGIyd+bmqxaRLKEs6ySS0sJN8z4qVlY2SIqYb6ISrihiF0JH1u2/nKXVbaISrihiKZ7fmmFEqbTUsINB1tKmF9aSrhhxjvZkD/YUsJ8EU33DUVUwnwRlTBfRCXcUEQlzC8tJcynpYQbdj1dCdNLSwk3zHglTBWxvwl3Nvx7XU2feggkl5S81kf79J0umHRWN6LJZyWt53n1c1aa+GTMPyt5EBErXdvrqp+XMZ2i3Ax/aW1dMqzpJLOwhCUsYf1SWL2/n5D51vJa9bD629HR+DgOHSvur68eo107rLjns+kA/+Yjrv4ec1QIa+f+JZ7+vkBYu++4euzdchmoQFi7z64/hHWrZJQIa/f1wP4Z1j3zAmGNA8Lqy9sUCGv3PxePbzDmJqxkWFHj07AfEVaVAX9IWFUGfB+vvsN9ZbUKYcURYVUZ8MeEVWTAx0E1DGElw5qKhNUM+F8O623ACysfVlPDzE56/vqOwhKWsP7LzIrlApGwMitr+SGElVlZ8b4jF1Y6rGm23cmvLGGlBvwys5qwkp+GEWN21iG53VnulRBWcm9Y46B0/zn4EJaw1sI66Lphd0U6F9ZUZbsz7a5h/+sIfggrH9Zc4f6sl8NqZbY7R9z5F8unaoUa9gNuk7yZK2x3dg+t+BJWje3Oci35lZH18dBc1Hgc5eERlLYWXbTP51I8u+NBJ2EJS1jCuoCznr6/ZFgnfa/DuOjX3Z3xjSHjsl8NOJ+gAQAAAAAAAAAAAAAAAAAA8J0/uz0RyXTAZWUAAAAASUVORK5CYII="
defaultPoster = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASwAAAHCCAMAAABi7QS1AAAABGdBTUEAALGPC/xhBQAAAAFzUkdCAK7OHOkAAAAMUExURczMzFZWVvn5+ZaWljBNENAAAAJySURBVHja7dzJbiMxDEBBtfT//xzH+xab6qidQKxCjp7DPJCCvJYCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAhNpGj50zVut4aDVa0Qcu1SIu4ceJFV1ESxgfLUvYUcsSxhfREsZHa7eEYkVHyxLGL1uWsGMRDVZ8EbWKL6Il7FhEgxVfRK3io2UJO2oZrPgiLgYrPFqWsKOWJYxftgxWfLS06jjjLWF8EQ1WfBG16lhESxhfRIPVsYje+4pt4p4lfB9quWhNkBeplnt6hVPtCfPsYP+JNPFWakV38HBwyXOvvmDXBtFKrW1aTXqkbRRrzieRYokl1j+N1a6V09+JWMdXE57dPk9/D5fSF93mjlVW3Mp3Bc+52qlhhlgr/3fnWOfSCWKtfifiOnYTKxyr7W/uCWKVAbGWLLFW/+fazWSVKlYs1vfFw2RFY2U54AetYYoz6xefYch3wA+JleWAHxIrywE/KFaOA76MWsMUscqAWFkO+OKA//BkfZ/w1tABL5ZYYk0Ya/++mVihWO3wiRCxArGOr9WI1RGrusFH1vD4jNxkhc+sIlbw6tBa9eJf+J7lxT+XUrH+IlbLF8v7hh+OtWR5ujMgVp4b/PqLllirRjPN0531X7ZZbp/u1OpjktFDz6eVI0dWqnvW2j18+PctyddRLt8/eTtP5d0XU3zRyRedxBJLLLHSx5r0F9w2+l2HSX9QpG0wV/P+glvdQAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIBEvgDxkA6cfrJoMQAAAABJRU5ErkJggg=="

showInfo = {}
episodeInfo = {}

class showMeta():
	def __init__(self, hasInfo):
		self.hasInfo = hasInfo

class episodeMeta():
	def __init__(self, hasInfo):
		self.hasInfo = hasInfo
		if not hasInfo:
			self.art = defaultArt

def traktSlugify(name):
	name = name.replace("_", "-")
	name = urllib.parse.unquote(name)
	parts = name.split("-")

	# Remove year from end of ID
	if re.match("\(\d+\)", parts[-1]) is not None:
		name = "-".join(parts[:-1])

	name = name.lower()
	return name

def nameFromSlug(slug):
	contractions = {
		"Don t ": "Don't ",
		"Can t ": "Can't ",
		"Won t ": "Won't ",
		"Isn t ": "Isn't ",
		"I m ": "I'm",
		"He s ": "He's ",
		"She s ": "She's "
	}
	name = slug.replace("_", " ")
	for contraction in contractions:
		name = name.replace(contraction, contractions[contraction])

	return name

def populateShowInfo(showID):
	if showID in showInfo and showInfo[showID] is not None:
		return

	traktSlug = traktSlugify(showID)

	apiURL = "http://api.trakt.tv/show/summary.json/{}/{}".format(TRAKT_API_KEY, traktSlug)

	try:
		req = urllib.request.urlopen(apiURL)
		data = req.read().decode("utf-8")
	except: # 404
		info = showMeta(False)
		info.art = defaultArt
		info.poster = defaultPoster # Change this to default poster
		showInfo[showID] = info
		return

	pyData = json.loads(data)
	info = showMeta(True)
	info.title = pyData["title"]
	info.description = pyData["overview"]

	if "images" in pyData and "fanart" in pyData["images"]:
		artURL = pyData["images"]["fanart"]
		size = "-940"
	else:
		artURL = pyData["poster"]
		size = "-300"

	posterURL = pyData["poster"]

	if "poster-dark" in artURL or "fanart-dark" in artURL:
		info.art = defaultArt

	if "poster-dark" in posterURL or "fanart-dark" in posterURL:
		info.poster = defaultArt

	artURL = artURL.split(".")
	artURL[-2] += size
	artURL = ".".join(artURL)

	posterURL = posterURL.split(".")
	posterURL[-2] += "-300"
	posterURL = ".".join(posterURL)

	info.art = artURL
	info.poster = posterURL

	info.firstAir = datetime.date.fromtimestamp(pyData["first_aired_utc"]).strftime("%B %d, %Y")
	info.genres = ", ".join(pyData["genres"])

	info.cast = pyData["people"]["actors"]

	showInfo[showID] = info


def populateEpisodeInfo(showID):
	if showID in episodeInfo:
		return

	traktSlug = traktSlugify(showID)
	showInfoURL = "http://api.trakt.tv/show/seasons.json/{}/{}".format(TRAKT_API_KEY, traktSlug)

	seasons = []
	try:
		req = urllib.request.urlopen(showInfoURL)
		data = req.read().decode("utf-8")
	except:
		episodeInfo[showID] = None
		return

	pyData = json.loads(data)
	for s in pyData:
		seasons.append(s["episodes"])

	print("Got show info for " + showID)

	seasonInfo = []

	for s, es in enumerate(seasons):
		seasonInfoURL = "http://api.trakt.tv/show/season.json/{}/{}/{}".format(TRAKT_API_KEY, traktSlug, s + 1)

		try:
			req = urllib.request.urlopen(seasonInfoURL)
			data = req.read().decode("utf-8")
		except:
			result = [episodeMeta(False)] * es
			seasonInfo.append(result)
			continue

		pyData = json.loads(data)

		result = []

		for x in pyData:
			e = episodeMeta(True)
			e.title = x["title"]
			e.art = x["screen"]
			e.description = x["overview"]
			e.date = x["first_aired_utc"]
			result.append(e)

		seasonInfo.append(result)

	episodeInfo[showID] = seasonInfo


@app.route("/")
def main():
	return render_template("main.html", searchVal = "")

@app.route("/search", methods = ["GET"])
def search():
	# Go through all the directories to search for the query
	# Try to merge results if they are the same
	# Cache merged results?
	q = request.args.get("q")

	results = {}

	for b in directoryList:
		results[b.id] = b.search(q)

	for k in results:
		for r in results[k]:
			results[k][r] = html.unescape(results[k][r])
			populateShowInfo(r)

	return render_template("search.html", searchVal = q, results = results, info = showInfo)

@app.route("/show/<showID>")
def show(showID):
	results = {}

	for b in directoryList:
		results[b.id] = b.getShow(showID)

	populateShowInfo(showID)
	populateEpisodeInfo(showID)

	if episodeInfo[showID] is None:
		art = defaultArt
	else:
		art = [[e.art for e in s] for s in episodeInfo[showID]]
	return render_template("show.html", name = nameFromSlug(showID), results = results, hasInfo = (not episodeInfo[showID] is None), info = showInfo[showID], art = art)

@app.route("/episode/<episodeID>")
def episode(episodeID):
	# Get season number and episode number from episodeID
	parts = episodeID.split("_")
	showID = "_".join(parts[:-2])
	season = int(parts[-2][1:]) # parts[-2] -> s10
	episodeNum = int(parts[-1][1:]) # parts[-1] -> e23

	results = {}

	for b in directoryList:
		results[b.id] = b.getEpisode(episodeID)

	populateEpisodeInfo(showID)

	if episodeInfo[showID] is None:
		info = None
	else:
		info = episodeInfo[showID][season - 1][episodeNum - 1]
	
	return render_template("episode.html", name = nameFromSlug(showID), season = season, episodeNum = episodeNum, links = results, hasInfo = (not episodeInfo[showID] is None) , info = info)

@app.route("/video", methods = ["GET"])
def video():
	videoURL = request.args.get("url")
	if "//" not in videoURL:
		videoURL = "//" + videoURL

	url = urllib.parse.urlparse(videoURL)

	for b in vidHostList:
		if url.netloc == b.domain or url.netloc == "www." + b.domain:
			a = b.getVid(url.path[1:])
			return a

	return "Video not found"

def initBackends():
	for importer, mod, ispkg in pkgutil.iter_modules(directories.__path__):
		try:
			directoryList.append(importlib.import_module("directories." + mod))
			print("Imported directory: {}".format(mod))
		except:
			print("Failed to import directory: {}".format(mod))

def initVidHosts():
	for importer, mod, isPkg in pkgutil.iter_modules(video_hosts.__path__):
		try:
			vidHostList.append(importlib.import_module("video_hosts." + mod))
			print("Imported video host: {}".format(mod))
		except:
			print("Failed to import video host: {}".format(mod))

if __name__ == "__main__":
	initBackends()
	initVidHosts()
	app.run(host="0.0.0.0", port=8080, debug=True)
