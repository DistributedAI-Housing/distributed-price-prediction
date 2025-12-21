import grpc
import file_pb2
import file_pb2_grpc

def run():
    with open('cert.pem','rb') as f:
        certificat = f.read()
    
    credentials = grpc.ssl_channel_credentials(root_certificates=certificat)

    channel = grpc.secure_channel('localhost:50051',credentials)
    stub = file_pb2_grpc.ConcatenationStub(channel)

    chaines = file_pb2.Attribut(a="Oussama" , b="Assraoui")
    print('=========')
    stub.Concat(chaines)
    # print("c'est bien")

    # print("resultat:",response.concat)

if __name__ == '__main__':
    run()