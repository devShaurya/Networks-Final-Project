from mininet.topo import Topo,SingleSwitchTopo
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.link import TCLink

class toposingle(Topo):
    topo = SingleSwitchTopo(k=6,controller=None)
    net = Mininet(topo)
    net.start()
    net.hosts[0].sendCmd("python3 tcp_server.py &")
    i=1
    for h in net.hosts[1:]:
        if(q=="e"):
            h.sendCmd("python3 tcp_client.py book{}".format(i))
        if(q=="f"):
            h.sendCmd("python3 tcp_client.py book1")
        i+=1
    # print(net.hosts[0].)
    results = {}
    for h in net.hosts:
        # if(h.name!="h1"):
        results[h.name] = h.waitOutput()
    for h in results:
        print(h)
        print(results[h])
    net.stop()