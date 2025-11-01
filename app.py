import os
import logging
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import tensorflow as tf
import numpy as np
from PIL import Image
import json
import io
import base64
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production-2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# In-memory user database
USERS_DB = {
    'admin@cattle.com': {
        'password': generate_password_hash('admin123'),
        'name': 'Admin User',
        'role': 'admin'
    }
}

# Session storage for predictions
PREDICTIONS_LOG = []

# Global variables
master_model = None
master_config = None
specialist_models = {}
specialist_configs = {}

# Disease Medical Information Database - COMPLETE FOR ALL 4 DISEASES
DISEASE_INFO = {
    'lumpy': {
        'name': 'Lumpy Skin Disease (LSD)',
        'severity': 'HIGH',
        'description': 'Viral disease causing fever and skin nodules across the body',
        'immediate_actions': [
            'Isolate the affected animal IMMEDIATELY to prevent spread',
            'Measure body temperature (normal: 38-39°C)',
            'Provide clean, cool drinking water',
            'Keep the animal in a shaded, fly-free area',
            'Do NOT attempt to burst or drain nodules yourself'
        ],
        'first_aid': [
            'Apply antiseptic solution (Betadine) around nodules',
            'Give paracetamol (500mg per 100kg body weight) for fever',
            'Provide soft, easy-to-eat feed if mouth is affected',
            'Clean water should be available at all times'
        ],
        'emergency_signs': [
            'Body temperature above 40°C (104°F)',
            'Difficulty breathing or excessive drooling',
            'Refusal to eat or drink for more than 12 hours',
            'Swelling of limbs or udder',
            'Nodules becoming infected or oozing pus'
        ],
        'medicines': [
            {'name': 'Streptopenicillin', 'type': 'Antibiotic', 'brand': 'Terramycin/Penstrep'},
            {'name': 'Meloxicam', 'type': 'Anti-inflammatory', 'brand': 'Melonex'},
            {'name': 'AD3E Injection', 'type': 'Vitamin supplement', 'brand': 'Various'}
        ],
        'home_remedies': [
            'Apply neem oil paste on nodules (antiseptic)',
            'Turmeric powder mixed with coconut oil (anti-inflammatory)',
            'Give jaggery water for energy (100g per day)',
            'Feed crushed garlic cloves (5-6 daily) - natural antibiotic'
        ],
        'timeline': 'Incubation: 4-14 days | Acute phase: 7-14 days | Recovery: 4-6 weeks',
        'prognosis': 'Good with proper care, but notifiable disease - report to authorities'
    },
    'mastitis': {
        'name': 'Mastitis (Udder Infection)',
        'severity': 'MEDIUM-HIGH',
        'description': 'Bacterial infection of udder tissue causing inflammation and reduced milk production',
        'immediate_actions': [
            'Stop milking the affected quarter immediately',
            'Milk out the affected quarter gently to remove infected milk',
            'Apply cold water compress on swollen udder (15 mins)',
            'Isolate milk from affected quarter - do NOT mix with other milk',
            'Wash hands thoroughly before and after handling'
        ],
        'first_aid': [
            'Gently massage udder with warm water (not hot)',
            'Apply camphor oil or eucalyptus oil around udder',
            'Give pain relief - paracetamol (500mg per 100kg)',
            'Ensure the cow is lying on soft bedding',
            'Increase milking frequency to 3-4 times daily'
        ],
        'emergency_signs': [
            'Udder becomes very hot and hard',
            'Bloody or watery milk with foul smell',
            'Cow refuses to stand or walk',
            'Body temperature above 40°C',
            'Complete loss of milk production',
            'Gangrene (black discoloration) of udder tissue'
        ],
        'medicines': [
            {'name': 'Mastilone (Cloxacillin)', 'type': 'Intramammary antibiotic', 'brand': 'Mastilone/Mamyzin'},
            {'name': 'Enrofloxacin', 'type': 'Systemic antibiotic', 'brand': 'Enrocin/Baytril'},
            {'name': 'Meloxicam', 'type': 'Anti-inflammatory', 'brand': 'Various'},
            {'name': 'Oxytocin 10IU', 'type': 'Milk letdown aid', 'brand': 'Oxytocin injection'}
        ],
        'home_remedies': [
            'Apply hot fomentation with salt water (warm compress)',
            'Turmeric paste application on udder surface',
            'Feed fenugreek seeds (100g daily) - anti-inflammatory',
            'Aloe vera gel application for soothing effect',
            'Neem leaf decoction for washing udder'
        ],
        'timeline': 'Acute onset: 12-24 hours | Treatment: 5-7 days | Full recovery: 2-3 weeks',
        'prognosis': 'Good if treated early | Chronic cases may require culling quarter'
    },
    'fmd': {
        'name': 'Foot and Mouth Disease (FMD)',
        'severity': 'VERY HIGH',
        'description': 'Highly contagious viral disease causing blisters in mouth and on feet',
        'immediate_actions': [
            'ISOLATE IMMEDIATELY - FMD spreads very rapidly',
            'Report to local veterinary authorities (MANDATORY)',
            'Stop all animal movement on farm',
            'Disinfect all equipment, boots, and clothes',
            'Do NOT allow visitors to farm',
            'Quarantine entire herd'
        ],
        'first_aid': [
            'Rinse mouth with warm salt water (antiseptic)',
            'Apply glycerin on mouth lesions for soothing',
            'Clean feet with potassium permanganate solution',
            'Apply Stockholm tar or copper sulfate on foot lesions',
            'Provide soft, liquid feed - green fodder, gruel',
            'Give plenty of clean drinking water'
        ],
        'emergency_signs': [
            'High fever (40-41°C / 104-106°F)',
            'Excessive drooling and frothing',
            'Severe lameness - unable to stand',
            'Blisters rupturing and becoming infected',
            'Refusal to eat for more than 24 hours',
            'Heart complications (sudden death in young calves)'
        ],
        'medicines': [
            {'name': 'Oxytetracycline', 'type': 'Antibiotic (secondary infection)', 'brand': 'Terramycin LA'},
            {'name': 'Penicillin-Streptomycin', 'type': 'Antibiotic', 'brand': 'Various'},
            {'name': 'Flunixin', 'type': 'Anti-inflammatory', 'brand': 'Banamine'},
            {'name': 'B-Complex', 'type': 'Vitamin supplement', 'brand': 'Various'}
        ],
        'home_remedies': [
            'Rinse mouth with alum solution (antiseptic)',
            'Apply honey on mouth lesions (healing)',
            'Turmeric + coconut oil paste on foot lesions',
            'Give buttermilk with rock salt (hydration)',
            'Neem leaf decoction for foot bath'
        ],
        'timeline': 'Incubation: 2-14 days | Fever: 2-3 days | Blisters: 3-7 days | Recovery: 2-3 weeks',
        'prognosis': 'FMD is viral - no cure, only supportive care | Vaccination is key prevention'
    },
    'tongue_disease': {
        'name': 'Tongue Disease / Oral Lesions',
        'severity': 'MEDIUM',
        'description': 'Various conditions affecting tongue including ulcers, inflammation, and infections',
        'immediate_actions': [
            'Inspect mouth and tongue thoroughly for lesions',
            'Check for foreign objects stuck in mouth',
            'Rinse mouth with clean lukewarm water',
            'Stop feeding dry, rough fodder immediately',
            'Provide soft, moist feed only',
            'Isolate if contagious disease suspected'
        ],
        'first_aid': [
            'Rinse mouth with warm saline solution (1 tsp salt in 1L water)',
            'Apply glycerin or honey on tongue lesions',
            'Give soft green fodder or soaked feed',
            'Offer lukewarm water (not cold)',
            'Crush feed into small pieces',
            'Give jaggery for energy and palatability'
        ],
        'emergency_signs': [
            'Complete refusal to eat or drink',
            'Severe swelling of tongue',
            'Profuse drooling or frothing',
            'Blue or black discoloration of tongue',
            'High fever above 40°C',
            'Difficulty breathing due to tongue swelling',
            'Bleeding from mouth or tongue'
        ],
        'medicines': [
            {'name': 'Betadine gargle', 'type': 'Oral antiseptic', 'brand': 'Betadine/Povidone-iodine'},
            {'name': 'Amoxicillin', 'type': 'Antibiotic', 'brand': 'Various'},
            {'name': 'Meloxicam', 'type': 'Anti-inflammatory', 'brand': 'Various'},
            {'name': 'B-Complex', 'type': 'Vitamin supplement', 'brand': 'B-Complex injection'},
            {'name': 'Orasep gel', 'type': 'Healing gel', 'brand': 'Orasep/Thrush gel'}
        ],
        'home_remedies': [
            'Rinse with turmeric water (1 tsp in warm water) - antiseptic',
            'Apply pure honey on lesions - healing properties',
            'Alum powder mixed with glycerin - astringent',
            'Tender coconut water for hydration and healing',
            'Betel leaf paste application - antimicrobial',
            'Feed soft banana or papaya - easy to swallow'
        ],
        'timeline': 'Onset: Gradual over 2-3 days | Acute phase: 3-7 days | Healing: 7-14 days | Full recovery: 2-3 weeks',
        'prognosis': 'Good if treated within 48 hours | Advanced cases may NOT respond'
    }
}

