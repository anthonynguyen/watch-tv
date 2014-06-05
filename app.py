"""
watch-tv - watch some TV pulled from various online sources
"""

# Included stuff
from flask import Flask
from flask import render_template
from flask import request

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

showInfo = {}
episodeInfo = {}

class showMeta():
	def __init__(self, title):
		self.title = title

class episodeMeta():
	def __init__(self, title):
		self.title = title

def traktSlugify(name):
	name = name.replace("_", "-")
	name = urllib.parse.unquote(name)
	parts = name.split("-")

	# Remove year from end of ID
	if re.match("\(\d+\)", parts[-1]) is not None:
		name = "-".join(parts[:-1])

	name = name.lower()
	return name

def populateShowInfo(showID):
	if showID in showInfo and showInfo[showID] is not None:
		return

	traktSlug = traktSlugify(showID)

	apiURL = "http://api.trakt.tv/show/summary.json/{}/{}".format(TRAKT_API_KEY, traktSlug)

	try:
		req = urllib.request.urlopen(apiURL)
		data = req.read().decode("utf-8")
	except:
		return defaultArt

	pyData = json.loads(data)
	if pyData["status"] ==  "failure":
		showInfo[showID] = None
		return
	else:
		info = showMeta(pyData["title"])
		info.description = pyData["overview"]

		if "images" in pyData and "fanart" in pyData["images"]:
			artURL = pyData["images"]["fanart"]
			size = "-940"
		else:
			artURL = pyData["poster"]
			size = "-300"

		if "poster-dark" in artURL or "fanart-dark" in artURL:
			info.art = defaultArt

		artURL = artURL.split(".")
		artURL[-2] += size
		artURL = ".".join(artURL)

		info.art = artURL

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
		print("except")
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
			print("except")
			result = [None] * es
			seasonInfo.append(result)
			continue

		pyData = json.loads(data)

		result = []

		for x in pyData:
			e = episodeMeta(x["title"])
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
	a = ""

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

	return render_template("show.html", name = showID, results = results, info = showInfo[showID], art = [[e.art for e in s] for s in episodeInfo[showID]])

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
	
	return render_template("episode.html", name = showID, season = season, episodeNum = episodeNum, links = results, info = episodeInfo[showID][season - 1][episodeNum - 1])

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
