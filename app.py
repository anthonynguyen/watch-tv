"""
watch-tv - watch some TV pulled from various online sources
"""

from flask import Flask
import directories
import importlib
import pkgutil

app = Flask(__name__)
directoryList = []

@app.route("/")
def hello_world():
	return "Hello World!"

@app.route("/search/<q>")
def search(q):
	# Go through all the directories to search for the query
	# Try to merge results if they are the same
	# Cache merged results?
	results = {}
	a = ""

	for b in directoryList:
		results[b.id] = b.search(q)
	for k in results:
		a += " {} -> {}".format(k, results[k])

	return a

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

	for k in results:
		a += " {} -> {}".format(k, results[k])
	
	return a

def initBackends():
	for importer, mod, isPkg in pkgutil.iter_modules(directories.__path__):
		try:
			directoryList.append(importlib.import_module("directories." + mod))
			print("Imported directory: {}".format(mod))
		except:
			print("Failed to import directory: {}".format(mod))

if __name__ == "__main__":
	initBackends()
	app.run(host="0.0.0.0", port=8080, debug=True)