# CORRECTED: Specialist model configuration with YOUR ACTUAL FILE PATHS
SPECIALIST_MODELS = {
    'general_body': {
        'name': 'Cattle Disease Classifier',
        'path': 'models/cattle_3class_classifier.keras',  # YOUR ACTUAL FILE
        'classes': ['Lumpy Skin Disease', 'Not Cattle', 'Healthy Cow']
    },
    'foot': {
        'name': 'Footrot (FMD) Classifier',
        'path': 'models/footrot_mobilenet_final_model.keras',  # YOUR ACTUAL FILE
        'classes_file': 'models/footrot_class_indices.json'
    },
    'udder': {
        'name': 'Udder Health Classifier',
        'path': 'models/cattle_udder_mobilenet_model.h5',  # YOUR ACTUAL FILE
        'classes': ['NON CATTLE IMAGES', 'mastitis teats', 'normal teats']
    },
    'tongue': {
        'name': 'Tongue Disease Classifier',
        'path': 'models/tongue_classification_mobilenetv2.h5',  # YOUR ACTUAL FILE
        'classes_file': 'models/tongue_model_config.json'
    }
}

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return redirect(url_for('login'))
        user = USERS_DB.get(session['user_email'])
        if not user or user.get('role') != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def load_master_model():
    global master_model, master_config
    try:
        master_path = 'models/master_cattle_classifier.keras'
        config_path = 'models/master_class_indices.json'
        
        if not os.path.exists(master_path):
            logger.error(f"❌ Master model not found: {master_path}")
            return False
        
        logger.info("🔄 Loading Master Model...")
        master_model = tf.keras.models.load_model(master_path, compile=False)
        master_model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                master_config = json.load(f)
        else:
            master_config = {'class_names': ['foot', 'general_body', 'non_cattle', 'tongue', 'udder']}
        
        logger.info(f"✅ Master Model loaded! Classes: {master_config['class_names']}")
        return True
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

