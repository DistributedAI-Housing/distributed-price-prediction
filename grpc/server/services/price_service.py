import grpc
import mysql.connector
import pickle
import numpy as np
from proto import api_pb2, api_pb2_grpc

class PriceService(api_pb2_grpc.PriceServiceServicer):

    def __init__(self):
        # Charger le modèle ML
        with open("model.pkl", "rb") as f:
            self.model = pickle.load(f)

    def PredictPrice(self, request, context):
        # Récupérer l'user_id depuis le contexte (AuthInterceptor)
        user_id = context.user_id  

        # Préparer les features pour le modèle
        # Ici on prend juste les colonnes principales pour l'exemple
        # Adapte selon ton pipeline ML
        features = np.array([[request.proprety_type, request.surface, request.bedroom, request.bathroom]])
        prediction = self.model.predict(features)[0]

        # Enregistrer la prédiction dans MySQL
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="real_estate_db"
            )
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO predictions 
                (user_id, proprety_type, surface, bedroom, bathroom, address, city, principale, price) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    request.proprety_type,
                    request.surface,
                    request.bedroom,
                    request.bathroom,
                    request.address,
                    request.city,
                    request.principale,
                    float(prediction)
                )
            )
            conn.commit()
        except mysql.connector.Error as err:
            print(f"[MySQL Error] {err}")
            context.abort(grpc.StatusCode.INTERNAL, "Database error")
        finally:
            cursor.close()
            conn.close()

        # Retourner la prédiction
        return api_pb2.PriceResponse(
            success=True,
            price=float(prediction),
            message="Prediction successful"
        )
