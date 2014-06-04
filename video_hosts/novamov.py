"""
Backend file for interfacing with video hosts
This backend is for novamov.com
"""

import re
import urllib.parse
import urllib.request

#http://www.novamov.com/api/player.api.php?file=481200e9d928e&key=76%2E10%2E136%2E30-39ce698e365bd646007293ddce454e25

id = "novamov"
domain = "novamov.com"

FKEY_RE = re.compile(r"flashvars\.filekey=\"(.+?)\";")

def getVid(videoID):
	videoID = videoID[6:] # Strip the video/ in the front
	
	firstReq = urllib.request.urlopen("http://www.novamov.com/video/{}".format(videoID))
	data = firstReq.read().decode("utf-8")

	#return data

	match = FKEY_RE.search(data)
	if match == None:
		return "Could not pull video from link"

	fkey = match.group(1)
	#return(urllib.parse.quote(fkey))

	gData = {
		"cid": 1,
		"cid2": "undefined",
		"ci3": "undefined",
		"user": "undefined",
		"pass": "undefined",
		"file": videoID,
		"key": fkey
	}

	headers = {
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36",
	}

	p = urllib.parse.urlencode(gData)

	reqObj = urllib.request.Request("http://www.novamov.com/api/player.api.php?" + p, headers = headers)
	
	secReq = urllib.request.urlopen(reqObj)
	data = secReq.read().decode("utf-8")[4:]

	data = data.split("&")

	return data[0]