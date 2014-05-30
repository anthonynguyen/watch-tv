"""
watch-tv - watch some TV pulled from various online sources
"""

from flask import Flask
from flask import render_template
from flask import request

import html
import importlib
import pkgutil
import urllib.parse

import directories
import video_hosts

app = Flask(__name__)
directoryList = []
vidHostList = []

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

	return render_template("search.html", searchVal = q, results = results)

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
