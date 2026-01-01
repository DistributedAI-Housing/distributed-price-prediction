import os
import sys
import uuid
import logging
import grpc
import jwt
import time      # <--- C'était probablement ça qui manquait !
import datetime 
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# --- 1. GESTION DES CHEMINS ---
current_dir = os.path.dirname(os.path.abspath(__file__)) 
root_dir = os.path.dirname(os.path.dirname(current_dir)) 
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from backend.proto import api_pb2, api_pb2_grpc
except ImportError as e:
    print("ERREUR D'IMPORT GRPC :", e)
    sys.exit(1)

# --- 2. CONFIGURATION GLOBALE ---
app = Flask(__name__)
app.secret_key = 'raron' 
GRPC_SECRET_KEY = "raron"
SERVER_ADDRESS = "localhost:50051"  # <--- INDISPENSABLE POUR gRPC

# Config DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/real_estate_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Config Uploads
BASE_CLIENT_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_CLIENT_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
logging.basicConfig(level=logging.INFO)

# --- 3. MODÈLE USER ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_image_path = db.Column(db.String(256), default='default.png')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_photo_url(self):
        if not self.profile_image_path or self.profile_image_path == 'default.png':
            return 'https://via.placeholder.com/150'
        return url_for('static', filename='uploads/' + self.profile_image_path)

with app.app_context():
    db.create_all()

# --- 4. UTILITAIRES ---
def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

@app.context_processor
def inject_user():
    return {'user': get_current_user(),
            'get_current_user': get_current_user,
            'User': User}

# --- 5. ROUTES PRINCIPALES ---
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        file = request.files.get('profile_picture')
        filename = 'default.png'
        if file and file.filename:
            ext = file.filename.split('.')[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        if User.query.filter_by(email=email).first():
            return render_template('signup.html', error="Email déjà utilisé")

        new_user = User(name=name, email=email, profile_image_path=filename)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            return redirect(url_for('predict'))
        
        return render_template('login.html', error="Identifiants invalides")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    user = get_current_user()
    if not user: return redirect(url_for('login'))
    return render_template('profile.html', user=user)

# --- 6. ROUTE PREDICT (CORRIGÉE AVEC LES BONS IMPORTS) ---
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    predicted_price = None
    history = [] 

    # Préparation du Token
    payload = {
        "user_id": user.id,
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600
    }
    token = jwt.encode(payload, GRPC_SECRET_KEY, algorithm="HS256")
    metadata = [("authorization", token)]

    if request.method == 'POST':
        print("🔴 1. Formulaire POST reçu !") 
        try:
            # Récupération des données (Conforme au HTML de votre collègue)
            surface = float(request.form.get('surface', 0))
            bedroom = int(request.form.get('bedroom', 0))
            bathroom = int(request.form.get('bathroom', 0))
            prop_type = request.form.get('property_type', 'Apartment')
            city = request.form.get('city', 'Rabat')
            address = request.form.get('address', 'Non spécifiée')
            principale = request.form.get('principale', 'Rabat-Salé-Kénitra')

            print(f"🔴 2. Données: {surface}m2, {city}, {prop_type}")

            # Appel gRPC
            with grpc.insecure_channel(SERVER_ADDRESS) as channel:
                print("🔴 3. Connexion gRPC...")
                price_stub = api_pb2_grpc.PriceServiceStub(channel)
                
                request_grpc = api_pb2.PriceRequest(
                    proprety_type=prop_type,
                    surface=surface,
                    bedroom=bedroom,
                    bathroom=bathroom,
                    address=address,
                    city=city,
                    principale=principale
                )

                print("🔴 4. Envoi...")
                response = price_stub.PredictPrice(request_grpc, metadata=metadata)
                print(f"🔴 5. Prix reçu : {response.price}")
                
                predicted_price = f"{response.price:,.2f} DH"

        except grpc.RpcError as e:
            print(f"🔴 ERREUR gRPC : {e.details()}")
            predicted_price = "Erreur Serveur (Vérifiez le terminal)"
        except Exception as e:
            print(f"🔴 ERREUR PYTHON : {e}")
            predicted_price = f"Erreur Interne: {e}" # Affiche l'erreur sur le site aussi

    # Récupération de l'HISTORIQUE
    try:
        with grpc.insecure_channel(SERVER_ADDRESS) as channel:
            user_stub = api_pb2_grpc.UserServiceStub(channel)
            history_response = user_stub.GetHistory(api_pb2.UserHistoryRequest(), metadata=metadata)
            history = history_response.predictions
    except Exception as e:
        print(f"🔴 Erreur Historique : {e}")

    return render_template('predict.html', 
                           predicted_price=predicted_price,
                           history=history, 
                           user=user)

# --- ROUTES STATIQUES ---
@app.route('/team')
def team(): return render_template('team.html')

@app.route('/contact')
def contact(): return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)