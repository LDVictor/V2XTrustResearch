import asyncio
import datetime
import json
import logging
import os
import time
from aiohttp import ClientError
from p2pnetwork.node import Node
import qrcode


from victor_aries_cloudagent.demo.runners.agent_container import (  # noqa:E402
   arg_parser,
   create_agent_with_args,
   AriesAgent,
)
from victor_aries_cloudagent.demo.runners.faber import FaberAgent
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

   connection_id = None
   _connection_ready = None
   cred_state = {}
   cred_attrs = {}


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

   def verifica_credencial(self, vc, vc_id):
        if (vc != None and vc != ""):
            # precisa verificar se a vc existe no VDR
            try:
                self.generate_proof_request_web_request(20, vc, vc_id, None)
            except Exception:
                return False
            else:
                return True
        return False

   def outbound_node_connected(self, node):
       print("No de saida conectado (" + self.id + "): " + node.id)
      
   def inbound_node_connected(self, node):
       print("No de entrada conectado: (" + self.id + "): " + node.id)


   def inbound_node_disconnected(self, node):
       print("No de entrada desconectado: (" + self.id + "): " + node.id)


   def outbound_node_disconnected(self, node):
       print("No de saida desconectado: (" + self.id + "): " + node.id)


   def node_message(self, node, data):
       print("Mensagem para no (" + self.id + ") do no " + node.id + ": " + str(data))
      
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
      
   def generate_proof_request_web_request(self, aip, cred_type, revocation, exchange_tracing, connectionless=False):
       d = datetime.date.today()
       if aip == 10:
           req_attrs = [
               {
                   "name": "name",
                   "restrictions": [{}],
               },
           ]
           if revocation:
               req_attrs.append(
                   {
                       "name": "name",
                       "restrictions": [{}],
                       "non_revoked": {"to": int(time.time() - 1)},
                   },
               )
           else:
               req_attrs.append(
                   {
                       "name": "name",
                       "restrictions": [{}],
                   }
               )
           if self.SELF_ATTESTED:
               # test self-attested claims
               req_attrs.append(
                   {"name": "self_attested_thing"},
               )
           req_preds = [
               # test zero-knowledge proofs
               {
                   "name": "Vehicle",
                   "p_type": "<=",
                   "restrictions": [{}],
               }
           ]
           indy_proof_request = {
               "name": "Proof of Request",
               "version": "1.0",
               "requested_attributes": {
                   f"0_{req_attr['name']}_uuid": req_attr for req_attr in req_attrs
               },
               "requested_predicates": {
                   f"0_{req_pred['name']}_GE_uuid": req_pred for req_pred in req_preds
               },
           }


           if revocation:
               indy_proof_request["non_revoked"] = {"to": int(time.time())}


           proof_request_web_request = {
               "proof_request": indy_proof_request,
               "trace": exchange_tracing,
           }
           if not connectionless:
               proof_request_web_request["connection_id"] = self.connection_id
           return proof_request_web_request


       elif aip == 20:
           if cred_type == CRED_FORMAT_INDY:
               req_attrs = [
                   {
                       "name": "name",
                       "restrictions": [{}],
                   },
                   {
                       "name": "name",
                       "restrictions": [{}],
                   },
               ]
               if revocation:
                   req_attrs.append(
                       {
                           "name": "name",
                           "restrictions": [{""}],
                           "non_revoked": {"to": int(time.time() - 1)},
                       },
                   )
               else:
                   req_attrs.append(
                       {
                           "name": "name",
                           "restrictions": [{""}],
                       }
                   )
               if self.SELF_ATTESTED:
                   # test self-attested claims
                   req_attrs.append(
                       {"name": "self_attested_thing"},
                   )
               req_preds = [
                   # test zero-knowledge proofs
                   {
                   "name": "Vehicle",
                   "p_type": "<=",
                   "restrictions": [{}],
                   }
               ]
               indy_proof_request = {
                   "name": "Proof of Request",
                   "version": "1.0",
                   "requested_attributes": {
                       f"0_{req_attr['name']}_uuid": req_attr for req_attr in req_attrs
                   },
                   "requested_predicates": {
                       f"0_{req_pred['name']}_GE_uuid": req_pred
                       for req_pred in req_preds
                   },
               }


               if revocation:
                   indy_proof_request["non_revoked"] = {"to": int(time.time())}


               proof_request_web_request = {
                   "presentation_request": {"indy": indy_proof_request},
                   "trace": exchange_tracing,
               }
               if not connectionless:
                   proof_request_web_request["connection_id"] = self.connection_id
               return proof_request_web_request


           elif cred_type == CRED_FORMAT_JSON_LD:
               proof_request_web_request = {
                   "comment": "test proof request for json-ld",
                   "presentation_request": {
                       "dif": {
                           "options": {
                               "challenge": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
                               "domain": "4jt78h47fh47",
                           },
                           "presentation_definition": {
                               "id": "32f54163-7166-48f1-93d8-ff217bdb0654",
                               "format": {"ldp_vp": {"proof_type": [SIG_TYPE_BLS]}},
                               "input_descriptors": [
                                   {
                                       "id": "citizenship_input_1",
                                       "name": "EU Driver's License",
                                       "schema": [
                                           {
                                               "uri": "https://www.w3.org/2018/credentials#VerifiableCredential"
                                           },
                                           {
                                               "uri": "https://w3id.org/citizenship#PermanentResident"
                                           },
                                       ],
                                       "constraints": {
                                           "limit_disclosure": "required",
                                           "is_holder": [
                                               {
                                                   "directive": "required",
                                                   "field_id": [
                                                       "1f44d55f-f161-4938-a659-f8026467f126"
                                                   ],
                                               }
                                           ],
                                           "fields": [
                                               {
                                                   "id": "1f44d55f-f161-4938-a659-f8026467f126",
                                                   "path": [
                                                       "$.credentialSubject.familyName"
                                                   ],
                                                   "purpose": "The claim must be from one of the specified person",
                                                   "filter": {"const": "SMITH"},
                                               },
                                               {
                                                   "path": [
                                                       "$.credentialSubject.givenName"
                                                   ],
                                                   "purpose": "The claim must be from one of the specified person",
                                               },
                                           ],
                                       },
                                   }
                               ],
                           },
                       }
                   },
               }
               if not connectionless:
                   proof_request_web_request["connection_id"] = self.connection_id
               return proof_request_web_request


           else:
               raise Exception(f"Error invalid credential type: {self.cred_type}")


       else:
           raise Exception(f"Error invalid AIP level: {self.aip}")


