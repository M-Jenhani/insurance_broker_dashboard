"""
Setup script to initialize the insurance broker dashboard
Run this script to set up the entire project from scratch
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def create_directories():
    """Create necessary directories"""
    print_header("📁 Création des répertoires")
    
    directories = ['data', 'models', 'notebooks', 'src', 'exports']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Répertoire '{directory}' créé/vérifié")

def install_dependencies():
    """Install Python dependencies"""
    print_header("📦 Installation des dépendances")
    
    try:
        print("Installation des packages Python...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✓ Toutes les dépendances sont installées")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation: {e}")
        return False
    
    return True

def generate_data():
    """Generate synthetic data"""
    print_header("🔄 Génération des données synthétiques")
    
    try:
        print("Génération de 16,000 prospects synthétiques...")
        subprocess.check_call([sys.executable, 'src/generate_synthetic_data.py'])
        print("✓ Données synthétiques générées avec succès")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la génération: {e}")
        return False
    
    return True

def process_data():
    """Process and clean data"""
    print_header("🧹 Traitement et nettoyage des données")
    
    try:
        print("Nettoyage des données, calcul des features...")
        subprocess.check_call([sys.executable, 'src/data_processor.py'])
        print("✓ Données nettoyées et traitées")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du traitement: {e}")
        return False
    
    return True

def train_models():
    """Train ML models"""
    print_header("🤖 Entraînement des modèles ML")
    
    try:
        print("Entraînement du modèle de conversion et du prédicteur de score...")
        subprocess.check_call([sys.executable, 'src/ml_models.py'])
        print("✓ Modèles ML entraînés et sauvegardés")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'entraînement: {e}")
        return False
    
    return True

def verify_setup():
    """Verify that all files are in place"""
    print_header("✅ Vérification de l'installation")
    
    required_files = {
        'data/prospects.csv': 'Données brutes',
        'data/processed_prospects.csv': 'Données nettoyées',
        'models/segmentation_model.pkl': 'Modèle K-Means',
        'models/anomaly_detector.pkl': 'Isolation Forest',
        'models/feature_analyzer.pkl': 'Feature Analyzer',
        'app.py': 'Dashboard Streamlit'
    }
    
    all_present = True
    
    for file_path, description in required_files.items():
        if os.path.exists(file_path):
            print(f"✓ {description}: {file_path}")
        else:
            print(f"❌ MANQUANT: {description}: {file_path}")
            all_present = False
    
    return all_present

def main():
    """Main setup function"""
    print("\n" + "🏥"*20)
    print(" "*10 + "INSURANCE BROKER DASHBOARD - SETUP")
    print("🏥"*20 + "\n")
    
    print("Ce script va configurer votre dashboard de gestion des prospects.")
    print("Durée estimée: 2-3 minutes\n")
    
    input("Appuyez sur Entrée pour continuer...")
    
    # Step 1: Create directories
    create_directories()
    
    # Step 2: Install dependencies
    if not install_dependencies():
        print("\n❌ Installation échouée. Veuillez corriger les erreurs et réessayer.")
        return
    
    # Step 3: Generate data
    if not generate_data():
        print("\n❌ Génération des données échouée.")
        return
    
    # Step 4: Process data
    if not process_data():
        print("\n❌ Traitement des données échoué.")
        return
    
    # Step 5: Train models
    if not train_models():
        print("\n❌ Entraînement des modèles échoué.")
        return
    
    # Step 6: Verify
    if verify_setup():
        print_header("🎉 INSTALLATION TERMINÉE AVEC SUCCÈS!")
        
        print("\n📋 PROCHAINES ÉTAPES:")
        print("\n1. Lancer le dashboard:")
        print("   streamlit run app.py")
        print("\n2. Ouvrir votre navigateur à:")
        print("   http://localhost:8502")
        print("\n3. Explorer les 8 pages du dashboard")
        print("\n4. Logger des contacts dans 'Suivi Conversions'")
        
        print("\n" + "="*60)
        print("  Dashboard prêt à l'emploi! 🚀")
        print("="*60 + "\n")
        
        # Ask if user wants to launch dashboard
        launch = input("\nVoulez-vous lancer le dashboard maintenant? (o/n): ")
        if launch.lower() in ['o', 'oui', 'y', 'yes']:
            print("\n🚀 Lancement du dashboard...")
            subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', 'app.py'])
    else:
        print("\n⚠️ Installation partiellement réussie. Certains fichiers sont manquants.")
        print("Veuillez vérifier les erreurs ci-dessus.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Installation interrompue par l'utilisateur.")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        print("Veuillez contacter le support technique.")
