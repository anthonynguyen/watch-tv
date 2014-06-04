"""
Backend file for interfacing with video hosts
This backend is for movpod.in
"""

import re
import urllib.parse
import urllib.request

id = "movpod"
domain = "movpod.in"

FNAME_RE = re.compile(r"file: \"(.+?/video.(?:mp4|flv))\",")

# Send POST to http://movpod.in/videoID
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

	req = urllib.request.urlopen("http://movpod.in/{}".format(videoID), data = p)
	data = req.read().decode("utf-8")

	match = FNAME_RE.search(data)
	if match == None:
		return "Could not pull video from link"

	fname = match.group(1)

	return fname