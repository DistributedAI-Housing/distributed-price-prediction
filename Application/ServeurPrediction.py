import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
# from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

import grpc
from concurrent import futures
import Interceptor_ServerPred_pb2
import Interceptor_ServerPred_pb2_grpc

class ServerPredection(Interceptor_ServerPred_pb2_grpc.PredictionServicer):
    def Pred(self,request,context):
        df = pd.read_csv('Data/processed/cleaned_data.csv')

        X = df.drop('price_dh', axis=1)
        y = df['price_dh']

        num_cols = ['surface', 'bedroom', 'bathroom']
        cat_cols = ['proprety_type', 'address', 'city', 'principale']

        preprocess = ColumnTransformer([
        ('num', StandardScaler(), num_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols)
        ])

        X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
        )

        model = Pipeline([
        ('preprocess', preprocess),
        ('regressor', RandomForestRegressor(
            n_estimators=300,     
            max_depth=None,       
            random_state=42,
            n_jobs=-1             
            ))
        ])

        model.fit(X_train, y_train)
        pr = model.predict(
            pd.DataFrame([{
                'proprety_type': request.proprety_type,
                'surface': request.surface,
                'bedroom': request.bedroom,
                'bathroom': request.bathroom,
                'address': request.address,
                'city': request.city,
                'principale': request.principale
            }])
        )[0]
        return Interceptor_ServerPred_pb2.Prix(prix=pr)

def serve():
        # je peux la nommée comme je veux
    with open('cert.pem','rb') as f:
        certificat = f.read()
        
    with open('key.pem','rb') as f:
        private_key = f.read()

    credentials = grpc.ssl_server_credentials([(private_key,certificat)])

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Ça veut dire que le serveur peut traiter jusqu’à 10 requêtes RPC en même temps.
    Interceptor_ServerPred_pb2_grpc.add_PredictionServicer_to_server(ServerPredection(),server)
    
    # Démarrer une connexion sécurisé

    server.add_secure_port('[::]:50052',credentials)
    server.start()
    print("Serveur Démarre sue le port 50052")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()

