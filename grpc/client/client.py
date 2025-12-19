# =============================
# Imports & path
# =============================
import os
import sys
import grpc
import jwt
import time

# Ajouter grpc/ au PYTHONPATH pour trouver proto
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from proto import api_pb2, api_pb2_grpc

# =============================
# Configuration
# =============================
SERVER_ADDRESS = "localhost:50051"
SECRET_KEY = "raron"   # doit être le même que dans server.py

# =============================
# Générer un JWT (simulation login)
# =============================
def generate_token(user_id=1):
    payload = {
        "user_id": user_id,
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600  # 1 heure
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

# =============================
# Client gRPC
# =============================
def main():
    print("🔌 Connexion au serveur gRPC...")
    channel = grpc.insecure_channel(SERVER_ADDRESS)
    price_stub = api_pb2_grpc.PriceServiceStub(channel)
    user_stub  = api_pb2_grpc.UserServiceStub(channel)
    # Générer token JWT
    token = generate_token(user_id=1)
    metadata = [("authorization", token)]

    # =============================
    # 1️⃣ Prédiction de prix
    # =============================
    try:
        print("📊 Envoi de la requête PredictPrice...")
        request = api_pb2.PriceRequest(
            proprety_type="Apartment",
            surface=106.0,
            bedroom=2,
            bathroom =1,
            address="Rabat" ,
            city= "Rabat" ,
            principale= "Rabat-Salé-Kénitra",
            
        )

        response = price_stub.PredictPrice(request, metadata=metadata)
        print("✅ Prix prédit :", response.price)

    except grpc.RpcError as e:
        print("❌ Erreur PredictPrice :", e.details())
        return

    # =============================
    # 2️⃣ Historique des prédictions
    # =============================
    try:
        print("\n📜 Récupération de l'historique...")
        history_request = api_pb2.UserHistoryRequest()

        history_response = user_stub.GetHistory(
            history_request,
            metadata=metadata
        )
        if not history_response.predictions:
            print("ℹ️ Aucun historique trouvé")
        else:
            for h in history_response.predictions:
                print(
                    f"- {h.proprety_type} | "
                    f"- {h.surface} m² | "
                    f"{h.bedroom} chambres | "
                    f"{h.bathroom} WC | "
                    f"{h.address} Addresse  | "
                    f"{h.city} Ville | "
                    f"{h.principale} Region | "
                    f"Prix: {h.price} | "
                    f"Date: {h.created_at}"
                )

    except grpc.RpcError as e:
        print("❌ Erreur GetHistory :", e.details())

# =============================
# Main
# =============================
if __name__ == "__main__":
    main()
