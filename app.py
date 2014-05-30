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
import urllib.parse
import urllib.request


# Custom stuff
from config import *

import directories
import video_hosts

app = Flask(__name__)
directoryList = []
vidHostList = []

coverArt = {}
defaultArt = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASwAAADICAMAAABlASxnAAAABGdBTUEAALGPC/xhBQAAAAFzUkdCAK7OHOkAAAASUExURczMzFVVVf7+/qmpqX19feXl5WEFUTsAAAKCSURBVHja7dztTuMwEAVQJ2O//ytvSRGULWQnacJKmXN+IRUqceU7jfPR1gAAAAAAAAAAAAAAAAAAgNr6Sb97SZFPoMewtNKxjqGIyd+bmqxaRLKEs6ySS0sJN8z4qVlY2SIqYb6ISrihiF0JH1u2/nKXVbaISrihiKZ7fmmFEqbTUsINB1tKmF9aSrhhxjvZkD/YUsJ8EU33DUVUwnwRlTBfRCXcUEQlzC8tJcynpYQbdj1dCdNLSwk3zHglTBWxvwl3Nvx7XU2feggkl5S81kf79J0umHRWN6LJZyWt53n1c1aa+GTMPyt5EBErXdvrqp+XMZ2i3Ax/aW1dMqzpJLOwhCUsYf1SWL2/n5D51vJa9bD629HR+DgOHSvur68eo107rLjns+kA/+Yjrv4ec1QIa+f+JZ7+vkBYu++4euzdchmoQFi7z64/hHWrZJQIa/f1wP4Z1j3zAmGNA8Lqy9sUCGv3PxePbzDmJqxkWFHj07AfEVaVAX9IWFUGfB+vvsN9ZbUKYcURYVUZ8MeEVWTAx0E1DGElw5qKhNUM+F8O623ACysfVlPDzE56/vqOwhKWsP7LzIrlApGwMitr+SGElVlZ8b4jF1Y6rGm23cmvLGGlBvwys5qwkp+GEWN21iG53VnulRBWcm9Y46B0/zn4EJaw1sI66Lphd0U6F9ZUZbsz7a5h/+sIfggrH9Zc4f6sl8NqZbY7R9z5F8unaoUa9gNuk7yZK2x3dg+t+BJWje3Oci35lZH18dBc1Hgc5eERlLYWXbTP51I8u+NBJ2EJS1jCuoCznr6/ZFgnfa/DuOjX3Z3xjSHjsl8NOJ+gAQAAAAAAAAAAAAAAAAAA8J0/uz0RyXTAZWUAAAAASUVORK5CYII="

@app.route("/")
def main():
	return render_template("main.html", searchVal = "")

def getArt(id): # Link to image art
	if id in coverArt:
		return coverArt[id]
	traktSlug = id.replace("_", "-") # Try to naively create a Trakt-recognizable slug from the ID's used by the show directories
	apiURL = "http://api.trakt.tv/show/summary.json/{}/{}".format(TRAKT_API_KEY, traktSlug)

	try:
		req = urllib.request.urlopen(apiURL)
		data = req.read().decode("utf-8")
	except:
		return defaultArt

	pyData = json.loads(data)
	if pyData["status"] ==  "failure":
		return defaultArt

	else:
		if "images" in pyData and "fanart" in pyData["images"]:
			artURL = pyData["images"]["fanart"]
			size = "-940"
		else:
			artURL = pyData["poster"]
			size = "-300"

		if "poster-dark" in artURL or "fanart-dark" in artURL:
			return defaultArt
		artURL = artURL.split(".")
		artURL[-2] += size
		artURL = ".".join(artURL)

		return artURL

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
			coverArt[r] = getArt(r)

	return render_template("search.html", searchVal = q, results = results, art = coverArt)

@app.route("/show/<showID>")
def show(showID):
	# ID should be unique per directory
	# Requesting an ID should get an aggregate of
	# all the results from all the different directories
	# an ID from any directory should be able to refer to the aggregate
	results = {}
	a = ""

	for b in directoryList:
		results[b.id] = b.getShow(showID)

	return render_template("show.html", name = showID, results = results)

@app.route("/episode/<episodeID>")
def episode(episodeID):
	# ID should be unique per directory
	# Requesting an ID should get an aggregate of
	# all the results from all the different directories
	# an ID from any directory should be able to refer to the aggregate
	results = {}
	a = ""

	for b in directoryList:
		results[b.id] = b.getEpisode(episodeID)

	for k in results:
		a += " {} -> {}".format(k, results[k])
	
	return a

@app.route("/video", methods = ["GET"])
def video():
	videoURL = request.args.get("url")
	if "//" not in videoURL:
		videoURL = "//" + videoURL

	url = urllib.parse.urlparse(videoURL)

	for b in vidHostList:
		if url.netloc == b.domain:
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
	app.run(host="0.0.0.0", port=8080)
