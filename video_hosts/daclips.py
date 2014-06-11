"""
Backend file for interfacing with video hosts
This backend is for daclips.in
"""

import re
import urllib.parse
import urllib.request

id = "daclips"
domain = "daclips.in"

vidType = "html5"

FNAME_RE = re.compile(r"{ file: \"(.+?)\", type:\"video\" }")

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

	# { file: "http://50.7.164.202:8182/vworopwb5ku4tqukwyflngloienul5urpbokbzwxonzgmorq4glgi24qeq/gkk3mft21uz3.mp4", type:"video" }
	match = FNAME_RE.search(data)
	if match == None:
		return "Could not pull video from link"

	fname = match.group(1)

	return fname