# Networks-Final-Project
We have implemented a mini-classroom for our networks course project
Some caveats are that the user error has been resolved for most issues but it could create problem in some instructions. It creates a problem in some instructions and login. So please carefully read the instructions that come up in CLI while running the file and follow them.

**Commands used**
1. Firstly run the command `python3 server.py` to run the server
2. After running the first command run `python3 client.py` to run client. And then follow exactly instructions written in CLI
3. For running on mininet run commands like `sudo mn --topo single,2` for creating topologies and then run commands like `xterm <h1>` to open **xterminal**. Then run `ifconfig`
command to get ip-address of the host that you want to designate as the server. Go to file config.py and change the variable ip to this host's ip. Then run *1* for creating one of them as server and *2*  for creating client.
video link :- https://drive.google.com/file/d/1GIORiQ3SdB29PvK3L0HpgWNgpfHgcKwx/view?usp=sharing
