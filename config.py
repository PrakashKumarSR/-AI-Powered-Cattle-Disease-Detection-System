import os
from datetime import timedelta

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///cattle_care.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Security Configuration
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Application Configuration
    APP_NAME = "CattleCare AI"
    APP_VERSION = "1.0.0"
    
    # Model Configuration
    MODEL_PATH = 'models/cattle_disease_model.h5'
    CLASS_NAMES = [
        'Healthy Cow', 'Foot and Mouth Disease', 'Blackleg', 
        'Lumpy Skin Disease', 'Mastitis', 'Not Cattle'
    ]
    
    # Disease Information
    DISEASE_INFO = {
        'Healthy Cow': {
            'description': 'The cattle appears to be in good health with no visible signs of disease.',
            'treatment_protocol': [
                'Continue regular monitoring and maintenance',
                'Ensure proper nutrition and hydration',
                'Maintain vaccination schedule',
                'Regular health check-ups'
            ],
            'emergency_measures': [
                'No emergency measures required',
                'Continue standard care procedures'
            ],
            'additional_notes': 'Regular preventive care is recommended to maintain health.'
        },
        'Foot and Mouth Disease': {
            'description': 'Highly contagious viral disease affecting cloven-hoofed animals, characterized by fever and blister-like sores.',
            'treatment_protocol': [
                'Immediate isolation of infected animals',
                'Antiviral medication as prescribed by veterinarian',
                'Symptomatic treatment for fever and pain',
                'Soft, palatable feed and plenty of water',
                'Topical treatment for lesions'
            ],
            'emergency_measures': [
                'Notify veterinary authorities immediately',
                'Quarantine the entire farm',
                'Disinfect all equipment and premises',
                'Restrict movement of animals and people'
            ],
            'additional_notes': 'FMD is a reportable disease in many countries. Strict biosecurity measures must be implemented.'
        },
        'Blackleg': {
            'description': 'Acute, fatal disease caused by Clostridium chauvoei, characterized by muscle necrosis and gas production.',
            'treatment_protocol': [
                'High doses of antibiotics (penicillin)',
                'Anti-inflammatory medications',
                'Supportive care and fluids',
                'Surgical intervention in early stages'
            ],
            'emergency_measures': [
                'Immediate veterinary attention required',
                'Isolate affected animals',
                'Vaccinate healthy animals in the herd',
                'Proper disposal of carcasses'
            ],
            'additional_notes': 'Vaccination is highly effective for prevention. Disease often affects well-fed young cattle.'
        },
        'Lumpy Skin Disease': {
            'description': 'Viral disease causing skin nodules, fever, and enlarged lymph nodes, transmitted by insects.',
            'treatment_protocol': [
                'Supportive care and antibiotics for secondary infections',
                'Anti-inflammatory drugs',
                'Wound care for skin lesions',
                'Nutritional support'
            ],
            'emergency_measures': [
                'Vector control (insecticides)',
                'Isolation of infected animals',
                'Vaccination of healthy animals',
                'Report to veterinary authorities'
            ],
            'additional_notes': 'Recovered animals develop immunity but may have permanent skin damage.'
        },
        'Mastitis': {
            'description': 'Inflammation of the mammary gland, usually due to bacterial infection, affecting milk quality and quantity.',
            'treatment_protocol': [
                'Antibiotic therapy based on culture sensitivity',
                'Anti-inflammatory medications',
                'Frequent milking to remove infected milk',
                'Intramammary infusions',
                'Supportive care and hydration'
            ],
            'emergency_measures': [
                'Isolate affected cows',
                'Practice strict milking hygiene',
                'Discard milk from treated cows',
                'Consult veterinarian for proper treatment'
            ],
            'additional_notes': 'Proper milking procedures and herd management can prevent most mastitis cases.'
        },
        'Not Cattle': {
            'description': 'The uploaded image does not appear to contain cattle or the image quality is insufficient for analysis.',
            'treatment_protocol': [
                'Upload a clear image of cattle',
                'Ensure proper lighting and focus',
                'Capture relevant body parts clearly'
            ],
            'emergency_measures': [
                'No emergency measures needed',
                'Retry with a better quality image'
            ],
            'additional_notes': 'For accurate diagnosis, please upload clear images of cattle showing potential symptoms.'
        }
    }

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_cattle_care.db'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}