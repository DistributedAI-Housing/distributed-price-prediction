import grpc
import Client_Interceptor_pb2
import Client_Interceptor_pb2_grpc

def run():
    with open('cert.pem','rb') as f:
        certificat = f.read()
    
    credentials = grpc.ssl_channel_credentials(root_certificates=certificat)

    channel = grpc.secure_channel('localhost:50051',credentials)
    stub = Client_Interceptor_pb2_grpc.PredictionStub(channel)

# a et b sont les mêmes du proto  
    chaines = Client_Interceptor_pb2.Attribut(proprety_type="Appartement" , surface= 240 , bedroom=5,
                                            bathroom = 3 , address="Ménara, Marrakech, Marrakech-Safi",
                                            city="Marrakech" , principale="Marrakech-Safi")
    print('=========')
    response = stub.Prd(chaines)
    # print("c'est bien")

    print("resultat:",response.prix)

if __name__ == '__main__':
    run()