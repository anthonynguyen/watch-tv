"""
watch-tv - watch some TV pulled from various online sources
"""

from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello_world():
	return "Hello World!"

@app.route("/search/<q>")
def search(q):
	# Go through all the backends to search for the query
	# Try to merge results if they are the same
	# Cache merged results?
	pass

@app.route("/show/<int:id>")
def show(id):
	# ID should be unique per backend
	# Requesting an ID should get an aggregate of
	# all the results from all the different backends
	# an ID from any backend should be able to refer to the aggregate
	pass

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8080, debug=True)
