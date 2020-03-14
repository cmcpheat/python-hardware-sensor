# ------ References
# https://docs.python.org/2/library/socket.html
# https://wiki.python.org/moin/TcpCommunication#Client
# https://docs.python.org/2/library/json.html

import socketserver
import time
from tcp_settings import IP, PORT
from OHM import OHM
import json


# request handler class
class TCPRequestHandler(socketserver.BaseRequestHandler):
    """
    The request handler receives the response data from the client
    """

    def __init__(self, request, client_address, server):
        # Init the base class
        super(TCPRequestHandler, self).__init__(request, client_address, server)

    def handle(self):

        #  self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip().decode("utf-8")  # NB bytes to string

        # request OHM data
        requested_data = {}
        my_ohm = OHM() # call OHM class from OHM module
        request = json.loads(self.data) # load request from client
        if request['type'] == 'request':
            if request['param'] == 'cpu_core_temp':
                requested_data = my_ohm.get_core_temps() # calls method from OHM for cpu temps
            elif request['param'] == "clock_speeds":
                requested_data = my_ohm.get_clock_speeds() # calls method from OHM for clock speeds
            elif request['param'] == "cpu_core_load":
                requested_data = my_ohm.get_core_loads() # calls method from OHM for cpu load times
            elif request['param'] == "cpu_core_power":
                requested_data = my_ohm.get_core_powers() # calls method from OHM for cpu powers

        # return the data to the client
        response = json.dumps(requested_data)
        self.request.sendall(response.encode('utf-8'))

def main():
    # starts server and serves forever
    # import IP and port from tcp_settings module
    with socketserver.TCPServer((IP, PORT), TCPRequestHandler) as server:
        print("Server Started")
        server.serve_forever()

if __name__ == '__main__':
    main()
    print("Server Stopped")
