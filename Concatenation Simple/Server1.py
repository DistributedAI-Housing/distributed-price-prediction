import grpc

from concurrent import futures
from google.protobuf import empty_pb2

import file1_pb2
import file1_pb2_grpc

class Servclass(file1_pb2_grpc.ChadWsqotServicer):
    def Concat(self,request,context):
        k = request.a + request.b
        print("le message est :",k)
        return empty_pb2.Empty()
def serve():
        # je peux la nommée comme je veux
    with open('cert.pem','rb') as f:
        certificat = f.read()
        
    with open('key.pem','rb') as f:
        private_key = f.read()

    credentials = grpc.ssl_server_credentials([(private_key,certificat)])

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Ça veut dire que le serveur peut traiter jusqu’à 10 requêtes RPC en même temps.
    file1_pb2_grpc.add_ChadWsqotServicer_to_server(Servclass(),server)
    
    # Démarrer une connexion sécurisé

    server.add_secure_port('[::]:50052',credentials)
    server.start()
    print("Serveur Démarre sue le port 50052")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
