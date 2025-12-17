import grpc
import mysql.connector
from proto import api_pb2, api_pb2_grpc

class UserService(api_pb2_grpc.UserServiceServicer):
    """
    Service pour gérer le profil et l'historique des utilisateurs.
    """

    def GetProfile(self, request, context):
        # Récupérer user_id depuis JWT / AuthInterceptor
        user_id = context.user_id

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="real_estate_db"
            )
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, name, email FROM users WHERE id=%s", (user_id,))
            user = cursor.fetchone()
        except mysql.connector.Error as err:
            print(f"[MySQL Error] {err}")
            context.abort(grpc.StatusCode.INTERNAL, "Database error")
        finally:
            cursor.close()
            conn.close()

        if not user:
            context.abort(grpc.StatusCode.NOT_FOUND, "User not found")

        return api_pb2.UserProfileResponse(
            id=user['id'],
            name=user['name'],
            email=user['email'],
             profile_image_path=user['profile_image_path']
        )

    def GetHistory(self, request, context):
        # Récupérer user_id depuis JWT / AuthInterceptor
        user_id = context.user_id

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="real_estate_db"
            )
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT proprety_type, surface, bedroom, bathroom, price, created_at
                FROM predictions
                WHERE user_id=%s
                ORDER BY created_at DESC
            """, (user_id,))
            rows = cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"[MySQL Error] {err}")
            context.abort(grpc.StatusCode.INTERNAL, "Database error")
        finally:
            cursor.close()
            conn.close()

        history = [
            api_pb2.PredictionRecord(
               proprety_type=row['proprety_type'],
        surface=row['surface'],
        bedroom=row['bedroom'],
        bathroom=row['bathroom'],
        price=row['price'],  
        address=row['address'],
        city=row['city'],
        principale=row['principale'],
        created_at=str(row['created_at'])
            )
            for row in rows
        ]

        return api_pb2.HistoryResponse(predictions=history)
