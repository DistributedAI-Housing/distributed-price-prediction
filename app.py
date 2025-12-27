from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import joblib
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid # Pour générer des noms de fichiers uniques

# --- 1. CONFIGURATION DE L'APPLICATION ---
app = Flask(__name__)
# CLÉ SECRÈTE OBLIGATOIRE POUR LES SESSIONS
app.secret_key = 'votre_cle_secrete_tres_securisee_ici' 

# Dossiers pour les uploads et la BDD (À ADAPTER)
UPLOAD_FOLDER = 'uploads/profile_pics'
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Crée le dossier s'il n'existe pas
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configuration de la Base de Données MySQL (XAMPP)
# Doit correspondre à votre base de données 'real_estate_db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/real_estate_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Définition de l'URL par défaut de la photo
DEFAULT_PHOTO_URL = 'https://via.placeholder.com/40/1C2E4A/FFFFFF?text=UT'
DEFAULT_IMAGE_FILENAME = 'default_avatar.png'

# --- 2. MODÈLE DE DONNÉES (SQLAlchemy) ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    # MODIFIEZ CETTE LIGNE (128 -> 255)
    password_hash = db.Column(db.String(255), nullable=False) 
    
    profile_image_path = db.Column(db.String(256), default=DEFAULT_IMAGE_FILENAME)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_photo_url(self):
        if self.profile_image_path == DEFAULT_IMAGE_FILENAME:
            return DEFAULT_PHOTO_URL
        # Utilise la route 'uploaded_file' pour servir le fichier local
        return url_for('uploaded_file', filename=self.profile_image_path)


# --- 3. CRÉATION DES TABLES (S'assure que la table existe) ---
with app.app_context():
    db.create_all()


# --- 4. GESTION DES FICHIERS UPLOADÉS ---
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # Sert le fichier depuis le dossier d'upload
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# --- 5. ROUTES D'AUTHENTIFICATION MISES À JOUR ---

# UTILITAIRE : Fonction pour récupérer l'utilisateur connecté dans chaque route
def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

@app.context_processor
def inject_user():
    # Rendre 'User' et 'get_current_user' disponible pour tous les templates
    return {'User': User, 'get_current_user': get_current_user}


@app.route('/')
@app.route('/home')
def home():
    # L'utilisateur actuel est accessible via get_current_user() dans le template
    return render_template('home.html')

@app.route('/profile')
def profile():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
        
    return render_template('profile.html', user=user)


@app.route('/login', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    success = request.args.get('success')

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        # 🔍 DEBUG (TEMPORAIRE)
        print("===== LOGIN DEBUG =====")
        print("EMAIL SAISI :", email)
        print("PASSWORD SAISI :", password)
        print("USER TROUVÉ :", user)
        if user:
            print("HASH EN BASE :", user.password_hash)
        print("=======================")

        if user and user.check_password(password):
            session['user_id'] = user.id
            return redirect(url_for('predict'))

        return render_template(
            'login.html',
            error="Email ou mot de passe incorrect.",
            success=success
        )

    return render_template('login.html', success=success)

@app.route('/signup', methods=['GET', 'POST'])
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        profile_picture = request.files.get('profile_picture')

        # Vérifier si l'email existe déjà
        if User.query.filter_by(email=email).first():
            return render_template(
                'signup.html',
                error="Cet email est déjà utilisé."
            )

        # Vérifier confirmation du mot de passe
        if password != confirm_password:
            return render_template(
                'signup.html',
                error="Les mots de passe ne correspondent pas."
            )

        image_filename = DEFAULT_IMAGE_FILENAME

        if profile_picture and profile_picture.filename:
            ext = profile_picture.filename.rsplit('.', 1)[1].lower()
            image_filename = str(uuid.uuid4()) + '.' + ext
            profile_picture.save(
                os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            )

        new_user = User(
            name=name,
            email=email,
            profile_image_path=image_filename
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        # ❗ PAS de login automatique
        return redirect(url_for('login', success=1))

    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))


# --- 6. ROUTES SECONDAIRES & PRÉDICTION ---

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
        
    predicted_price = None

    if request.method == 'POST':
        data = request.form.to_dict()
        try:
            surface = float(data.get('surface', 0))
            bedroom = float(data.get('bedroom', 0))
            bathroom = float(data.get('bathroom', 0))

            predicted_price = (
                surface * 3500 +
                bedroom * 120000 +
                bathroom * 80000
            )
        except Exception as e:
            predicted_price = "Erreur de calcul. Veuillez vérifier vos entrées."
        
    attributes = [{'name': 'localisation', 'label': 'Localisation (Ville ou Quartier)', 'type': 'text', 'placeholder': 'Ex: Paris 16, Casablanca Anfa'}, {'name': 'surface', 'label': 'Surface (m²)', 'type': 'number', 'placeholder': 'Ex: 120'}, {'name': 'rooms', 'label': 'Nombre de pièces', 'type': 'number', 'placeholder': 'Ex: 4'}, {'name': 'bathrooms', 'label': 'Nombre de salles de bains', 'type': 'number', 'placeholder': 'Ex: 2'}, {'name': 'floor', 'label': 'Étage', 'type': 'number', 'placeholder': 'Ex: 3'}, {'name': 'age', 'label': 'Âge du bâtiment (années)', 'type': 'number', 'placeholder': 'Ex: 10'}, ]
    options = {'type': [('Apartment', 'Appartement'), ('Villa', 'Villa'), ('Studio', 'Studio')], 'furnished': [('yes', 'Oui'), ('no', 'Non')], }

    return render_template('predict.html', attributes=attributes, options=options, predicted_price=predicted_price, user=user)


# Routes de navigation
@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/team')
def team():
    return render_template('team.html')


if __name__ == '__main__':
    app.run(debug=True)