def load_specialist_models():
    """Load all specialist models with compatibility fixes"""
    global specialist_models, specialist_configs
    
    loaded_count = 0
    
    for model_key, info in SPECIALIST_MODELS.items():
        try:
            if not os.path.exists(info['path']):
                logger.warning(f"⚠️ Specialist model not found: {info['path']}")
                continue
            
            logger.info(f"🔄 Loading {info['name']}...")
            
            # Handle different Keras versions
            try:
                model = tf.keras.models.load_model(info['path'], compile=False)
            except Exception as e:
                if 'batch_shape' in str(e) or 'InputLayer' in str(e):
                    logger.warning(f"⚠️ Compatibility issue, trying custom_objects...")
                    from tensorflow.keras.layers import InputLayer
                    custom_objects = {'InputLayer': InputLayer}
                    model = tf.keras.models.load_model(
                        info['path'], 
                        compile=False,
                        custom_objects=custom_objects
                    )
                else:
                    raise e
            
            model.compile(
                optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            
            specialist_models[model_key] = model
            
            # Load class mapping
            if 'classes_file' in info:
                if os.path.exists(info['classes_file']):
                    with open(info['classes_file'], 'r') as f:
                        class_data = json.load(f)
                    
                    if 'class_names' in class_data:
                        specialist_configs[model_key] = class_data['class_names']
                    elif 'class_indices' in class_data:
                        indices = class_data['class_indices']
                        specialist_configs[model_key] = [None] * len(indices)
                        for class_name, idx in indices.items():
                            specialist_configs[model_key][idx] = class_name
                    else:
                        specialist_configs[model_key] = [None] * len(class_data)
                        for class_name, idx in class_data.items():
                            specialist_configs[model_key][idx] = class_name
                else:
                    specialist_configs[model_key] = info.get('classes', [])
            else:
                specialist_configs[model_key] = info['classes']
            
            logger.info(f"✅ {info['name']} loaded!")
            loaded_count += 1
            
        except Exception as e:
            logger.error(f"❌ Error loading {info['name']}: {e}")
    
    logger.info(f"\n✅ Loaded {loaded_count}/{len(SPECIALIST_MODELS)} specialists!")
    return loaded_count > 0

def preprocess_image(image, target_size=(224, 224)):
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image = image.resize(target_size)
    img_array = np.array(image) / 255.0
    return np.expand_dims(img_array, axis=0)

def get_disease_key(class_name):
    """Map predicted class to disease key for medical info"""
    class_lower = class_name.lower()
    if 'lumpy' in class_lower:
        return 'lumpy'
    elif 'mastitis' in class_lower:
        return 'mastitis'
    elif 'fmd' in class_lower or 'foot' in class_lower:
        return 'fmd'
    elif 'tongue' in class_lower or 'disease' in class_lower:
        return 'tongue_disease'
    return None

def predict_with_master(image):
    processed_img = preprocess_image(image)
    master_predictions = master_model.predict(processed_img, verbose=0)
    body_part_idx = np.argmax(master_predictions[0])
    body_part_confidence = float(np.max(master_predictions[0]))
    body_part = master_config['class_names'][body_part_idx]
    
    master_probabilities = {master_config['class_names'][i]: float(master_predictions[0][i])
                           for i in range(len(master_config['class_names']))}
    
    if body_part == 'non_cattle':
        return {
            'success': True,
            'stage': 'master_only',
            'body_part': body_part,
            'body_part_confidence': body_part_confidence,
            'master_probabilities': master_probabilities,
            'predicted_class': 'Not Cattle',
            'confidence': body_part_confidence,
            'status': 'WARNING',
            'medical_info': None
        }
    
    if body_part not in specialist_models:
        return {'success': False, 'error': f'No specialist for {body_part}'}
    
    specialist_model = specialist_models[body_part]
    class_names = specialist_configs[body_part]
    
    specialist_predictions = specialist_model.predict(processed_img, verbose=0)
    disease_idx = np.argmax(specialist_predictions[0])
    disease_confidence = float(np.max(specialist_predictions[0]))
    disease_class = class_names[disease_idx]
    
    disease_probabilities = {class_names[i]: float(specialist_predictions[0][i])
                            for i in range(len(class_names))}
    
    combined_confidence = (body_part_confidence * 0.3 + disease_confidence * 0.7)
    
    # Get medical info
    disease_key = get_disease_key(disease_class)
    medical_info = DISEASE_INFO.get(disease_key)
    
    is_healthy = 'healthy' in disease_class.lower() or 'normal' in disease_class.lower()
    is_non_cattle = 'non' in disease_class.lower()
    
    if is_non_cattle:
        status = 'WARNING'
    elif is_healthy:
        status = 'HEALTHY'
    else:
        status = 'DISEASE'
    
    return {
        'success': True,
        'stage': 'two_stage',
        'body_part': body_part,
        'body_part_confidence': body_part_confidence,
        'master_probabilities': master_probabilities,
        'predicted_class': disease_class,
        'confidence': combined_confidence,
        'disease_confidence': disease_confidence,
        'specialist_probabilities': disease_probabilities,
        'specialist_used': SPECIALIST_MODELS[body_part]['name'],
        'status': status,
        'medical_info': medical_info
    }

def generate_pdf_report(prediction_data, user_info):
    """Generate PDF report"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24,
                                textColor=colors.HexColor('#2c3e50'), spaceAfter=30, alignment=TA_CENTER)
    story.append(Paragraph("🐄 Cattle Disease Detection Report", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Report info
    data = [
        ['Report Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        ['User:', user_info['name']],
        ['', ''],
        ['DIAGNOSIS RESULTS', ''],
        ['Body Part Detected:', prediction_data['body_part'].upper()],
        ['Disease/Condition:', prediction_data['predicted_class']],
        ['Confidence Level:', f"{prediction_data['confidence']*100:.2f}%"],
        ['Status:', prediction_data['status']],
    ]
    
    table = Table(data, colWidths=[2.5*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#e74c3c')),
        ('TEXTCOLOR', (0, 3), (-1, 3), colors.whitesmoke),
        ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    story.append(Spacer(1, 0.5*inch))
    
    # Medical information
    if prediction_data.get('medical_info'):
        med_info = prediction_data['medical_info']
        story.append(Paragraph("⚕️ MEDICAL RECOMMENDATIONS", styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))
        
        # Immediate actions
        story.append(Paragraph("⚠️ IMMEDIATE ACTIONS:", styles['Heading3']))
        for action in med_info['immediate_actions']:
            story.append(Paragraph(f"• {action}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Medicines
        story.append(Paragraph("💊 RECOMMENDED MEDICINES:", styles['Heading3']))
        for med in med_info['medicines']:
            story.append(Paragraph(f"• {med['name']} ({med['type']}) - Brand: {med['brand']}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
    
    # Disclaimer
    story.append(Spacer(1, 0.5*inch))
    disclaimer_style = ParagraphStyle('Disclaimer', parent=styles['Normal'], fontSize=9,
                                     textColor=colors.red, alignment=TA_CENTER)
    story.append(Paragraph("⚠️ MEDICAL DISCLAIMER: This report is for informational purposes only. Always consult a licensed veterinarian for accurate diagnosis and treatment.", disclaimer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = USERS_DB.get(email)
        if user and check_password_hash(user['password'], password):
            session['user_email'] = email
            session['user_name'] = user['name']
            session['user_role'] = user.get('role', 'user')
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        
        if email in USERS_DB:
            flash('Email already registered', 'warning')
        else:
            USERS_DB[email] = {
                'password': generate_password_hash(password),
                'name': name,
                'role': 'user'
            }
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_predictions = [p for p in PREDICTIONS_LOG if p['user_email'] == session['user_email']]
    return render_template('dashboard.html', predictions=user_predictions[-10:])

@app.route('/detect')
@login_required
def detect():
    return render_template('detect.html')

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    try:
        if master_model is None:
            return jsonify({'error': 'System not ready'}), 500
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        image = Image.open(file.stream)
        
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        result = predict_with_master(image)
        
        if not result['success']:
            return jsonify(result), 400
        
        result['image'] = f"data:image/jpeg;base64,{img_str}"
        result['confidence_percent'] = f"{(result['confidence'] * 100):.2f}%"
        result['timestamp'] = datetime.now().isoformat()
        
        # Log prediction
        log_entry = {
            'user_email': session['user_email'],
            'user_name': session['user_name'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'body_part': result['body_part'],
            'diagnosis': result['predicted_class'],
            'confidence': result['confidence']
        }
        PREDICTIONS_LOG.append(log_entry)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download_report', methods=['POST'])
@login_required
def download_report():
    try:
        data = request.json
        user_info = {'name': session['user_name'], 'email': session['user_email']}
        
        pdf_buffer = generate_pdf_report(data, user_info)
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f'cattle_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/admin')
@admin_required
def admin_panel():
    return render_template('admin.html', predictions=PREDICTIONS_LOG[-50:], users=USERS_DB)

if __name__ == '__main__':
    os.makedirs('models', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    print("="*60)
    print("🐄 CATTLE DISEASE DETECTION SYSTEM v3.0")
    print("="*60)
    
    load_master_model()
    load_specialist_models()
    
    print("\n✅ System Ready!")
    print("📍 http://localhost:5000")
    print("="*60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)