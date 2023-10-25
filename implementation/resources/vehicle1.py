from p2pnetwork.node import Node

class Vehicle1(Node):

    def __init__(self, host, port, id=None, callback=None, max_connections=0):
        super(Vehicle1, self).__init__(host, port, id, callback, max_connections)
        print("Vehicle 1: OBU started")

    # estes métodos são chamados quando algo acontece na rede.
    # precisamos implementar o comportamento do nó de rede para criar a funcionalidade necessária.

    def outbound_node_connected(self, node):
        print("outbound_node_connected (" + self.id + "): " + node.id)
        
    def inbound_node_connected(self, node):
        print("inbound_node_connected: (" + self.id + "): " + node.id)

    def inbound_node_disconnected(self, node):
        print("inbound_node_disconnected: (" + self.id + "): " + node.id)

    def outbound_node_disconnected(self, node):
        print("outbound_node_disconnected: (" + self.id + "): " + node.id)

    def node_message(self, node, data):
        print("node_message (" + self.id + ") from " + node.id + ": " + str(data))
        
    def node_disconnect_with_outbound_node(self, node):
        print("node wants to disconnect with oher outbound node: (" + self.id + "): " + node.id)
        
    def node_request_to_stop(self):
        print("node is requested to stop (" + self.id + "): ")