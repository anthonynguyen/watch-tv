"""
Backend file for interfacing with video hosts
This backend is for gorillavid.in
"""

import re
import urllib.parse
import urllib.request

id = "gorillavid"
domain = "gorillavid.in"

vidType = "html5"

FNAME_RE = re.compile(r"file: \"(.+?/video.(?:mp4|flv))\",")

# Send POST to http://gorillavid.in/videoID
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

	req = urllib.request.urlopen("http://gorillavid.in/{}".format(videoID), data = p)
	data = req.read().decode("utf-8")

	# file: "http://50.7.164.210:8182/qworpjelugu4tqukwyflnet7lvagbvzna4ncsavvcimteizgfwds27cxjy/video.mp4",
	match = FNAME_RE.search(data)
	if match == None:
		return "Could not pull video from link"

	fname = match.group(1)

	return fname