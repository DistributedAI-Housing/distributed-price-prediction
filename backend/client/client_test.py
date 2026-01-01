# client.py
import grpc
from proto import price_pb2, price_pb2_grpc

def run():
    # Connexion au serveur gRPC
    channel = grpc.insecure_channel('localhost:50051')
    stub = price_pb2_grpc.PriceServiceStub(channel)

    # Préparer la requête
    request = price_pb2.PriceRequest(
        proprety_type="apartment",
        surface=80,
        bedroom=2,
        bathroom=1,
        address="123 Main Street",
        city="Casablanca",
        principale=True
    )

    # Appeler le RPC PredictPrice
    response = stub.PredictPrice(request)
    print("Predicted price:", response.price)
    print("Message:", response.message)

if __name__ == "__main__":
    run()
