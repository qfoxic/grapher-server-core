## Motivation
If you run a large company with a complicated infrastructure in AWS or
any other env, it quite hard to view stuff in a hierarchical mode,
like what virtual machines resides in which regions or how to hierarchically 
view regions -> security groups -> load balancers -> virtual machines.
Also, it would be very useful to display logical structure of a database data,
like organizations->users->assets.
After all, we need a tool that can flexible display logical data structures
and we can tell it how data should be represented. Grapher was created with 
all those thoughts in mind, all you need is to decide which structure you 
wish to see, install existing Grapher driver or create your own and then go 
to play with your data.

## Grapher server
#### Overview
Purely written in a python3.6 with async feature in mind. When it starts,
it’s looking for installed drivers and activate them by user/client request.
It doesn’t support multiple connections, it was intendenly written to 
support one client connection per one server instance, mostly to avoid 
multiprocessing/multithreading complications, to be fast and simple.

#### Installation (TBD)
All you need is to decide what data you wish to display, search for a driver
in a pip manager. Install driver in a virtual environment or globally,
if you have dedicated grapher server. You can install as many drivers as
you wish.

#### Start server
You have to two options how you can run it:
* locally - just install drivers with a python3 pip manager into some desired venv and then run command like:
  ```commandline.
  $ grapher_venv/bin/activate && python3 -m grapher.core.server --port 9999
  ```
* you can use any websocket client to play with the server. 

## Grapher protocol
#### Overview
To implement a flexible way to build different hierarchical visualizations it was decided to use typical structure for parent-children relations.
Table representation of a simple tree structure looks like:

| id | pid | name      |
|----|-----|-----------|
| 1  | 0   | root 0    |
| 2  | 1   | parent 1  |
| 3  | 2   | child 1.1 |
| 4  | 1   | parent 2  |
| 5  | 4   | child 2.1 |


If we add a tree item `type` field and wrap everything in `json` we will get even more flexible structure which allows to differentiate between different item types.
Actually, grapher server is wrapping hierarchical data into json and create streaming session which send them as soon as they become available.

#### Grapher language
The basic idea here is to create driver that will cover some data which
is desired to be displayed, install it in a system, run server and ask it
to load that driver and then communicate with actually driver using it’s
exposed methods. So, grapher server itself support two verbs:

* `load DRIVER` - where DRIVER is a driver name installed in a system
                  this method load driver into a session and expose its
                  methods
* `unload` - this method unload loaded driver to provide ability to switch 
             between drivers. The rest verbs are exposed by actually loaded
             driver. Server in that case is a proxy which accepts parameters,
             loads driver’s method and pass arguments to it.
             That operation looks like:
             ```commandline.
             > load DRIVER
             > driver_method arg1=data1&&arg2=data2             
             ```

## Grapher client
Currently, we support a client written with Qt Library (C++) https://github.com/qfoxic/grapher-client-qt.
