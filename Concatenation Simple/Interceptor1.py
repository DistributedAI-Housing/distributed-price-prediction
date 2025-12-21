# from kivy.uix.gridlayout import accumulate
import grpc

from concurrent import futures
from google.protobuf import empty_pb2

import file1_pb2
import file1_pb2_grpc
import file_pb2
import file_pb2_grpc

class Concatenation(file_pb2_grpc.ConcatenationServicer):
    # Démarrer la connection avec le serveur
    def __init__(self):
        with open('cert.pem','rb') as f:
            certificat = f.read()
    
        credentials = grpc.ssl_channel_credentials(root_certificates=certificat)

        channel = grpc.secure_channel('localhost:50052',credentials)
        self.stub = file1_pb2_grpc.ChadWsqotStub(channel)


    # Correspond à la méthode que je définie dans le fichier .proto(le même nom)
    def Concat(self, request, context):
        # a et b son définie dans le fichier .proto
        # request et context peuvent prendre n'importe quelle nom
        # result = request.a + request.b

        # Forward vers Server2
        '''self.server2_stub.ForwardData(
            file1_pb2.ForwardRequest(message=request.message)
        )'''

        self.stub.Concat(
            file1_pb2.Attribut(a = request.a ,
                               b = request.b)
        )

        return empty_pb2.Empty()
        # return file_pb2.Result(concat = result)
    
def serve():
        # je peux la nommée comme je veux
    with open('cert.pem','rb') as f:
        certificat = f.read()
        
    with open('key.pem','rb') as f:
        private_key = f.read()

    credentials = grpc.ssl_server_credentials([(private_key,certificat)])

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Ça veut dire que le serveur peut traiter jusqu’à 10 requêtes RPC en même temps.
    file_pb2_grpc.add_ConcatenationServicer_to_server(Concatenation(),server)

        # Démarrer une connexion sécurisé

    server.add_secure_port('[::]:50051',credentials)
    server.start()
    print("Serveur Démarre sue le port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()