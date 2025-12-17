import sys
import os
import grpc

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from proto import user_pb2, user_pb2_grpc
from proto import price_pb2, price_pb2_grpc

# Connexion au serveur
channel = grpc.insecure_channel("localhost:50051")
user_stub = user_pb2_grpc.UserServiceStub(channel)
price_stub = price_pb2_grpc.PriceServiceStub(channel)

# 1️⃣ Inscription
try:
    response = user_stub.RegisterUser(user_pb2.RegisterRequest(
        nom="Rim",
        prenom="Bari",
        email="rim@example.com",
        password="123456",
        photo="photo_url"
    ))
    print(response.message)
except grpc.RpcError as e:
    print("Erreur inscription:", e.details())

# 2️⃣ Login
try:
    response = user_stub.LoginUser(user_pb2.LoginRequest(
        email="rim@example.com",
        password="123456"
    ))
    print(response.message)
    token = response.token
except grpc.RpcError as e:
    print("Erreur login:", e.details())
    exit()

# Metadata pour authentification
metadata = [("authorization", token)]

# 3️⃣ Prédiction
try:
    pred = price_stub.PredictPrice(price_pb2.PriceRequest(
        proprety_type="House",
        surface=120.0,
        bedroom=3,
        bathroom=2,
        address="123 Rue Exemple",
        city="Casablanca",
        principale="Centre"
    ), metadata=metadata)
    print("Prix prédit:", pred.price)
except grpc.RpcError as e:
    print("Erreur prédiction:", e.details())

# 4️⃣ Récupérer historique
try:
    history_resp = user_stub.GetHistory(user_pb2.HistoryRequest(token=token))
    print("Historique prédictions:")
    for h in history_resp.history:
        print(h.proprety_type, h.surface, h.price, h.date)
except grpc.RpcError as e:
    print("Erreur historique:", e.details())