## Main do Aries


async def main(args):
   agent = await create_agent_with_args(args, ident="ran")


   try:
       log_status(
           "#1 Provision an agent and wallet, get back configuration details"
           + (
               f" (Wallet type: {agent.wallet_type})"
               if agent.wallet_type
               else ""
           )
       )
       agent = FaberAgent(
           "faber.agent",
           agent.start_port,
           agent.start_port + 1,
           genesis_data=agent.genesis_txns,
           genesis_txn_list=agent.genesis_txn_list,
           no_auto=agent.no_auto,
           tails_server_base_url=agent.tails_server_base_url,
           revocation=agent.revocation,
           timing=agent.show_timing,
           multitenant=agent.multitenant,
           mediation=agent.mediation,
           wallet_type=agent.wallet_type,
           seed=agent.seed,
           aip=agent.aip,
           endorser_role=agent.endorser_role,
       )


       faber_schema_name = "degree schema"
       faber_schema_attrs = [
           "name",
           "date",
           "degree",
           "birthdate_dateint",
           "timestamp",
       ]
       if agent.cred_type == CRED_FORMAT_INDY:
           agent.public_did = True
           await agent.initialize(
               the_agent=agent,
               schema_name=faber_schema_name,
               schema_attrs=faber_schema_attrs,
               create_endorser_agent=(agent.endorser_role == "author")
               if agent.endorser_role
               else False,
           )
       elif agent.cred_type == CRED_FORMAT_JSON_LD:
           agent.public_did = True
           await agent.initialize(the_agent=agent)
       else:
           raise Exception("Invalid credential type:" + agent.cred_type)


       # generate an invitation for Vehicle
       await agent.generate_invitation(
           display_qr=True, reuse_connections=agent.reuse_connections, wait=True
       )


       exchange_tracing = False
       options = (
           "    (1) Issue Credential\n"
           "    (2) Send Proof Request\n"
           "    (2a) Send *Connectionless* Proof Request (requires a Mobile client)\n"
           "    (3) Send Message\n"
           "    (4) Create New Invitation\n"
       )
       if agent.revocation:
           options += "    (5) Revoke Credential\n" "    (6) Publish Revocations\n"
       if agent.endorser_role and agent.endorser_role == "author":
           options += "    (D) Set Endorser's DID\n"
       if agent.multitenant:
           options += "    (W) Create and/or Enable Wallet\n"
       options += "    (T) Toggle tracing on credential/proof exchange\n"
       options += "    (X) Exit?\n[1/2/3/4/{}{}T/X] ".format(
           "5/6/" if agent.revocation else "",
           "W/" if agent.multitenant else "",
       )
       async for option in prompt_loop(options):
           if option is not None:
               option = option.strip()


           if option is None or option in "xX":
               break


           elif option in "dD" and agent.endorser_role:
               endorser_did = await prompt("Enter Endorser's DID: ")
               await agent.agent.admin_POST(
                   f"/transactions/{agent.agent.connection_id}/set-endorser-info",
                   params={"endorser_did": endorser_did},
               )


           elif option in "wW" and agent.multitenant:
               target_wallet_name = await prompt("Enter wallet name: ")
               include_subwallet_webhook = await prompt(
                   "(Y/N) Create sub-wallet webhook target: "
               )
               if include_subwallet_webhook.lower() == "y":
                   created = await agent.agent.register_or_switch_wallet(
                       target_wallet_name,
                       webhook_port=agent.agent.get_new_webhook_port(),
                       public_did=True,
                       mediator_agent=agent.mediator_agent,
                       endorser_agent=agent.endorser_agent,
                       taa_accept=agent.taa_accept,
                   )
               else:
                   created = await agent.agent.register_or_switch_wallet(
                       target_wallet_name,
                       public_did=True,
                       mediator_agent=agent.mediator_agent,
                       endorser_agent=agent.endorser_agent,
                       cred_type=agent.cred_type,
                       taa_accept=agent.taa_accept,
                   )
               # create a schema and cred def for the new wallet
               # TODO check first in case we are switching between existing wallets
               if created:
                   # TODO this fails because the new wallet doesn't get a public DID
                   await agent.create_schema_and_cred_def(
                       schema_name=faber_schema_name,
                       schema_attrs=faber_schema_attrs,
                   )


           elif option in "tT":
               exchange_tracing = not exchange_tracing
               log_msg(
                   ">>> Credential/Proof Exchange Tracing is {}".format(
                       "ON" if exchange_tracing else "OFF"
                   )
               )


           elif option == "1":
               log_status("#13 Issue credential offer to X")


               if agent.aip == 10:
                   offer_request = agent.agent.generate_credential_offer(
                       agent.aip, None, agent.cred_def_id, exchange_tracing
                   )
                   await agent.agent.admin_POST(
                       "/issue-credential/send-offer", offer_request
                   )


               elif agent.aip == 20:
                   if agent.cred_type == CRED_FORMAT_INDY:
                       offer_request = agent.agent.generate_credential_offer(
                           agent.aip,
                           agent.cred_type,
                           agent.cred_def_id,
                           exchange_tracing,
                       )


                   elif agent.cred_type == CRED_FORMAT_JSON_LD:
                       offer_request = agent.agent.generate_credential_offer(
                           agent.aip,
                           agent.cred_type,
                           None,
                           exchange_tracing,
                       )


                   else:
                       raise Exception(
                           f"Error invalid credential type: {agent.cred_type}"
                       )


                   await agent.agent.admin_POST(
                       "/issue-credential-2.0/send-offer", offer_request
                   )


               else:
                   raise Exception(f"Error invalid AIP level: {agent.aip}")


           elif option == "2":
               log_status("#20 Request proof of degree from alice")
               if agent.aip == 10:
                   proof_request_web_request = (
                       agent.agent.generate_proof_request_web_request(
                           agent.aip,
                           agent.cred_type,
                           agent.revocation,
                           exchange_tracing,
                       )
                   )
                   await agent.agent.admin_POST(
                       "/present-proof/send-request", proof_request_web_request
                   )
                   pass


               elif agent.aip == 20:
                   if agent.cred_type == CRED_FORMAT_INDY:
                       proof_request_web_request = (
                           agent.agent.generate_proof_request_web_request(
                               agent.aip,
                               agent.cred_type,
                               agent.revocation,
                               exchange_tracing,
                           )
                       )


                   elif agent.cred_type == CRED_FORMAT_JSON_LD:
                       proof_request_web_request = (
                           agent.agent.generate_proof_request_web_request(
                               agent.aip,
                               agent.cred_type,
                               agent.revocation,
                               exchange_tracing,
                           )
                       )


                   else:
                       raise Exception(
                           "Error invalid credential type:" + agent.cred_type
                       )


                   await agent.admin_POST(
                       "/present-proof-2.0/send-request", proof_request_web_request
                   )


               else:
                   raise Exception(f"Error invalid AIP level: {agent.aip}")


           elif option == "2a":
               log_status("#20 Request * Connectionless * proof of degree from alice")
               if agent.aip == 10:
                   proof_request_web_request = (
                       agent.agent.generate_proof_request_web_request(
                           agent.aip,
                           agent.cred_type,
                           agent.revocation,
                           exchange_tracing,
                           connectionless=True,
                       )
                   )
                   proof_request = await agent.agent.admin_POST(
                       "/present-proof/create-request", proof_request_web_request
                   )
                   pres_req_id = proof_request["presentation_exchange_id"]
                   url = (
                       os.getenv("WEBHOOK_TARGET")
                       or (
                           "http://"
                           + os.getenv("DOCKERHOST").replace(
                               "{PORT}", str(agent.agent.admin_port + 1)
                           )
                           + "/webhooks"
                       )
                   ) + f"/pres_req/{pres_req_id}/"
                   log_msg(f"Proof request url: {url}")
                   # depois, retirar essa integracao com qrcode
                   qr = qrcode(border=1)
                   qr.add_data(url)
                   log_msg(
                       "Scan the following QR code to accept the proof request from a mobile agent."
                   )
                   qr.print_ascii(invert=True)


               elif agent.aip == 20:
                   if agent.cred_type == CRED_FORMAT_INDY:
                       proof_request_web_request = (
                           agent.agent.generate_proof_request_web_request(
                               agent.aip,
                               agent.cred_type,
                               agent.revocation,
                               exchange_tracing,
                               connectionless=True,
                           )
                       )
                   elif agent.cred_type == CRED_FORMAT_JSON_LD:
                       proof_request_web_request = (
                           agent.agent.generate_proof_request_web_request(
                               agent.aip,
                               agent.cred_type,
                               agent.revocation,
                               exchange_tracing,
                               connectionless=True,
                           )
                       )
                   else:
                       raise Exception(
                           "Error invalid credential type:" + agent.cred_type
                       )


                   proof_request = await agent.agent.admin_POST(
                       "/present-proof-2.0/create-request", proof_request_web_request
                   )
                   pres_req_id = proof_request["pres_ex_id"]
                   url = (
                       "http://"
                       + os.getenv("DOCKERHOST").replace(
                           "{PORT}", str(agent.agent.admin_port + 1)
                       )
                       + "/webhooks/pres_req/"
                       + pres_req_id
                       + "/"
                   )
                   log_msg(f"Proof request url: {url}")
                   #qr = QRCode(border=1)
                   #qr.add_data(url)
                   log_msg(
                       "Scan the following QR code to accept the proof request from a mobile agent."
                   )
                   qr.print_ascii(invert=True)
               else:
                   raise Exception(f"Error invalid AIP level: {agent.aip}")


           elif option == "3":
               msg = await prompt("Enter message: ")
               await agent.agent.admin_POST(
                   f"/connections/{agent.agent.connection_id}/send-message",
                   {"content": msg},
               )


           elif option == "4":
               log_msg(
                   "Creating a new invitation, please receive "
                   "and accept this invitation using Alice agent"
               )
               await agent.generate_invitation(
                   display_qr=True,
                   reuse_connections=agent.reuse_connections,
                   wait=True,
               )


           elif option == "5" and agent.revocation:
               rev_reg_id = (await prompt("Enter revocation registry ID: ")).strip()
               cred_rev_id = (await prompt("Enter credential revocation ID: ")).strip()
               publish = (
                   await prompt("Publish now? [Y/N]: ", default="N")
               ).strip() in "yY"
               try:
                   await agent.agent.admin_POST(
                       "/revocation/revoke",
                       {
                           "rev_reg_id": rev_reg_id,
                           "cred_rev_id": cred_rev_id,
                           "publish": publish,
                           "connection_id": agent.agent.connection_id,
                           # leave out thread_id, let aca-py generate
                           # "thread_id": "12345678-4444-4444-4444-123456789012",
                           "comment": "Revocation reason goes here ...",
                       },
                   )
               except ClientError:
                   pass


           elif option == "6" and agent.revocation:
               try:
                   resp = await agent.agent.admin_POST(
                       "/revocation/publish-revocations", {}
                   )
                   agent.agent.log(
                       "Published revocations for {} revocation registr{} {}".format(
                           len(resp["rrid2crid"]),
                           "y" if len(resp["rrid2crid"]) == 1 else "ies",
                           json.dumps([k for k in resp["rrid2crid"]], indent=4),
                       )
                   )
               except ClientError:
                   pass


       if agent.show_timing:
           timing = await agent.agent.fetch_timing()
           if timing:
               for line in agent.agent.format_timing(timing):
                   log_msg(line)


   finally:
       terminated = await agent.terminate()


   await asyncio.sleep(0.1)


   if not terminated:
       os._exit(1)




