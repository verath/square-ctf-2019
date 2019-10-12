from telnetlib import Telnet

with Telnet("talk-to-me-dd00922915bfc3f1.squarectf.com", 5678) as tn:   
    # Allow chars (at least): 1234567890.,-+/;:{}><%'"

    msg = b"''<<72<<101<<108<<108<<111<<33\n"
    print("->", msg)
    tn.write(msg)

    data = ""
    while True:
        d = tn.read_some()
        if not d:
            break
        data += d.decode('ascii')
    print("<-", data)
