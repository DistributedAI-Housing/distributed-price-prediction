# =============================
# Imports système & chemins
# =============================
from concurrent import futures
import os

from pyexpat import features
import sys
import time
import pandas as pd

import grpc
import jwt
import numpy as np
import mysql.connector
from joblib import load
from pandas import DataFrame


# Ajouter grpc/ au PYTHONPATH pour trouver proto
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from proto import api_pb2, api_pb2_grpc

print("✅ server.py chargé")

# =============================
# Configuration
# =============================
SECRET_KEY = "raron"

# =============================
# Interceptors
# =============================
class AuthInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        meta = dict(handler_call_details.invocation_metadata)
        token = meta.get("authorization")

        handler = continuation(handler_call_details)

        def unary_unary(request, context):
            if not token:
                context.abort(grpc.StatusCode.UNAUTHENTICATED, "Token manquant")
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                context.user_id = payload.get("user_id")
            except jwt.ExpiredSignatureError:
                context.abort(grpc.StatusCode.UNAUTHENTICATED, "Token expiré")
            except jwt.InvalidTokenError:
                context.abort(grpc.StatusCode.UNAUTHENTICATED, "Token invalide")

            return handler.unary_unary(request, context)

        return grpc.unary_unary_rpc_method_handler(
            unary_unary,
            request_deserializer=handler.request_deserializer,
            response_serializer=handler.response_serializer,
        )

class LoggingInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        print(f"[LOG] Appel : {handler_call_details.method}")
        return continuation(handler_call_details)

class TimingInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        start = time.time()
        handler = continuation(handler_call_details)
        end = time.time()
        print(f"[TIMING] {handler_call_details.method} → {end - start:.4f}s")
        return handler

# =============================
# Service gRPC
# =============================
class PriceService(api_pb2_grpc.PriceServiceServicer):
    def __init__(self):
        SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
        MODEL_PATH = os.path.join(SERVER_DIR, "models", "price_model.pkl")

        print("📦 Chargement du modèle ML...")
        self.model = load(MODEL_PATH)
        print("✅ Modèle chargé")

    def PredictPrice(self, request, context):
        user_id = getattr(context, "user_id", None)

        input_df = pd.DataFrame([{
        "proprety_type": request.proprety_type,
        "surface": request.surface,
        "bedroom": request.bedroom,
        "bathroom": request.bathroom,
        "address":request.address,
        "city": request.city,
        "principale": request.principale
    }])
        prediction = float(self.model.predict(input_df)[0])

        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="real_estate_db"
        )
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO predictions (user_id, proprety_type, surface,
            bedroom,bathroom, price,city,address,principale)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)
            """,
        (user_id, request.proprety_type, request.surface, request.bedroom,request.bathroom,
          prediction,request.city,request.address,request.principale )
    )
        conn.commit()
        cursor.close()
        conn.close()

        return api_pb2.PriceResponse(price=prediction)
class UserService(api_pb2_grpc.UserServiceServicer):

    def GetHistory(self, request, context):
        user_id = getattr(context, "user_id", None)

        if not user_id:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "User not authenticated")

        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="real_estate_db"
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
           SELECT proprety_type, surface, bedroom, bathroom,
           address, city, principale, price, created_at
    FROM predictions
    WHERE user_id=%s
            ORDER BY created_at DESC
            """,
            (user_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        history = [
            api_pb2.PredictionRecord(
               proprety_type=row["proprety_type"],
                surface=row["surface"],
                bedroom=row["bedroom"],
                bathroom=row["bathroom"],
                address=row["address"],
                city=row["city"],
                principale=row["principale"],
                price=row["price"],
                created_at=str(row["created_at"])
            )
            for row in rows
        ]

        return api_pb2.HistoryResponse(predictions=history)

# =============================
# Lancement du serveur
# =============================
def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=[
            LoggingInterceptor(),
            TimingInterceptor(),
            AuthInterceptor()
        ]
    )

    api_pb2_grpc.add_PriceServiceServicer_to_server(
        PriceService(), server
    )

    api_pb2_grpc.add_UserServiceServicer_to_server(
        UserService(), server
)
    server.add_insecure_port("[::]:50051")
    server.start()

    print("🚀 gRPC server running on port 50051")

    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        print("🛑 Server stopped")
        server.stop(0)

# =============================
# Main
# =============================
if __name__ == "__main__":
    serve()
