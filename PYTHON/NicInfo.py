import socket
import fcntl
import struct

def active_nic_addresses():
    """
    Return a list of IPv4 addresses that are active on the computer.
    """

    addresses = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1]

    return addresses

def get_ip_address( NICname ):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', NICname[:15].encode("UTF-8"))
    )[20:24])


def nic_info():
    """
    Return a list with tuples containing NIC and IPv4
    """
    nic = []

    for ix in socket.if_nameindex():
        name = ix[1]
        ip = get_ip_address( name )

        nic.append( (name, ip) )

    return nic

if __name__ == "__main__":

    print active_nic_addresses() 
    print nic_info() 
