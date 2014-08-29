import threading
import urllib.request
import json

def json2objects(data):
        try:
                return json.loads(data)
        except Exception as e:
                print("WARNING: no json: "+str(e))
                return None

# should use http.client here instead of urllib?

# Define a function for the thread
def generate_batatweets():
    print("Hello")
    link = "http://library.ewi.utwente.nl/ecadata/batatweets.txt"
    req = urllib.request.Request(link)
    response = urllib.request.urlopen(req)
    page_str = response.read().decode("utf-8")
    for line in page_str.split("\n"):
        jo = json2objects(line)
        try:
            print(jo['text'])
        except:
            print("IGNORE:"+line)

try:
   t = threading.Thread(target=generate_batatweets)
   t.start()
except:
   print("Error: unable to start generate_batatweets thread")

while 1:
   pass

