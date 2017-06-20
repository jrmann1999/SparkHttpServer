#!/usr/bin/env python
# Reflects the requests from HTTP methods GET, POST, PUT, and DELETE
# Written by Nathan Hamiel (2010)
# Updated by Jeremy Mann (2017)

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from optparse import OptionParser
import json
import requests
import sys

IMGURAPIKEY = sys.argv[1]
SPARKAPIKEY = sys.argv[2]

def search_imgur(search):
    headers = {'Authorization': 'Client-ID ' + IMGURAPIKEY}
    imgurl = 'https://api.imgur.com/3'
    try:
        result = requests.get(imgurl + '/gallery/search?q=' + search +'&q_type=anigif&sort=viral',
                              headers=headers)

        if(result.status_code == 200):
            for q in result.json()['data']:
                if not q['nsfw']:
                    f = q['link']
                    return f
        else:
            print result.request.headers, result.json()
    except Exception as e:
        print "SearchImgurException ", type(e), e.args, e


def get_sparkmsg(msgId):
    headers = {'Authorization': 'Bearer ' + SPARKAPIKEY,
               'Content-type': 'application/json'}
    url = 'https://api.ciscospark.com/v1'

    try:
        r = requests.get(url + '/messages/' + msgId, headers=headers)
    except Exception as e:
        print "GetSparkMSG " + type(e) + ' ' +  e
        pass

    return r

def post_sparkmsg(body):
    headers = {'Authorization': 'Bearer ' + SPARKAPIKEY,
               'Content-type': 'application/json'}
    url = 'https://api.ciscospark.com/v1'

    return requests.post(url + '/messages', headers=headers, data=json.dumps(body))

def handle_hook(payload):
    data = json.loads(payload)['data']
    msg = data['id']
    body = {}
    sparkbot = 'botname@sparkbot.io'

    print data
    try:
     r = get_sparkmsg(msg)
     if r.status_code == 200:
      if (r.json()['personEmail'] <> sparkbot):
        if (r.json()['roomType'] == 'direct'):
            search =  r.json()['text']
            body['toPersonId'] = data['personId']
        else:
            search = r.json()['text'].split(' ', 1)[1]
            body['roomId'] = data['roomId']

        url = str(search_imgur(search))
        body['files'] = [url]
        print (json.dumps(body))
        post = post_sparkmsg(body)
      else:
        pass
    except Exception as e:
     print "HandleHookException: ", type(e), e.args, e
     pass

class RequestHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    request_path = self.path

    print("\n----- Request Start ----->\n")
    print(request_path)
    print(self.headers)
    print("<----- Request End -----\n")

    self.send_response(200)
    self.send_header("Content-Type", "text/html")
    self.end_headers()

  def do_POST(self):
    request_path = self.path
    request_headers = self.headers
    content_length = request_headers.getheaders('content-length')
    length = int(content_length[0]) if content_length else 0
    payload = self.rfile.read(length)

    print("\n----- Request Start ----->\n")
    #print(request_headers)
    #print(json.loads(payload)['data'])
    handle_hook (payload)
    print("<----- Request End -----\n")

    self.send_response(200)
    self.send_header("Content-Type", "text/html")
    self.end_headers()

  do_PUT = do_POST
  do_DELETE = do_GET

def main():
    port = 90
    print('Listening on localhost:%s' % port)
    server = HTTPServer(('', port), RequestHandler)
    server.serve_forever()

main()
