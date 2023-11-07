import datetime
import logging
import os
import time
from p2pnetwork.node import Node

from victor_aries_cloudagent.demo.runners.agent_container import (  # noqa:E402
    arg_parser,
    create_agent_with_args,
    AriesAgent,
)
from victor_aries_cloudagent.demo.runners.support.agent import (  # noqa:E402
    CRED_FORMAT_INDY,
    CRED_FORMAT_JSON_LD,
    SIG_TYPE_BLS,
)
from victor_aries_cloudagent.demo.runners.support.utils import (  # noqa:E402
    log_msg,
    log_status,
    prompt,
    prompt_loop,
)

class RAN(Node, AriesAgent):

    #agent = AriesAgent()

    CRED_PREVIEW_TYPE = "https://didcomm.org/issue-credential/2.0/credential-preview"
    SELF_ATTESTED = os.getenv("SELF_ATTESTED")
    TAILS_FILE_COUNT = int(os.getenv("TAILS_FILE_COUNT", 100))
    logging.basicConfig(level=logging.WARNING)
    LOGGER = logging.getLogger(__name__)

    def __init__(self, 
                 host, 
                 port, 
                 id=None, 
                 callback=None, 
                 max_connections=0):
        super(RAN, self).__init__(host, port, id, callback, max_connections)
        print("RAN iniciado")

    # funcoes do node

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

    # funcoes do hyperledger

    async def detect_connection(self):
        await self._connection_ready
        self._connection_ready = None

    @property
    def connection_ready(self):
        return self._connection_ready.done() and self._connection_ready.result()
    

    # funcao para gerar uma credencial verificavel para um no
    
    def generate_credential_offer(self, aip, cred_type, cred_def_id, exchange_tracing):
        d = datetime.date.today()
        if aip == 10:
            # define attributes to send for credential
            self.cred_attrs[cred_def_id] = {
                "name": "Vehicle",
                "application": "ADAS",
                "datetime": d,
                "timestamp": str(int(time.time())),
            }

            cred_preview = {
                "@type": self.CRED_PREVIEW_TYPE,
                "attributes": [
                    {"name": n, "value": v}
                    for (n, v) in self.cred_attrs[cred_def_id].items()
                ],
            }
            offer_request = {
                "connection_id": self.connection_id,
                "cred_def_id": cred_def_id,
                "comment": f"Offer on cred def id {cred_def_id}",
                "auto_remove": False,
                "credential_preview": cred_preview,
                "trace": exchange_tracing,
            }
            return offer_request

        elif aip == 20:
            if cred_type == CRED_FORMAT_INDY:
                self.cred_attrs[cred_def_id] = {
                    "name": "Vehicle",
                    "application": "ADAS",
                    "datetime": d,
                    "timestamp": str(int(time.time())),
                }

                cred_preview = {
                    "@type": self.CRED_PREVIEW_TYPE,
                    "attributes": [
                        {"name": n, "value": v}
                        for (n, v) in self.cred_attrs[cred_def_id].items()
                    ],
                }
                offer_request = {
                    "connection_id": self.connection_id,
                    "comment": f"Offer on cred def id {cred_def_id}",
                    "auto_remove": False,
                    "credential_preview": cred_preview,
                    "filter": {"indy": {"cred_def_id": cred_def_id}},
                    "trace": exchange_tracing,
                }
                return offer_request

            elif cred_type == CRED_FORMAT_JSON_LD:
                offer_request = {
                    "connection_id": self.connection_id,
                    "filter": {
                        "ld_proof": {
                            "credential": {
                                "@context": [
                                    "https://www.w3.org/2018/credentials/v1",
                                    "https://w3id.org/citizenship/v1",
                                    "https://w3id.org/security/bbs/v1",
                                ],
                                "type": [
                                    "VerifiableCredential",
                                    "PermanentResident",
                                ],
                                "id": "https://credential.example.com/residents/1234567890",
                                "issuer": self.did,
                                "issuanceDate": "2020-01-01T12:00:00Z",
                                "credentialSubject": {
                                    "type": ["PermanentResident"],
                                    "givenName": "Vehicle",
                                    "application": "ADAS",
                                },
                            },
                            "options": {"proofType": SIG_TYPE_BLS},
                        }
                    },
                }
                return offer_request

            else:
                raise Exception(f"Error invalid credential type: {self.cred_type}")

        else:
            raise Exception(f"Error invalid AIP level: {self.aip}")