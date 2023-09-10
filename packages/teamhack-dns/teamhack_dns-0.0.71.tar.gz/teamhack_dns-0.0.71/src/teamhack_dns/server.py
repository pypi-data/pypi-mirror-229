import socket
from dnslib          import *
from teamhack_db.sql import select_hostname_recordtype

UPSTREAM_SERVER = '8.8.8.8'
UPSTREAM_PORT   = 53

# Function to handle DNS queries and return a response
def handle_dns_query(conn, data):
    request = DNSRecord.parse(data)

    reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)

    qname = str(request.q.qname)
    qtype = request.q.qtype
    #if   qtype == QTYPE.NS: qt = 'NS'
    #elif qtype == QTYPE.A:  qt = 'A'
    #else:
    #  a = request.send(UPSTREAM_SERVER, UPSTREAM_PORT, tcp=False, timeout=10)
    #  request.add_answer(a)
    #  return request.pack()

    print(f'qname: {qname}, qtype: {qtype}')
    res = select_hostname_recordtype(conn, qname, qtype)
    print(f'res: {res}')
    if not res:
      a = request.send(UPSTREAM_SERVER, UPSTREAM_PORT, tcp=False, timeout=10)
      return a
    res = res[3]
    print(f'res: {res}')
    if not res:
      a = request.send(UPSTREAM_SERVER, UPSTREAM_PORT, tcp=False, timeout=10)
      return a
    #res = res[3]
    #if not res:
    #  a = request.send(UPSTREAM_SERVER, UPSTREAM_PORT, tcp=False, timeout=10)
    #  return a
    print(f'qname: {qname}, qtype: {qtype}, res: {res}')

    #if qname in dns_records and qtype in dns_records[qname]:
    #if res:
    if qtype == QTYPE.NS: reply.add_answer(RR(rname=qname, rtype=qtype, rdata=NS(res)))
    else:                 reply.add_answer(RR(rname=qname, rtype=qtype, rdata=A(res)))
    #else:
    #    # TODO
    #    #reply.add_answer(RR(rname=qname, rtype=qtype, rdata=A('0.0.0.0')))
    #    #q = DNSRecord(q=DNSQuestion(qname))
    #    a = reply.send(UPSTREAM_SERVER, UPSTREAM_PORT, tcp=False, timeout=10)
    #    reply.add_answer(a)

    return reply.pack()

# Function to start the DNS server and listen for requests
def start_server(conn):
    host = ''
    port = 53

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))

    print(f'DNS server listening on port {port}... \n \n' )

    while True:
        data, address = server_socket.recvfrom(1024)
        response = handle_dns_query(conn, data)
        server_socket.sendto(response, address)

