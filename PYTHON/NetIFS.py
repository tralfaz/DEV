import socket

print [i[4][0] for i in socket.getaddrinfo(socket.gethostname(), None)]

for nif in socket.getaddrinfo(None, None):
  print "NIF:", nif

#from netifaces import interfaces, ifaddresses, AF_INET
#
#def ip4_addresses():
#    ip_list = []
#    for interface in interfaces():
#        for link in ifaddresses(interface)[AF_INET]:
#            ip_list.append(link['addr'])
#    return ip_list
