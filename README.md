# j2p2j
Websocket Javascript/Python framework, Copyright (c) 2015, Michael Scott Cuthbert and cuthbertLab

What is it?
===========
A way of working with Javascript and Python together for the best parts of both.

Use it to make a great UI for a Python project in the web browser.

Use it to add some amazing Python tools to a Javascript project.


What do I do?
==============
Subclass the `j2p2j.Application` and `j2p2j.Client` objects.

In `j2p2j.Client` define methods that you'd like to be available from Javascript

Create a UI in an index.html file.

Call your application with: 

    a = MyApplication('index.html', MyClientClass)
    a.run()
    
Tada!  See the demos directory for two demos...