if __name__ == "__main__":
   parser = arg_parser(ident="faber", port=8020)
   args = parser.parse_args()


   ENABLE_PYDEVD_PYCHARM = os.getenv("ENABLE_PYDEVD_PYCHARM", "").lower()
   ENABLE_PYDEVD_PYCHARM = ENABLE_PYDEVD_PYCHARM and ENABLE_PYDEVD_PYCHARM not in (
       "false",
       "0",
   )
   PYDEVD_PYCHARM_HOST = os.getenv("PYDEVD_PYCHARM_HOST", "localhost")
   PYDEVD_PYCHARM_CONTROLLER_PORT = int(
       os.getenv("PYDEVD_PYCHARM_CONTROLLER_PORT", 5001)
   )


   if ENABLE_PYDEVD_PYCHARM:
       try:
           import pydevd_pycharm


           print(
               "Faber remote debugging to "
               f"{PYDEVD_PYCHARM_HOST}:{PYDEVD_PYCHARM_CONTROLLER_PORT}"
           )
           pydevd_pycharm.settrace(
               host=PYDEVD_PYCHARM_HOST,
               port=PYDEVD_PYCHARM_CONTROLLER_PORT,
               stdoutToServer=True,
               stderrToServer=True,
               suspend=False,
           )
       except ImportError:
           print("pydevd_pycharm library was not found")


   try:
       asyncio.get_event_loop().run_until_complete(main(args))
   except KeyboardInterrupt:
       os._exit(1)