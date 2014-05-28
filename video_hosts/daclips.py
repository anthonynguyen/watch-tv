"""
Backend file for interfacing with video hosts
This backend is for daclips.in
"""

import re
import urllib.parse
import urllib.request

id = "daclips"
domain = "daclips.in"

# Send POST to http://daclips.in/videoID
#    + op -> download1
#    + id -> videoID
#    + method_free -> Free Download

def getVid(videoID): # e.g. 59k4uhwsye0b
	params = {
		"op": "download1",
		"id": videoID,
		"method_free": "Free Download"
	}

	p = urllib.parse.urlencode(params)
	p = p.encode("ascii")

	req = urllib.request.urlopen("http://daclips.in/{}".format(videoID), data = p)
	data = req.read().decode("utf-8")

	return data