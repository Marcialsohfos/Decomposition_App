"""
Script pour créer les exemples de données et configurer l'application
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json

def create_example_datasets():
    """Crée les jeux de données d'exemple"""
    
    # 1. Données démographiques Afrique
    africa_data = {
        'Country': ['Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 
                   'Cameroon', 'Congo, Dem. Rep.', 'Egypt', 'Ethiopia', 'Ghana',
                   'Kenya', 'Morocco', 'Mozambique', 'Nigeria', 'South Africa',
                   'Sudan', 'Tanzania', 'Tunisia', 'Uganda', 'Zambia'],
        'w_2015': [3.30, 2.35, 0.91, 0.19, 1.56, 1.92, 6.56, 8.15, 8.54, 2.41,
                  3.91, 2.89, 2.24, 15.34, 4.66, 3.18, 4.38, 0.96, 3.12, 1.35],
        'y_2015': [3.28, 1.53, 2.76, 9.67, 4.15, 2.55, 2.15, 4.68, 3.79, 4.25,
                  5.79, 4.94, 3.55, 0.64, 4.56, 4.64, 3.69, 5.44, 1.55, 2.89],
        'w_2020': [3.20, 2.46, 0.93, 0.19, 1.58, 1.95, 6.83, 7.91, 8.62, 2.37,
                  3.83, 2.70, 2.29, 15.33, 4.33, 3.27, 4.54, 0.90, 3.27, 1.39],
        'y_2020': [4.02, 3.93, 3.33, 10.12, 4.84, 2.94, 2.15, 5.34, 3.32, 4.47,
                  5.37, 6.04, 5.62, 0.82, 7.43, 2.55, 4.02, 6.79, 1.65, 3.37]
    }
    
    df_africa = pd.DataFrame(africa_data)
    df_africa.to_csv('data/examples/education_africa.csv', index=False)
    
    # 2. Données salariales H/F (exemple Oaxaca-Blinder)
    np.random.seed(42)
    n = 1000
    
    wage_data = pd.DataFrame({
        'gender': np.random.choice(['Homme', 'Femme'], n, p=[0.6, 0.4]),
        'education': np.random.normal(12, 3, n).clip(0, 20),
        'experience': np.random.exponential(10, n).clip(0, 40),
        'sector': np.random.choice(['Public', 'Privé'], n)
    })
    
    # Salaire avec discrimination potentielle
    wage_data['wage'] = (
        20000 + 
        3000 * (wage_data['gender'] == 'Homme') +  # Discrimination
        1500 * wage_data['education'] +
        800 * wage_data['experience'] +
        2000 * (wage_data['sector'] == 'Privé') +
        np.random.normal(0, 2000, n)
    )
    
    wage_data.to_csv('data/examples/wage_gender_gap.csv', index=False)
    
    # 3. Données démographiques pour décomposition structurelle
    demo_data = pd.DataFrame({
        'region': np.repeat(['Nord', 'Sud', 'Est', 'Ouest'], 25),
        'age_group': np.tile(['0-14', '15-29', '30-49', '50-64', '65+'], 20),
        'period': np.repeat([2010, 2015, 2020, 2025], 25),
        'population': np.random.poisson(100000, 100),
        'income': np.random.gamma(2, 500, 100),
        'education_rate': np.random.beta(5, 2, 100)
    })
    
    demo_data.to_csv('data/examples/demographic_structure.csv', index=False)
    
    print("✅ Exemples créés avec succès!")
    print("📁 Fichiers créés :")
    print("  - data/examples/education_africa.csv")
    print("  - data/examples/wage_gender_gap.csv")
    print("  - data/examples/demographic_structure.csv")

def create_config_file():
    """Crée le fichier de configuration"""
    config = {
        'app': {
            'name': 'Decomposition Analysis Tool',
            'version': '1.0.0',
            'language': 'fr',
            'debug': False
        },
        'data': {
            'default_dir': 'data',
            'max_file_size_mb': 10,
            'allowed_formats': ['.csv', '.xlsx', '.xls']
        },
        'analysis': {
            'default_method': 'kitagawa',
            'normalize_weights': True,
            'confidence_level': 0.95
        },
        'export': {
            'formats': ['excel', 'pdf', 'html', 'csv'],
            'default_format': 'excel',
            'include_charts': True
        },
        'footer_text': 'Power by Lab_Math and SCSM Group & CIE. Copyright 2026, tous droits réservés.'
    }
    
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("✅ Fichier config.json créé")

def setup_directories():
    """Crée la structure de dossiers"""
    directories = [
        'data/examples',
        'data/uploads',
        'data/templates',
        'modules',
        'visualization',
        'docs',
        'reports',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  📂 Créé: {directory}")
    
    print("✅ Structure de dossiers créée")

if __name__ == "__main__":
    print("🔧 Configuration de l'application...")
    print("=" * 50)
    
    setup_directories()
    create_example_datasets()
    create_config_file()
    
    print("=" * 50)
    print("🎉 Configuration terminée!")
    print("\nPour démarrer l'application :")
    print("  streamlit run app.py")
    print("\nAccédez à : http://localhost:8501")