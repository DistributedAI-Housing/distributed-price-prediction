import grpc
from concurrent import futures
import time
import mysql.connector
import pickle
import numpy as np
import jwt

from proto import price_pb2, price_pb2_grpc

# -----------------------------
# Interceptors
# -----------------------------
SECRET_KEY = "raron"

class AuthInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        meta = dict(handler_call_details.invocation_metadata)
        token = meta.get("authorization")

        if not token:
            context = grpc.ServicerContext()
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Token manquant")

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            handler_call_details.user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            context = grpc.ServicerContext()
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Token expiré")
        except jwt.InvalidTokenError:
            context = grpc.ServicerContext()
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Token invalide")

        return continuation(handler_call_details)

class LoggingInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        print(f"[LOG] Appel méthode : {handler_call_details.method}")
        return continuation(handler_call_details)

class TimingInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        start_time = time.time()
        response = continuation(handler_call_details)
        end_time = time.time()
        print(f"[TIMING] {handler_call_details.method} exécuté en {end_time - start_time:.4f}s")
        return response

# -----------------------------
# Service de prédiction
# -----------------------------
class PriceService(price_pb2_grpc.PriceServiceServicer):
    def __init__(self):
        # Charger le modèle ML
        with open("model.pkl", "rb") as f:
            self.model = pickle.load(f)

    def PredictPrice(self, request, context):
        user_id = context.user_id  # récupéré depuis AuthInterceptor

        # Préparer les features pour le modèle
        # Attention : adapter selon ton preprocessing réel
        features = np.array([[request.proprety_type, request.surface, request.bedroom]])
        prediction = self.model.predict(features)[0]

        # Enregistrer la prédiction dans MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="real_estate_db"
        )
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO predictions (user_id, proprety_type, surface, bedroom, predicted_price) VALUES (%s, %s, %s, %s, %s)",
            (user_id, request.proprety_type, request.surface, request.bedroom, float(prediction))
        )
        conn.commit()
        cursor.close()
        conn.close()

        return price_pb2.PriceResponse(price=float(prediction))

    # Méthode pour récupérer l'historique
    def GetHistory(self, request, context):
        user_id = context.user_id

        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="real_estate_db"
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT proprety_type, surface, city, predicted_price, created_at "
            "FROM predictions WHERE user_id=%s ORDER BY created_at DESC",
            (user_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        history = [price_pb2.PredictionRecord(
            proprety_type=row['proprety_type'],
            surface=row['surface'],
            bedroom=row['bedroom'],
            predicted_price=row['predicted_price'],
            created_at=str(row['created_at'])
        ) for row in rows]

        return price_pb2.HistoryResponse(predictions=history)

# -----------------------------
# Lancement du serveur
# -----------------------------
def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=[LoggingInterceptor(), TimingInterceptor(), AuthInterceptor()]
    )

    price_pb2_grpc.add_PriceServiceServicer_to_server(PriceService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("🚀 gRPC server running on port 50051")

    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == "__main__":
    serve()
