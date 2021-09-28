
""" This code use curl to download 2100 github projects
  @author : Ossim Belias François Philippe
  @date : 28 september 2021"""

import pycurl
import time

for i in range(1, 11, 1):
    # request for projects 100 per page
    url = "https://api.github.com/search/repositories?q=language:java+is:public+forks:0+topic:android+archived:false" \
          "&per_page=100&page=" + str(i)

    # file downloaded
    file = open('./data/pycurl_' + str(i) + '.json', 'wb')

    crl = pycurl.Curl()
    crl.setopt(crl.URL, url)
    crl.setopt(crl.WRITEDATA, file)
    crl.perform()
    crl.close()

    print("finished downloading projects for page " + str(i))

    # little sleep time at the middle of the request
    if i == int(11 / 2):
        print("going for a little sleep ...")
        time.sleep(100)

print("done")
