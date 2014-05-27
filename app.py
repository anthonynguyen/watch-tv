"""
watch-tv - watch some TV pulled from various online sources
"""

from flask import Flask
import backends
import importlib
import pkgutil

app = Flask(__name__)
backendList = []

@app.route("/")
def hello_world():
	return "Hello World!"

@app.route("/search/<q>")
def search(q):
	# Go through all the backends to search for the query
	# Try to merge results if they are the same
	# Cache merged results?
	results = {}
	a = ""
	for b in backendList:
		results[b.id] = b.search(q)
	for k in results:
		a += " {} -> {}".format(k, results[k])
	return a

@app.route("/show/<int:id>")
def show(id):
	# ID should be unique per backend
	# Requesting an ID should get an aggregate of
	# all the results from all the different backends
	# an ID from any backend should be able to refer to the aggregate
	pass

def initBackends():
	for importer, mod, isPkg in pkgutil.iter_modules(backends.__path__):
		try:
			backendList.append(importlib.import_module("backends." + mod))
			print("Imported backend: {}".format(mod))
		except:
			print("Failed to import backend: {}".format(mod))

if __name__ == "__main__":
	initBackends()
	app.run(host="0.0.0.0", port=8080, debug=True)
