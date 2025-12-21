1) l'installation du gRPC avec la commande suivante : "pip install grpcio grpcio-tools"  
2) Créer le fichier .proto qui permet de définir la méthode à appeller et les entrées et la sortie.
3) Traduire le fichier .proto en fichier .py à l'aide de la commande : "python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. file.proto" ,  deux fichier seront générer 'file_pb2_grpc.py' qui contient la méthode appellée et 'file_pb2.py' qui contient les entrées et les sorties.
4) les connection sont sécurisées(certificat,klé privé)
    la commande pour créer la certificat et la klé privé:
    "openssl req -newkey rsa:40996 -x509 -days365 -nodes -out cert.pem -keyout key.pem"