# from kivy.uix.gridlayout import accumulate
import grpc

from concurrent import futures

import Interceptor_ServerPred_pb2
import Interceptor_ServerPred_pb2_grpc
import Client_Interceptor_pb2
import Client_Interceptor_pb2_grpc

class Prediction(Client_Interceptor_pb2_grpc.PredictionServicer):
    # Démarrer la connection avec le serveur
    def __init__(self):
        with open('cert.pem','rb') as f:
            certificat = f.read()
    
        credentials = grpc.ssl_channel_credentials(root_certificates=certificat)

        channel = grpc.secure_channel('localhost:50052',credentials)
        self.stub = Interceptor_ServerPred_pb2_grpc.PredictionStub(channel)


    # Correspond à la méthode que je définie dans le fichier .proto(le même nom)
    def Prd(self, request, context):
        # a et b son définie dans le fichier .proto
        # request et context peuvent prendre n'importe quelle nom
        # result = request.a + request.b

        response = self.stub.Pred(
            Interceptor_ServerPred_pb2.Featers(proprety_type = request.proprety_type , surface = request.surface ,
                                               bedroom = request.bedroom , bathroom = request.bathroom ,
                                               address = request.address , city = request.city ,
                                               principale = request.principale)
        )

        return Client_Interceptor_pb2.Result(prix=response.prix)
    
def serve():
        # je peux la nommée comme je veux
    with open('cert.pem','rb') as f:
        certificat = f.read()
        
    with open('key.pem','rb') as f:
        private_key = f.read()

    credentials = grpc.ssl_server_credentials([(private_key,certificat)])

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Ça veut dire que le serveur peut traiter jusqu’à 10 requêtes RPC en même temps.
    Client_Interceptor_pb2_grpc.add_PredictionServicer_to_server(Prediction(),server)

        # Démarrer une connexion sécurisé

    server.add_secure_port('[::]:50051',credentials)
    server.start()
    print("Serveur Démarre sue le port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()