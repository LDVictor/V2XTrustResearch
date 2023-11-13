from victor_aries_cloudagent.demo.runners.agent_container import AriesAgent
from p2pnetwork.node import Node

class Vehicle(Node):

    pendingMessages = []
    agent = AriesAgent('id-01', 8011, 8011)

    def __init__(self, host, port, id=None, callback=None, max_connections=0):
        # verificar o erro dessa linha
        super(Vehicle, self).__init__(host, port, id, callback, max_connections)
        print("Vehicle: OBU iniciado")

    # estes métodos são chamados quando algo acontece na rede.
    # precisamos implementar o comportamento do nó de rede para criar a funcionalidade necessária.

    def outbound_node_connected(self, node):
        print("No de saida conectado (" + self.id + "): " + node.id)
        
    def inbound_node_connected(self, node):
        print("No de entrada conectado: (" + self.id + "): " + node.id)

    def inbound_node_disconnected(self, node):
        print("No de entrada desconectado: (" + self.id + "): " + node.id)

    def outbound_node_disconnected(self, node):
        print("No de saida desconectado: (" + self.id + "): " + node.id)

    def node_message(self, node, data):
        print("Mensagem (" + self.id + ") de " + node.id + ": " + str(data))
        
    def node_disconnect_with_outbound_node(self, node):
        print("No deseja se desconectar de outro no de saida: (" + self.id + "): " + node.id)
        
    def node_request_to_stop(self):
        print("No eh solicitado a parar (" + self.id + "): ")

    def verifica_credencial(self, node):
        # A funcao deve verificar se a entidade que deseja se comunicar com esse veiculo possui uma credencial verificavel
        print("verifica_credencial")
        return True