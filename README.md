# 🐄 AI-Powered Cattle Disease Detection System


A comprehensive web-based AI system for early detection and diagnosis of cattle diseases using deep learning. The system employs a novel two-stage classification pipeline to identify body parts and diagnose diseases with 85-90% accuracy.



## 🎯 Features

- **Two-Stage AI Classification**: Master model identifies body part → Specialist model diagnoses disease
- **Real-time Detection**: 1-3 second analysis time
- **High Accuracy**: 85-90% end-to-end accuracy
- **Comprehensive Medical Database**: Immediate actions, medicines, home remedies, timelines
- **User Authentication**: Secure login and role-based access
- **PDF Report Generation**: Downloadable medical reports
- **Responsive Design**: Works on desktop, tablet, and mobile
- **4 Disease Detection**: Lumpy Skin Disease, FMD, Mastitis, Tongue Disease
- **Multi-body Part Support**: Body, Foot, Udder, Tongue

## 📋 Table of Contents

- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Model Information](#model-information)
- [Dataset Structure](#dataset-structure)
- [API Documentation](#api-documentation)
- [Training Guide](#training-guide)
- [Contributing](#contributing)
- [License](#license)
- [Citation](#citation)

## 🏗️ Architecture

### System Architecture
```
┌─────────────────────┐
│   User Uploads      │
│      Image          │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  STAGE 1: MASTER    │
│  Body Part Detector │ → foot, body, udder, tongue, non_cattle
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  STAGE 2: SPECIALIST│
│  Disease Classifier │ → Specific disease diagnosis
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   Medical Info +    │
│   PDF Report        │
└─────────────────────┘
```

### Technology Stack

**Backend:**
- Flask 3.0.3 (Python web framework)
- TensorFlow 2.15.0 (Deep learning)
- Keras (Neural network API)
- ReportLab (PDF generation)

**Frontend:**
- HTML5, CSS3, JavaScript
- Bootstrap 5 (Responsive design)
- Font Awesome (Icons)

**AI/ML:**
- MobileNetV2 (Pre-trained CNN)
- Transfer Learning
- Data Augmentation

**Database:**
- In-memory (Development)
- PostgreSQL/MySQL compatible (Production)

## 📥 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/cattle-disease-detection.git
cd cattle-disease-detection
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Download Pre-trained Models

**Option 1: From Release**
Download the models from the [Releases](https://github.com/yourusername/cattle-disease-detection/releases) page and extract to `models/` folder.

**Option 2: Train Your Own**
Follow the [Training Guide](#training-guide) to train models from scratch.

### Step 5: Verify File Structure

```
cattle-disease-detection/
├── app.py
├── requirements.txt
├── models/
│   ├── master_cattle_classifier.keras
│   ├── master_class_indices.json
│   ├── cattle_3class_classifier.keras
│   ├── footrot_mobilenet_final_model.keras
│   ├── footrot_class_indices.json
│   ├── cattle_udder_mobilenet_model.h5
│   ├── udder_class_indices.json
│   ├── tongue_classification_mobilenetv2.h5
│   └── tongue_model_config.json
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── detect.html
│   ├── about.html
│   ├── contact.html
│   └── admin.html
└── static/
    ├── css/
    └── js/
```

### Step 6: Run Application

```bash
python app.py
```

Open browser and navigate to: `http://localhost:5000`

**Default Login:**
- Email: `admin@cattle.com`
- Password: `admin123`

## 🚀 Usage

### Basic Usage

1. **Login**: Use default credentials or register new account
2. **Navigate to "Detect Disease"**
3. **Upload Image**: Drag-drop or click to select cattle image
4. **Analyze**: Click "Analyze Image" button
5. **View Results**: See body part detection, disease diagnosis, and medical recommendations
6. **Download Report**: Get PDF report for veterinarian

### Supported Image Formats

- JPEG/JPG
- PNG
- Maximum size: 16MB
- Recommended: Clear, well-lit images

### Best Practices

✅ **Good Images:**
- Clear focus on affected area
- Good lighting (natural or bright)
- Close-up of disease symptoms
- Minimal background clutter

❌ **Avoid:**
- Blurry or out-of-focus images
- Poor lighting or shadows
- Multiple animals in frame
- Obstructed view of symptoms

## 🧠 Model Information

### Master Body Part Classifier

**Architecture:** MobileNetV2 + Custom Dense Layers
**Input:** 224×224×3 RGB images
**Output:** 5 classes (foot, general_body, non_cattle, tongue, udder)
**Accuracy:** 92-95%
**Parameters:** ~3.5M

### Specialist Models

| Model | Body Part | Diseases Detected | Accuracy |
|-------|-----------|-------------------|----------|
| Body Disease Classifier | General Body | Lumpy Skin Disease, Healthy, Non-cattle | 88-91% |
| Footrot Classifier | Foot | FMD (Foot & Mouth Disease), Healthy | 91-94% |
| Udder Health Classifier | Udder | Mastitis, Normal, Non-cattle | 89-92% |
| Tongue Disease Classifier | Tongue | Diseased Tongue, Normal | 90-93% |

### Model Architecture Details

```python
Base Model: MobileNetV2 (ImageNet pre-trained)
├── Input: (224, 224, 3)
├── MobileNetV2 Base (frozen/fine-tuned)
├── GlobalAveragePooling2D
├── BatchNormalization
├── Dropout(0.5)
├── Dense(256, activation='relu')
├── BatchNormalization
├── Dropout(0.3)
├── Dense(128, activation='relu')
├── Dropout(0.2)
└── Dense(num_classes, activation='softmax')
```

### Confidence Calculation

```python
# Combined confidence from both stages
combined_confidence = (body_part_confidence × 0.3) + (disease_confidence × 0.7)

# Example:
# Body Part: 89.7% (weight: 0.3) = 26.91%
# Disease:   94.3% (weight: 0.7) = 66.01%
# Combined:  92.92%
```

## 📊 Dataset Structure

### Training Dataset

Total images: **1,722**

```
dataset/
├── foot/           (398 images)
│   ├── fmd/        (199 images - diseased)
│   └── healthy/    (199 images)
├── general_body/   (246 images)
│   ├── lumpy/      (123 images - diseased)
│   └── healthy/    (123 images)
├── udder/          (300 images)
│   ├── mastitis/   (150 images - diseased)
│   └── normal/     (150 images)
├── tongue/         (528 images)
│   ├── diseased/   (264 images)
│   └── normal/     (264 images)
└── non_cattle/     (250 images)
```

### Data Split

- **Training:** 80% (1,378 images)
- **Validation:** 20% (344 images)

### Data Augmentation

```python
rotation_range=20          # ±20 degrees
width_shift_range=0.2      # 20% horizontal shift
height_shift_range=0.2     # 20% vertical shift
horizontal_flip=True       # Mirror images
zoom_range=0.2            # 20% zoom in/out
brightness_range=[0.8, 1.2]  # Brightness variation
```

## 🔌 API Documentation

### POST /predict

**Description:** Analyze uploaded cattle image

**Request:**
```
Content-Type: multipart/form-data

Body:
  file: <image_file>
```

**Response:**
```json
{
  "success": true,
  "body_part": "general_body",
  "body_part_confidence": 89.7,
  "predicted_class": "Lumpy Skin Disease",
  "disease_confidence": 94.3,
  "confidence": 92.92,
  "status": "DISEASE",
  "medical_info": {
    "name": "Lumpy Skin Disease",
    "severity": "HIGH",
    "immediate_actions": [...],
    "first_aid": [...],
    "emergency_signs": [...],
    "medicines": [...],
    "home_remedies": [...],
    "timeline": "...",
    "prognosis": "..."
  },
  "specialist_used": "Cattle Disease Classifier",
  "timestamp": "2025-10-30T07:15:32"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message here"
}
```

### POST /download_report

**Description:** Generate and download PDF medical report

**Request:**
```json
{
  "body_part": "general_body",
  "predicted_class": "Lumpy Skin Disease",
  "confidence": 92.92,
  "medical_info": {...}
}
```

**Response:** PDF file download

## 📚 Training Guide

### Train Master Model

**Step 1: Prepare Dataset**
```bash
# Organize images as shown in Dataset Structure
master_model_training/
├── dataset/
│   ├── foot/
│   ├── general_body/
│   ├── non_cattle/
│   ├── tongue/
│   └── udder/
```

**Step 2: Upload to Google Colab**
```python
# Create ZIP file
import zipfile
shutil.make_archive('dataset', 'zip', 'master_model_training')
```

**Step 3: Run Training Code**
```python
# See training_notebooks/train_master_model.ipynb
# Training time: ~25-40 minutes on Colab GPU
```

**Step 4: Download Model**
```python
# Models saved as:
# - master_cattle_classifier.keras
# - master_class_indices.json
```

### Train Specialist Models

Follow similar process for each specialist:
1. Prepare body-part-specific dataset
2. Use transfer learning with MobileNetV2
3. Two-phase training (freeze → fine-tune)
4. Validate on test set
5. Save model and config

**Training Notebooks:**
- `training_notebooks/train_body_model.ipynb`
- `training_notebooks/train_foot_model.ipynb`
- `training_notebooks/train_udder_model.ipynb`
- `training_notebooks/train_tongue_model.ipynb`

## 🧪 Testing

### Unit Tests

```bash
# Install pytest
pip install pytest

# Run tests
pytest tests/
```

### Test Coverage

```bash
pytest --cov=app tests/
```

### Manual Testing Checklist

- [ ] Image upload works
- [ ] All body parts detected correctly
- [ ] Disease classification accurate
- [ ] Medical information displays
- [ ] PDF download works
- [ ] Authentication functional
- [ ] Responsive on mobile

## 🚀 Deployment

### Local Development

```bash
python app.py
# Runs on http://localhost:5000
```

### Production Deployment

**Using Gunicorn:**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Using Docker:**
```bash
docker build -t cattle-detection .
docker run -p 5000:5000 cattle-detection
```

### Environment Variables

Create `.env` file:
```
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
DATABASE_URL=postgresql://user:password@localhost/dbname
MAX_CONTENT_LENGTH=16777216
```

### Production Checklist

- [ ] Change SECRET_KEY
- [ ] Set debug=False
- [ ] Use production database
- [ ] Enable HTTPS
- [ ] Set up logging
- [ ] Configure CORS
- [ ] Add rate limiting
- [ ] Set up monitoring

## 📈 Performance

### Metrics

| Metric | Value |
|--------|-------|
| End-to-End Accuracy | 85-90% |
| Master Model Accuracy | 92-95% |
| Specialist Avg Accuracy | 88-94% |
| Average Inference Time | 1-3 seconds |
| Model Size (Total) | ~60 MB |
| Supported Concurrent Users | 100+ |

### Optimization Tips

1. **Use GPU**: Enable GPU acceleration for faster inference
2. **Model Quantization**: Reduce model size for mobile deployment
3. **Caching**: Cache model predictions for identical images
4. **Batch Processing**: Process multiple images simultaneously
5. **CDN**: Serve static assets via CDN

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions
- Write unit tests for new features

## 🐛 Known Issues

- Large images (>16MB) need to be compressed
- Safari browser may have CORS issues
- PDF generation slow for complex reports

See [Issues](https://github.com/yourusername/cattle-disease-detection/issues) for full list.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Dataset Contributors**: Farmers and veterinarians who provided images
- **TensorFlow Team**: For the excellent deep learning framework
- **MobileNetV2**: Google Research for the pre-trained model
- **Bootstrap Team**: For the responsive UI framework

## 📧 Contact

**Developer:** Your Name  
**Email:** your.email@example.com  
**Project Link:** [https://github.com/yourusername/cattle-disease-detection](https://github.com/yourusername/cattle-disease-detection)

## 📖 Citation

If you use this project in your research, please cite:

```bibtex
@software{cattle_disease_detection_2025,
  author = {Your Name},
  title = {AI-Powered Cattle Disease Detection System},
  year = {2025},
  url = {https://github.com/yourusername/cattle-disease-detection}
}
```

## 🔮 Roadmap

### Version 2.0 (Q2 2025)
- [ ] Mobile app (iOS/Android)
- [ ] 10+ disease detection
- [ ] Multi-language support
- [ ] Offline mode

### Version 3.0 (Q4 2025)
- [ ] Real-time video analysis
- [ ] IoT camera integration
- [ ] Telemedicine integration
- [ ] Blockchain medical records

## 📊 Statistics


---

**⚠️ Medical Disclaimer:** This system is a diagnostic aid tool and should NOT replace professional veterinary consultation. Always consult a licensed veterinarian for accurate diagnosis and treatment.

**Made with ❤️ for healthier cattle and empowered farmers**


# 🚀 Quick Start Guide

Get the Cattle Disease Detection System running in 5 minutes!

## ⚡ Prerequisites

- Python 3.8+ installed
- 500MB free disk space
- Internet connection (for first-time setup)

## 📥 Installation (3 Steps)

### Step 1: Clone & Navigate
```bash
git clone https://github.com/yourusername/cattle-disease-detection.git
cd cattle-disease-detection
```

### Step 2: Install Dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 3: Download Models
Download pre-trained models from [Releases](https://github.com/yourusername/cattle-disease-detection/releases/tag/v1.0.0) and extract to `models/` folder.

**Required files in models/ folder:**
```
models/
├── master_cattle_classifier.keras
├── master_class_indices.json
├── cattle_3class_classifier.keras
├── footrot_mobilenet_final_model.keras
├── footrot_class_indices.json
├── cattle_udder_mobilenet_model.h5
├── udder_class_indices.json
├── tongue_classification_mobilenetv2.h5
└── tongue_model_config.json
```

## 🎯 Run Application

```bash
python app.py
```

**Output should show:**
```
============================================================
🐄 CATTLE DISEASE DETECTION SYSTEM v3.0
============================================================
✅ Master Model loaded! Classes: ['foot', 'general_body', 'non_cattle', 'tongue', 'udder']
✅ Cattle Disease Classifier loaded!
✅ Footrot (FMD) Classifier loaded!
✅ Udder Health Classifier loaded!
✅ Tongue Disease Classifier loaded!

✅ Loaded 4/4 specialists!

✅ System Ready!
📍 http://localhost:5000
```

Open browser: **http://localhost:5000**

## 🔐 Login

**Default credentials:**
- Email: `admin@cattle.com`
- Password: `admin123`

## 🎮 Quick Test

1. Login with default credentials
2. Navigate to "Detect Disease"
3. Upload a sample image from `sample_images/` folder
4. Click "Analyze Image"
5. View results with medical information
6. Download PDF report

## ✅ Success Indicators

You'll know it's working when:
- ✅ Terminal shows all 4 models loaded
- ✅ No errors in terminal
- ✅ Can login to web interface
- ✅ Can upload and analyze images
- ✅ See medical recommendations
- ✅ Can download PDF reports

## ❌ Troubleshooting

### Issue: "Module not found"
```bash
pip install -r requirements.txt
```

### Issue: "Model not found"
Download models from Releases page and place in `models/` folder

### Issue: "Port 5000 already in use"
```bash
# Use different port
python app.py --port 5001
```
Or kill existing process using port 5000

### Issue: "TensorFlow errors"
```bash
pip uninstall tensorflow
pip install tensorflow==2.15.0
```

### Issue: "Cannot upload image"
- Clear browser cache (Ctrl+Shift+R)
- Try different image format (JPG/PNG)
- Ensure image is < 16MB

## 📚 Next Steps

- Read full [README.md](README.md) for detailed documentation
- Check [API Documentation](docs/api_documentation.md)
- Review [Training Guide](docs/training_guide.md) to train your own models
- See [User Guide](docs/user_guide.md) for detailed usage instructions

## 💡 Tips

- Use clear, well-lit images for best results
- Ensure cattle is the main subject in image
- Try different angles if confidence is low
- Always consult veterinarian for confirmation

## 🐛 Still Having Issues?

1. Check [Issues](https://github.com/yourusername/cattle-disease-detection/issues)
2. Create new issue with:
   - Error message
   - Steps to reproduce
   - Your OS and Python version
   - Screenshot if applicable

## 📞 Support

Email: your.email@example.com  
GitHub: [@yourusername](https://github.com/yourusername)

---

**Happy detecting! 🐄🎉**
