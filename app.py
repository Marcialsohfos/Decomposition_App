"""
Application principale pour l'analyse de décomposition sociale
Auteur: Équipe IFORD Groupe 4, Lab_Math and SCSM Group & CIE
Version: 1.0.0 - Copyright 2026
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys
import os
import tempfile
from datetime import datetime

# Ajouter le dossier modules au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

# Importer tous les modules de décomposition
try:
    from modules.demographic import DemographicDecomposition
    from modules.mathematical import MathematicalDecomposition
    from modules.regression import RegressionDecomposition
    from modules.structural import StructuralDecomposition
    from modules.utils import DataLoader, Validator, Exporter
    from visualization.charts import create_decomposition_charts, create_time_series_chart
    from visualization.tables import TableGenerator
    from visualization.reports import ReportGenerator, ExcelExporter
except ImportError as e:
    st.error(f"Erreur d'importation des modules: {str(e)}")
    st.info("Assurez-vous que tous les modules sont dans le dossier 'modules/'")
    # Créer des classes factices pour éviter les erreurs
    class DemographicDecomposition:
        def analyze(self, *args, **kwargs):
            return {"error": "Module non chargé"}
    class MathematicalDecomposition:
        pass
    class RegressionDecomposition:
        pass
    class StructuralDecomposition:
        pass
    class TableGenerator:
        @staticmethod
        def create_detailed_table(*args, **kwargs):
            return go.Figure()
    class ReportGenerator:
        pass

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Analyse de Décomposition Sociale",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/iford/decomposition-app',
        'Report a bug': 'https://github.com/iford/decomposition-app/issues',
        'About': "Application d'analyse de décomposition sociale - IFORD Groupe 4"
    }
)

# ============================================================================
# STYLES CSS PERSONNALISÉS
# ============================================================================
st.markdown("""
<style>
    /* En-tête principal */
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Sous-titres */
    .sub-header {
        font-size: 1.8rem;
        color: #3B82F6;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #3B82F6;
    }
    
    /* Boîtes d'information */
    .info-box {
        background-color: #DBEAFE;
        padding: 1.5rem;
        border-radius: 0.8rem;
        border-left: 5px solid #3B82F6;
        margin: 1.2rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .success-box {
        background-color: #D1FAE5;
        padding: 1.2rem;
        border-radius: 0.6rem;
        border-left: 4px solid #10B981;
        margin: 1rem 0;
    }
    
    .warning-box {
        background-color: #FEF3C7;
        padding: 1.2rem;
        border-radius: 0.6rem;
        border-left: 4px solid #F59E0B;
        margin: 1rem 0;
    }
    
    .formula-box {
        font-family: "Courier New", monospace;
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.8rem 0;
        border: 1px solid #D1D5DB;
        font-size: 0.9rem;
    }
    
    /* Boutons personnalisés */
    .stButton button {
        width: 100%;
        border-radius: 0.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Onglets */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 0.5rem 0.5rem 0 0;
        padding: 10px 20px;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #666;
        font-size: 0.8rem;
        padding: 1.5rem;
        margin-top: 2rem;
        border-top: 1px solid #E5E7EB;
        background-color: #F9FAFB;
        border-radius: 0.5rem;
    }
    
    /* Cartes de métriques */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.8rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border: 1px solid #E5E7EB;
    }
    
    /* Animation d'entrée */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Scrollbar personnalisée */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALISATION DE SESSION STATE
# ============================================================================
if 'current_data' not in st.session_state:
    st.session_state.current_data = None
if 'results' not in st.session_state:
    st.session_state.results = {}
if 'analysis_type' not in st.session_state:
    st.session_state.analysis_type = None
if 'file_uploaded' not in st.session_state:
    st.session_state.file_uploaded = False
if 'use_example' not in st.session_state:
    st.session_state.use_example = False
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================
def reset_application():
    """Réinitialise complètement l'application"""
    st.session_state.current_data = None
    st.session_state.results = {}
    st.session_state.analysis_type = None
    st.session_state.file_uploaded = False
    st.session_state.use_example = False
    st.rerun()

def load_example_data(example_name):
    """Charge un jeu de données d'exemple"""
    examples = {
        "Afrique: Dépenses éducation (2015-2020)": {
            'path': 'data/examples/education_africa.csv',
            'description': '54 pays africains, dépenses en éducation'
        },
        "USA: Opinion présidentielle (1972-2010)": {
            'path': 'data/examples/usa_president_opinion.csv',
            'description': 'Opinion sur la présidence féminine aux USA'
        },
        "Écarts salariaux H/F (Oaxaca-Blinder)": {
            'path': 'data/examples/wage_gender_gap.csv',
            'description': 'Données salariales pour décomposition Oaxaca-Blinder'
        }
    }
    
    if example_name in examples:
        try:
            # En production, on chargerait depuis le dossier data/examples
            # Pour l'exemple, créons des données factices
            if example_name == "Afrique: Dépenses éducation (2015-2020)":
                data = {
                    'Pays': ['Algérie', 'Angola', 'Bénin', 'Botswana', 'Burkina Faso'],
                    'w_2015': [3.2969, 2.3451, 0.9115, 0.1922, 1.5606],
                    'y_2015': [3.2804, 1.5274, 2.7579, 9.6725, 4.1548],
                    'w_2020': [3.1978, 2.4601, 0.9305, 0.1874, 1.5839],
                    'y_2020': [4.0239, 3.9343, 3.3283, 10.1181, 4.8370]
                }
                df = pd.DataFrame(data)
            elif example_name == "USA: Opinion présidentielle (1972-2010)":
                data = {
                    'Niveau_éducation': ['Sans diplôme', 'Secondaire', 'Université incomplète', 'Bachelor', 'Master+'],
                    'w_1972': [40.705, 46.923, 1.090, 7.949, 3.333],
                    'y_1972': [69, 75, 71, 84, 89],
                    'w_2010': [14.922, 48.973, 7.094, 18.346, 10.665],
                    'y_2010': [93, 96, 99, 98, 100]
                }
                df = pd.DataFrame(data)
            else:  # Écarts salariaux H/F
                np.random.seed(42)
                n = 200
                df = pd.DataFrame({
                    'genre': np.random.choice(['Homme', 'Femme'], n, p=[0.6, 0.4]),
                    'education': np.random.normal(12, 3, n).clip(0, 20),
                    'experience': np.random.exponential(10, n).clip(0, 40),
                    'salaire': 30000 + 5000*(df['genre']=='Homme') + 2000*df['education'] + 800*df['experience'] + np.random.normal(0, 3000, n)
                })
            
            st.session_state.current_data = df
            st.session_state.use_example = True
            return df
        except Exception as e:
            st.error(f"Erreur lors du chargement de l'exemple: {str(e)}")
            return None
    return None

def save_to_history(analysis_type, results):
    """Sauvegarde une analyse dans l'historique"""
    history_entry = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'type': analysis_type,
        'summary': {
            'total_change': results.get('aggregate_results', {}).get('total_change', 0),
            'composition_percent': results.get('aggregate_results', {}).get('composition_percent', 0),
            'behavior_percent': results.get('aggregate_results', {}).get('behavior_percent', 0)
        }
    }
    st.session_state.analysis_history.append(history_entry)
    # Garder seulement les 10 dernières analyses
    if len(st.session_state.analysis_history) > 10:
        st.session_state.analysis_history = st.session_state.analysis_history[-10:]

# ============================================================================
# HEADER PRINCIPAL
# ============================================================================
st.markdown('<h1 class="main-header fade-in">📊 APPLICATION D\'ANALYSE DE DÉCOMPOSITION SOCIALE</h1>', unsafe_allow_html=True)

st.markdown("""
<div class="info-box fade-in">
    <strong>🚀 Transformez vos nuits blanches de calculs Excel en analyses rigoureuses en quelques clics</strong><br><br>
    Cet outil implémente les méthodes de décomposition pour l'étude du changement social selon le manuel IFORD.
    Identifiez les sources du changement social (effets de composition vs comportement) de manière simple et rigoureuse.
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - NAVIGATION ET CONFIGURATION
# ============================================================================
with st.sidebar:
    # Logo et titre
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/1995/1995515.png", width=60)
    with col2:
        st.markdown("### 🔍 Navigation")
    
    st.markdown("---")
    
    # Sélection du type d'analyse
    analysis_type = st.radio(
        "**CHOISISSEZ LE TYPE D'ANALYSE :**",
        [
            "🏠 Accueil et Guide",
            "👥 Décomposition Démographique", 
            "➗ Décomposition Mathématique",
            "📈 Décomposition de Régression", 
            "🏗️ Décomposition Structurelle",
            "📚 Documentation et Exemples"
        ],
        key="nav_analysis_type"
    )
    
    st.markdown("---")
    
    # Section de chargement de données
    st.markdown("### 📁 CHARGEMENT DES DONNÉES")
    
    uploaded_file = st.file_uploader(
        "Importer vos données :",
        type=['csv', 'xlsx', 'xls'],
        help="Formats acceptés: CSV, Excel (xlsx, xls)",
        key="file_uploader"
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.session_state.current_data = df
            st.session_state.file_uploaded = True
            
            st.success(f"✅ Fichier chargé : {uploaded_file.name}")
            st.info(f"Dimensions : {df.shape[0]} lignes × {df.shape[1]} colonnes")
            
            with st.expander("👁️ Aperçu rapide"):
                st.dataframe(df.head(), use_container_width=True)
                
        except Exception as e:
            st.error(f"❌ Erreur de chargement : {str(e)}")
    
    # Boutons d'action rapide
    st.markdown("### ⚡ ACTIONS RAPIDES")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 Exemples", use_container_width=True):
            st.session_state.use_example = True
    with col2:
        if st.button("🔄 Réinitialiser", use_container_width=True):
            reset_application()
    
    # Informations sur les données actuelles
    if st.session_state.current_data is not None:
        st.markdown("---")
        st.markdown("### 📊 DONNÉES CHARGÉES")
        df_info = st.session_state.current_data
        st.metric("Lignes", df_info.shape[0])
        st.metric("Colonnes", df_info.shape[1])
        st.caption(f"Colonnes : {', '.join(df_info.columns.tolist()[:5])}{'...' if len(df_info.columns) > 5 else ''}")
    
    st.markdown("---")
    
    # Pied de page de la sidebar
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.8rem; padding: 1rem;">
    <strong>Power by Lab_Math and SCSM Group & CIE.</strong><br>
    Copyright 2026, tous droits réservés.<br>
    Version 1.0.0
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# PAGE D'ACCUEIL
# ============================================================================
if analysis_type == "🏠 Accueil et Guide":
    st.markdown('<h2 class="sub-header">🏠 Bienvenue dans l\'outil d\'analyse de décomposition</h2>', unsafe_allow_html=True)
    
    # Introduction avec colonnes
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 📋 Qu'est-ce que la décomposition ?
        
        La **décomposition** est une méthode statistique qui permet de comprendre **les sources d'un changement social** 
        en séparant les effets de **composition** et de **comportement**.
        
        ### 🎯 Pourquoi utiliser cette application ?
        
        1. **Simplifier** les analyses complexes de décomposition
        2. **Automatiser** les calculs fastidieux
        3. **Visualiser** les résultats de manière intuitive
        4. **Documenter** les analyses de manière professionnelle
        5. **Réduire les erreurs** de calcul manuel
        """)
    
    with col2:
        st.markdown("""
        ### 🚀 Démarrage rapide
        
        1. **Sélectionnez** un type d'analyse
        2. **Chargez** vos données
        3. **Configurez** les paramètres
        4. **Visualisez** les résultats
        5. **Exportez** votre rapport
        
        [📖 Guide complet →](#)
        """)
    
    st.markdown("---")
    
    # Types d'analyse disponibles
    st.markdown('<h3 class="sub-header">📊 Types d\'analyse disponibles</h3>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        with st.container(border=True):
            st.markdown("### 👥 Démographique")
            st.markdown("""
            **Effets composition/comportement**
            
            ΔY = Σ(ȳⱼΔwⱼ) + Σ(ẇⱼΔyⱼ)
            
            *Par groupes, régions, etc.*
            """)
    
    with col2:
        with st.container(border=True):
            st.markdown("### ➗ Mathématique")
            st.markdown("""
            **Formules exactes**
            
            Δ(Y/Z) = (1/Ƶ)ΔY - (Ȳ/Ƶ²)ΔZ
            
            *Ratios, produits, etc.*
            """)
    
    with col3:
        with st.container(border=True):
            st.markdown("### 📈 Régression")
            st.markdown("""
            **Oaxaca-Blinder**
            
            ΔY = Δα + β̄ΔX + X̄Δβ
            
            *Écarts entre groupes*
            """)
    
    with col4:
        with st.container(border=True):
            st.markdown("### 🏗️ Structurelle")
            st.markdown("""
            **Analyses complexes**
            
            *Multi-niveaux*
            *Emboîtée*
            *Cheminement*
            """)
    
    st.markdown("---")
    
    # Dernières analyses
    if st.session_state.analysis_history:
        st.markdown('<h3 class="sub-header">📈 Historique des analyses</h3>', unsafe_allow_html=True)
        
        history_df = pd.DataFrame(st.session_state.analysis_history)
        st.dataframe(
            history_df,
            column_config={
                "timestamp": "Date/Heure",
                "type": "Type d'analyse",
                "summary.total_change": st.column_config.NumberColumn("Δ Total", format="%.4f"),
                "summary.composition_percent": st.column_config.NumberColumn("% Composition", format="%.1f%%"),
                "summary.behavior_percent": st.column_config.NumberColumn("% Comportement", format="%.1f%%")
            },
            use_container_width=True
        )
    
    # Section de démarrage
    st.markdown("---")
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("""
    **💡 Conseil pédagogique :** Commencez par un exemple pour comprendre la logique avant d'importer vos propres données.
    
    **👉 Sélectionnez un type d'analyse dans le menu de gauche pour commencer !**
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# MODULE DÉCOMPOSITION DÉMOGRAPHIQUE
# ============================================================================
elif analysis_type == "👥 Décomposition Démographique":
    st.markdown('<h2 class="sub-header">👥 Décomposition Démographique</h2>', unsafe_allow_html=True)
    
    # Description et formule
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("""
        <div class="info-box">
        <strong>Définition :</strong> Cette méthode décompose un changement observé au niveau agrégé en deux effets :<br><br>
        1. <strong>Effet de composition</strong> : changement dû aux variations dans la répartition des groupes<br>
        2. <strong>Effet de comportement</strong> : changement dû aux variations dans les comportements moyens des groupes
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="formula-box">
        <strong>Formule de base (Kitagawa, 1955) :</strong><br><br>
        ΔY = Σ[(y₂ᵢ + y₁ᵢ)/2 × (w₂ᵢ - w₁ᵢ)] + Σ[(w₂ᵢ + w₁ᵢ)/2 × (y₂ᵢ - y₁ᵢ)]<br><br>
        <em>où :<br>
        • y = variable d'intérêt<br>
        • w = poids du groupe<br>
        • indices 1 et 2 = périodes</em>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Section de données
    st.markdown('<h3 class="sub-header">📥 Données d\'entrée</h3>', unsafe_allow_html=True)
    
    # Options de chargement
    data_option = st.radio(
        "Source des données :",
        ["📤 Importer un fichier", "📋 Utiliser un exemple", "✍️ Saisie manuelle"],
        horizontal=True,
        key="demographic_data_option"
    )
    
    if data_option == "📤 Importer un fichier":
        if st.session_state.current_data is not None:
            df = st.session_state.current_data
            
            with st.expander("🔍 Visualisation des données", expanded=True):
                st.dataframe(df, use_container_width=True)
                
                # Statistiques descriptives
                st.markdown("**Statistiques descriptives :**")
                st.dataframe(df.describe(), use_container_width=True)
        else:
            st.warning("⚠️ Aucun fichier chargé. Utilisez l'importeur dans la sidebar.")
    
    elif data_option == "📋 Utiliser un exemple":
        example_choice = st.selectbox(
            "Choisir un exemple :",
            [
                "Afrique: Dépenses éducation (2015-2020)", 
                "USA: Opinion présidentielle féminine (1972-2010)",
                "Cameroun: Mortalité infantile (1991-2011)"
            ],
            key="demographic_example"
        )
        
        if st.button("📥 Charger cet exemple", type="primary"):
            with st.spinner("Chargement de l'exemple..."):
                df = load_example_data(example_choice)
                if df is not None:
                    st.session_state.current_data = df
                    st.success(f"✅ Exemple '{example_choice}' chargé avec succès!")
                    st.dataframe(df, use_container_width=True)
    
    else:  # Saisie manuelle
        st.info("💡 Créez votre propre ensemble de données")
        
        num_groups = st.number_input("Nombre de groupes :", min_value=2, max_value=20, value=5, step=1)
        
        if st.button("📝 Créer le tableau de saisie", type="secondary"):
            st.session_state.manual_data_ready = True
        
        if st.session_state.get('manual_data_ready', False):
            manual_data = []
            
            st.markdown("**Saisie des données par groupe :**")
            
            for i in range(num_groups):
                cols = st.columns(5)
                with cols[0]:
                    group_name = st.text_input(f"Nom groupe {i+1}", value=f"Groupe {i+1}", key=f"group_{i}")
                with cols[1]:
                    w1 = st.number_input(f"w₁ {i+1}", value=20.0, min_value=0.0, key=f"w1_{i}")
                with cols[2]:
                    y1 = st.number_input(f"y₁ {i+1}", value=50.0, key=f"y1_{i}")
                with cols[3]:
                    w2 = st.number_input(f"w₂ {i+1}", value=25.0, min_value=0.0, key=f"w2_{i}")
                with cols[4]:
                    y2 = st.number_input(f"y₂ {i+1}", value=60.0, key=f"y2_{i}")
                
                manual_data.append([group_name, w1, y1, w2, y2])
            
            if st.button("✅ Valider la saisie manuelle"):
                df = pd.DataFrame(manual_data, columns=['Groupe', 'w_2015', 'y_2015', 'w_2020', 'y_2020'])
                st.session_state.current_data = df
                st.success("Données manuelles validées!")
    
    # Configuration de l'analyse
    if st.session_state.current_data is not None:
        st.markdown("---")
        st.markdown('<h3 class="sub-header">⚙️ Configuration de l\'analyse</h3>', unsafe_allow_html=True)
        
        df = st.session_state.current_data
        col_names = list(df.columns)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Variables de groupe :**")
            group_col = st.selectbox("Colonne des groupes :", col_names, index=0)
            period_names = st.text_input("Noms des périodes :", value="2015, 2020")
        
        with col2:
            st.markdown("**Variables période 1 :**")
            w1_col = st.selectbox("w₁ (poids) :", col_names, index=1 if len(col_names) > 1 else 0)
            y1_col = st.selectbox("y₁ (valeur) :", col_names, index=2 if len(col_names) > 2 else 0)
        
        with col3:
            st.markdown("**Variables période 2 :**")
            w2_col = st.selectbox("w₂ (poids) :", col_names, index=3 if len(col_names) > 3 else 0)
            y2_col = st.selectbox("y₂ (valeur) :", col_names, index=4 if len(col_names) > 4 else 0)
        
        # Options supplémentaires
        st.markdown("**Options d'analyse :**")
        col_opt1, col_opt2, col_opt3 = st.columns(3)
        
        with col_opt1:
            normalize = st.checkbox("Normaliser les poids à 100%", value=True)
        with col_opt2:
            confidence_level = st.slider("Niveau de confiance :", 0.90, 0.99, 0.95, 0.01)
        with col_opt3:
            decimal_places = st.selectbox("Décimales :", [2, 3, 4, 5], index=2)
        
        # Bouton d'analyse
        if st.button("🚀 Lancer l'analyse démographique", type="primary", use_container_width=True):
            with st.spinner("🔍 Analyse en cours..."):
                try:
                    analyzer = DemographicDecomposition()
                    
                    results = analyzer.analyze(
                        df=df,
                        group_col=group_col,
                        w1_col=w1_col,
                        y1_col=y1_col,
                        w2_col=w2_col,
                        y2_col=y2_col,
                        normalize=normalize
                    )
                    
                    st.session_state.results = results
                    st.session_state.analysis_type = "demographic"
                    save_to_history("demographic", results)
                    
                    st.success("✅ Analyse terminée avec succès!")
                    
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'analyse: {str(e)}")
                    st.info("Vérifiez la sélection de vos colonnes et le format de vos données.")
    
    # Affichage des résultats
    if st.session_state.results and st.session_state.analysis_type == "demographic":
        st.markdown("---")
        st.markdown('<h2 class="sub-header">📊 Résultats de l\'analyse démographique</h2>', unsafe_allow_html=True)
        
        results = st.session_state.results
        
        # Onglets pour différents types de résultats
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Tableau détaillé", 
            "📈 Visualisations", 
            "🎯 Résumé global", 
            "📝 Interprétation", 
            "💾 Export"
        ])
        
        with tab1:
            st.markdown("#### Contributions détaillées par groupe")
            
            # Tableau des résultats par groupe
            group_results = results['group_results'].copy()
            
            # Formater les nombres
            for col in group_results.select_dtypes(include=[np.float64]).columns:
                group_results[col] = group_results[col].apply(lambda x: f"{x:.{decimal_places}f}")
            
            st.dataframe(group_results, use_container_width=True)
            
            # Téléchargement du tableau
            csv = group_results.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger ce tableau (CSV)",
                data=csv,
                file_name="resultats_demographiques.csv",
                mime="text/csv",
                key="download_group_results"
            )
        
        with tab2:
            st.markdown("#### Visualisations graphiques")
            
            col_viz1, col_viz2 = st.columns(2)
            
            with col_viz1:
                # Diagramme en barres des contributions
                fig1 = go.Figure()
                
                df_sorted = results['group_results'].sort_values('total_contribution', ascending=False)
                
                fig1.add_trace(go.Bar(
                    x=df_sorted['group'],
                    y=df_sorted['total_contribution'],
                    name='Contribution totale',
                    marker_color='#3B82F6',
                    text=df_sorted['contribution_percent'].apply(lambda x: f"{x:.1f}%"),
                    textposition='auto'
                ))
                
                fig1.update_layout(
                    title='Contributions totales par groupe',
                    xaxis_title='Groupes',
                    yaxis_title='Contribution',
                    height=400,
                    template='plotly_white',
                    showlegend=False
                )
                
                st.plotly_chart(fig1, use_container_width=True)
            
            with col_viz2:
                # Camembert des effets globaux
                agg = results['aggregate_results']
                
                fig2 = go.Figure(data=[go.Pie(
                    labels=['Effet de Composition', 'Effet de Comportement'],
                    values=[agg['composition_effect'], agg['behavior_effect']],
                    hole=0.4,
                    marker_colors=['#10B981', '#3B82F6'],
                    textinfo='percent+label',
                    hoverinfo='value+percent'
                )])
                
                fig2.update_layout(
                    title='Répartition des effets globaux',
                    height=400,
                    showlegend=True
                )
                
                st.plotly_chart(fig2, use_container_width=True)
            
            # Graphique d'évolution
            st.markdown("#### Évolution des groupes")
            
            evolution_data = []
            for _, row in results['group_results'].iterrows():
                evolution_data.append({
                    'Groupe': row['group'],
                    'Période 1': row['y1'],
                    'Période 2': row['y2'],
                    'Changement': row['y2'] - row['y1']
                })
            
            evolution_df = pd.DataFrame(evolution_data)
            fig3 = px.bar(
                evolution_df, 
                x='Groupe', 
                y=['Période 1', 'Période 2'],
                title='Évolution de la variable y par groupe',
                barmode='group',
                color_discrete_sequence=['#EF4444', '#10B981']
            )
            
            fig3.update_layout(height=400)
            st.plotly_chart(fig3, use_container_width=True)
        
        with tab3:
            st.markdown("#### Résumé global de l'analyse")
            
            agg = results['aggregate_results']
            
            # Métriques principales
            col_met1, col_met2, col_met3 = st.columns(3)
            
            with col_met1:
                st.metric(
                    "Changement total (ΔY)", 
                    f"{agg['total_change']:.{decimal_places}f}",
                    delta=f"{agg['Y1']:.{decimal_places}f} → {agg['Y2']:.{decimal_places}f}",
                    delta_color="normal"
                )
            
            with col_met2:
                st.metric(
                    "Effet de composition", 
                    f"{agg['composition_effect']:.{decimal_places}f}",
                    delta=f"{agg['composition_percent']:.1f}%",
                    delta_color="off"
                )
            
            with col_met3:
                st.metric(
                    "Effet de comportement", 
                    f"{agg['behavior_effect']:.{decimal_places}f}",
                    delta=f"{agg['behavior_percent']:.1f}%",
                    delta_color="off"
                )
            
            # Détails supplémentaires
            st.markdown("**Détails techniques :**")
            
            tech_col1, tech_col2, tech_col3 = st.columns(3)
            
            with tech_col1:
                st.metric("Y₁ (moyenne période 1)", f"{agg['Y1']:.{decimal_places}f}")
            with tech_col2:
                st.metric("Y₂ (moyenne période 2)", f"{agg['Y2']:.{decimal_places}f}")
            with tech_col3:
                st.metric("Vérification", f"{agg['verification']:.6f}", 
                         help="Différence entre ΔY calculé et somme des contributions (doit être proche de 0)")
            
            # Groupes les plus contributeurs
            st.markdown("**Groupes les plus contributeurs :**")
            
            top_groups = results['group_results'].nlargest(3, 'contribution_abs')
            
            for idx, (_, row) in enumerate(top_groups.iterrows()):
                with st.container(border=True):
                    cols = st.columns([2, 1, 1, 1])
                    with cols[0]:
                        st.markdown(f"**{row['group']}**")
                    with cols[1]:
                        st.metric("Contribution", f"{row['total_contribution']:.{decimal_places}f}")
                    with cols[2]:
                        st.metric("% Total", f"{row['contribution_percent']:.1f}%")
                    with cols[3]:
                        comp = "➕" if row['total_contribution'] > 0 else "➖"
                        st.markdown(f"**{comp}**")
        
        with tab4:
            st.markdown("#### Interprétation des résultats")
            
            agg = results['aggregate_results']
            
            # Interprétation automatique
            interpretation = f"""
            ### 📝 Analyse de décomposition démographique
            
            **Résumé global :**
            
            • **Changement total observé** : {agg['total_change']:.{decimal_places}f} unités
            • **Effet de composition** : {agg['composition_percent']:.1f}% du changement
            • **Effet de comportement** : {agg['behavior_percent']:.1f}% du changement
            
            **Interprétation principale :**
            """
            
            if agg['composition_percent'] > 70:
                interpretation += """
                Le changement est **principalement dû à des modifications dans la structure** de la population 
                (effet de composition > 70%). Cela suggère que les transformations démographiques, sociales 
                ou économiques de la structure des groupes sont le principal moteur du changement.
                
                **Implications politiques :** Les politiques ciblant les groupes spécifiques (redistribution, 
                quotas, programmes sectoriels) pourraient être particulièrement efficaces.
                """
            elif agg['behavior_percent'] > 70:
                interpretation += """
                Le changement est **principalement dû à des modifications dans les comportements** individuels 
                (effet de comportement > 70%). Cela indique que les individus, indépendamment de leur groupe 
                d'appartenance, ont modifié leurs comportements de manière similaire.
                
                **Implications politiques :** Des politiques générales affectant l'ensemble de la population 
                (campagnes de sensibilisation, changements législatifs globaux) pourraient être appropriées.
                """
            else:
                interpretation += """
                Le changement résulte d'une **combinaison équilibrée** des modifications structurelles et comportementales. 
                Les deux types d'effets contribuent significativement à l'évolution observée.
                
                **Implications politiques :** Une approche mixte combinant politiques ciblées et interventions 
                générales pourrait être nécessaire pour maximiser l'impact.
                """
            
            # Analyse des groupes
            interpretation += "\n\n**Analyse des groupes :**\n\n"
            
            positive_groups = results['group_results'][results['group_results']['total_contribution'] > 0]
            negative_groups = results['group_results'][results['group_results']['total_contribution'] < 0]
            
            if len(positive_groups) > 0:
                top_positive = positive_groups.nlargest(1, 'total_contribution')
                interpretation += f"• **Groupe le plus contributeur positif** : {top_positive.iloc[0]['group']} " \
                                f"({top_positive.iloc[0]['contribution_percent']:.1f}% du changement)\n"
            
            if len(negative_groups) > 0:
                top_negative = negative_groups.nsmallest(1, 'total_contribution')
                interpretation += f"• **Groupe le plus freinateur** : {top_negative.iloc[0]['group']} " \
                                f"({top_negative.iloc[0]['contribution_percent']:.1f}% du changement)\n"
            
            # Recommandations
            interpretation += """
            
            **⚠️ Limitations méthodologiques :**
            1. La décomposition identifie les **sources** du changement, pas les **causes** profondes
            2. Les résultats dépendent de la qualité et de la pertinence des variables de groupe
            3. L'interprétation nécessite une connaissance du contexte spécifique
            4. Les effets d'interaction entre groupes ne sont pas capturés par cette méthode simple
            """
            
            st.markdown(interpretation)
            
            # Guide d'interprétation
            with st.expander("🎓 Guide d'interprétation détaillé"):
                st.markdown("""
                **Comment interpréter les résultats :**
                
                **Effet de composition (%) :** Pourcentage du changement total dû aux modifications dans la 
                répartition relative des groupes. Un pourcentage élevé (>70%) signifie que le changement 
                provient surtout de transformations dans la structure de la population.
                
                **Effet de comportement (%) :** Pourcentage du changement total dû aux modifications dans 
                les comportements moyens des groupes. Un pourcentage élevé (>70%) signifie que le changement 
                provient surtout de l'évolution des comportements individuels.
                
                **Contributions par groupe :** Chaque groupe contribue positivement (accentue le changement) 
                ou négativement (freine le changement). La somme des contributions est égale à 100%.
                
                **Exemple concret :** Si l'on étudie l'évolution du taux de chômage et que l'effet de 
                composition est élevé, cela signifie que le changement vient surtout de modifications dans 
                la structure de la population active (plus de jeunes, plus de diplômés, etc.).
                """)
        
        with tab5:
            st.markdown("#### Options d'export")
            
            export_format = st.radio(
                "Format d'export :",
                ["📊 Excel complet (.xlsx)", "📄 Rapport PDF", "📋 Données brutes (CSV)", 
                 "🖼️ Graphiques (PNG)", "📝 Rapport HTML"],
                key="export_format_demographic"
            )
            
            if export_format == "📊 Excel complet (.xlsx)":
                st.markdown("""
                **Contenu de l'export Excel :**
                • Feuille 1 : Résultats détaillés par groupe
                • Feuille 2 : Résumé global et métriques
                • Feuille 3 : Données source
                • Feuille 4 : Métadonnées de l'analyse
                """)
                
                if st.button("📥 Générer le fichier Excel", type="primary"):
                    with st.spinner("Génération du fichier Excel..."):
                        try:
                            # Créer un fichier Excel temporaire
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
                                with pd.ExcelWriter(tmp.name, engine='openpyxl') as writer:
                                    # Feuille des résultats
                                    results['group_results'].to_excel(writer, sheet_name='Résultats détaillés', index=False)
                                    
                                    # Feuille de synthèse
                                    summary_data = pd.DataFrame([{
                                        'Métrique': 'Changement total (ΔY)',
                                        'Valeur': agg['total_change'],
                                        'Unité': 'unités'
                                    }, {
                                        'Métrique': 'Effet de composition',
                                        'Valeur': agg['composition_effect'],
                                        'Pourcentage': f"{agg['composition_percent']:.1f}%"
                                    }, {
                                        'Métrique': 'Effet de comportement',
                                        'Valeur': agg['behavior_effect'],
                                        'Pourcentage': f"{agg['behavior_percent']:.1f}%"
                                    }])
                                    summary_data.to_excel(writer, sheet_name='Synthèse', index=False)
                                    
                                    # Feuille des données source
                                    df.to_excel(writer, sheet_name='Données source', index=False)
                                    
                                    # Feuille des métadonnées
                                    metadata = pd.DataFrame([{
                                        'Paramètre': 'Type d\'analyse',
                                        'Valeur': 'Décomposition Démographique'
                                    }, {
                                        'Paramètre': 'Date d\'analyse',
                                        'Valeur': datetime.now().strftime("%Y-%m-%d %H:%M")
                                    }, {
                                        'Paramètre': 'Colonne des groupes',
                                        'Valeur': group_col
                                    }])
                                    metadata.to_excel(writer, sheet_name='Métadonnées', index=False)
                                
                                # Lire le fichier pour le téléchargement
                                with open(tmp.name, 'rb') as f:
                                    excel_data = f.read()
                                
                                st.download_button(
                                    label="💾 Télécharger le fichier Excel",
                                    data=excel_data,
                                    file_name="analyse_decomposition_demographique.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    key="download_excel_full"
                                )
                        except Exception as e:
                            st.error(f"Erreur lors de la génération Excel : {str(e)}")
            
            elif export_format == "📄 Rapport PDF":
                st.markdown("**Génération d'un rapport PDF professionnel**")
                
                if st.button("📥 Générer le rapport PDF", type="primary"):
                    with st.spinner("Génération du rapport PDF..."):
                        try:
                            # En production, utiliser ReportGenerator
                            st.info("Fonctionnalité PDF en développement. Utilisez l'export Excel en attendant.")
                        except:
                            st.warning("Le module PDF n'est pas encore disponible.")
            
            elif export_format == "📋 Données brutes (CSV)":
                csv_all = results['group_results'].to_csv(index=False).encode('utf-8')
                
                st.download_button(
                    label="💾 Télécharger les résultats (CSV)",
                    data=csv_all,
                    file_name="resultats_complets.csv",
                    mime="text/csv",
                    key="download_csv_all"
                )
            
            # Code de reproduction
            with st.expander("🧮 Code de reproduction (Python)"):
                st.code("""
# Code Python pour reproduire cette analyse
import pandas as pd
import numpy as np

def decomposition_demographique(df, group_col, w1_col, y1_col, w2_col, y2_col):
    \"\"\"
    Décomposition démographique selon Kitagawa (1955)
    \"\"\"
    results = []
    
    for idx, row in df.iterrows():
        # Moyennes
        y_bar = (row[y1_col] + row[y2_col]) / 2
        w_bar = (row[w1_col] + row[w2_col]) / 2
        
        # Effets
        effet_composition = y_bar * (row[w2_col] - row[w1_col]) / 100
        effet_comportement = w_bar * (row[y2_col] - row[y1_col]) / 100
        contribution_totale = effet_composition + effet_comportement
        
        results.append({
            'groupe': row[group_col],
            'effet_composition': effet_composition,
            'effet_comportement': effet_comportement,
            'contribution_totale': contribution_totale
        })
    
    return pd.DataFrame(results)

# Exemple d'utilisation
df = pd.read_csv('vos_donnees.csv')
resultats = decomposition_demographique(df, 'Pays', 'w_2015', 'y_2015', 'w_2020', 'y_2020')
print(resultats)
                """, language='python')

# ============================================================================
# MODULE DÉCOMPOSITION MATHÉMATIQUE
# ============================================================================
elif analysis_type == "➗ Décomposition Mathématique":
    st.markdown('<h2 class="sub-header">➗ Décomposition Mathématique</h2>', unsafe_allow_html=True)
    
    # Description
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("""
        <div class="info-box">
        <strong>Définition :</strong> Décomposition basée sur des formules mathématiques exactes.<br><br>
        <strong>Applications typiques :</strong><br>
        • PIB par habitant<br>
        • Ratios démographiques<br>
        • Dépenses publiques par enfant<br>
        • Productivité du travail<br>
        • Dividende démographique
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="formula-box">
        <strong>Exemple : Ratio simple</strong><br><br>
        Y = A / B<br><br>
        ΔY = (1/B̄)ΔA - (Ā/B̄²)ΔB<br><br>
        <em>où :<br>
        • Ā, B̄ = moyennes des périodes<br>
        • ΔA, ΔB = changements absolus</em>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sélection de formule
    st.markdown('<h3 class="sub-header">📐 Sélection de la formule</h3>', unsafe_allow_html=True)
    
    formula_type = st.selectbox(
        "Formule mathématique :",
        [
            "Ratio simple (Y = A/B)",
            "Produit de ratios (Y = (G*k)/P)",
            "Dividende démographique (Y = π * α)",
            "Fonction Cobb-Douglas",
            "Formule personnalisée"
        ],
        key="math_formula_type"
    )
    
    # Interface de saisie selon la formule
    if formula_type == "Ratio simple (Y = A/B)":
        st.markdown("**Valeurs pour A et B :**")
        
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            st.markdown("**Période 1 :**")
            A1 = st.number_input("A₁ (ex: PIB total)", value=100.0, step=10.0, key="A1_ratio")
            B1 = st.number_input("B₁ (ex: Population)", value=10.0, step=1.0, key="B1_ratio")
        
        with col_a2:
            st.markdown("**Période 2 :**")
            A2 = st.number_input("A₂", value=120.0, step=10.0, key="A2_ratio")
            B2 = st.number_input("B₂", value=12.0, step=1.0, key="B2_ratio")
        
        if st.button("🔍 Analyser ce ratio", type="primary", use_container_width=True):
            try:
                analyzer = MathematicalDecomposition()
                data = {
                    'A': {'2015': A1, '2020': A2},
                    'B': {'2015': B1, '2020': B2}
                }
                results = analyzer.analyze('ratio', data, ('2015', '2020'))
                st.session_state.results = results
                st.session_state.analysis_type = "mathematical"
                save_to_history("mathematical", results)
                st.success("✅ Analyse du ratio terminée!")
            except Exception as e:
                st.error(f"❌ Erreur : {str(e)}")
    
    elif formula_type == "Produit de ratios (Y = (G*k)/P)":
        st.markdown("**Valeurs pour G, k et P :**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Période 1 :**")
            G1 = st.number_input("G₁ (ex: Revenu national)", value=1000.0, key="G1_product")
            k1 = st.number_input("k₁ (ex: % budget éducation)", value=0.05, format="%.3f", key="k1_product")
            P1 = st.number_input("P₁ (ex: Population enfants)", value=100.0, key="P1_product")
        
        with col2:
            st.markdown("**Période 2 :**")
            G2 = st.number_input("G₂", value=1200.0, key="G2_product")
            k2 = st.number_input("k₂", value=0.06, format="%.3f", key="k2_product")
            P2 = st.number_input("P₂", value=110.0, key="P2_product")
        
        if st.button("🔍 Analyser ce produit", type="primary", use_container_width=True):
            try:
                analyzer = MathematicalDecomposition()
                data = {
                    'G': {'2015': G1, '2020': G2},
                    'k': {'2015': k1, '2020': k2},
                    'P': {'2015': P1, '2020': P2}
                }
                results = analyzer.analyze('product', data, ('2015', '2020'))
                st.session_state.results = results
                st.session_state.analysis_type = "mathematical"
                st.success("✅ Analyse du produit terminée!")
            except Exception as e:
                st.error(f"❌ Erreur : {str(e)}")
    
    elif formula_type == "Dividende démographique (Y = π * α)":
        st.markdown("**Valeurs pour G, A et P :**")
        st.markdown("""
        **Rappel :** 
        • π = G/A (productivité des actifs)
        • α = A/P (ratio actifs/population totale)
        • Y = π × α = (G/A) × (A/P) = G/P
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Période 1 :**")
            G1 = st.number_input("G₁ (Revenu national)", value=500.0, key="G1_dividend")
            A1 = st.number_input("A₁ (Population active)", value=300.0, key="A1_dividend")
            P1 = st.number_input("P₁ (Population totale)", value=500.0, key="P1_dividend")
        
        with col2:
            st.markdown("**Période 2 :**")
            G2 = st.number_input("G₂", value=600.0, key="G2_dividend")
            A2 = st.number_input("A₂", value=350.0, key="A2_dividend")
            P2 = st.number_input("P₂", value=550.0, key="P2_dividend")
        
        if st.button("🔍 Analyser le dividende démographique", type="primary", use_container_width=True):
            try:
                analyzer = MathematicalDecomposition()
                data = {
                    'G': {'2015': G1, '2020': G2},
                    'A': {'2015': A1, '2020': A2},
                    'P': {'2015': P1, '2020': P2}
                }
                results = analyzer.analyze('demographic_dividend', data, ('2015', '2020'))
                st.session_state.results = results
                st.session_state.analysis_type = "mathematical"
                st.success("✅ Analyse du dividende démographique terminée!")
            except Exception as e:
                st.error(f"❌ Erreur : {str(e)}")
    
    # Guide des formules
    with st.sidebar.expander("📝 Guide des formules", expanded=False):
        st.markdown("""
        **Ratio simple: Y = A/B**
        - Exemple : PIB par habitant
        - A = PIB total
        - B = Population totale
        
        **Produit de ratios: Y = (G*k)/P**
        - Exemple : Dépenses éducation par enfant
        - G = Revenu national
        - k = % budget éducation
        - P = Nombre d'enfants
        
        **Dividende démographique: Y = π × α**
        - π = Productivité (G/A)
        - α = Structure par âge (A/P)
        
        **Cobb-Douglas: Y = A × K^α × L^(1-α)**
        - Fonction de production
        - Décomposition de la croissance
        """)
    
    # Affichage des résultats
    if st.session_state.results and st.session_state.analysis_type == "mathematical":
        st.markdown("---")
        st.markdown('<h3 class="sub-header">📊 Résultats mathématiques</h3>', unsafe_allow_html=True)
        
        results = st.session_state.results
        
        # Afficher les résultats selon la structure
        if 'formula' in results:
            st.markdown(f"**Formule analysée :** `{results['formula']}`")
            
            # Tableau des valeurs
            col_val1, col_val2 = st.columns(2)
            
            with col_val1:
                st.markdown("**Valeurs période 1 :**")
                p1 = results['values']['period1']
                for key, value in p1.items():
                    st.metric(key, f"{value:.4f}")
            
            with col_val2:
                st.markdown("**Valeurs période 2 :**")
                p2 = results['values']['period2']
                for key, value in p2.items():
                    st.metric(key, f"{value:.4f}")
            
            # Changements
            st.markdown("**Changements :**")
            changes = results['changes']
            for key, value in changes.items():
                if key.startswith('delta_'):
                    var_name = key.replace('delta_', '').upper()
                    st.metric(f"Δ{var_name}", f"{value:.4f}")
            
            # Effets et contributions
            if 'effects' in results:
                st.markdown("**Décomposition des effets :**")
                
                effects = results['effects']
                total_effect = effects.get('total_effect', 0)
                
                for key, value in effects.items():
                    if key != 'total_effect':
                        var_name = key.replace('effect_', '').upper()
                        percent = (value / total_effect * 100) if total_effect != 0 else 0
                        st.metric(f"Effet {var_name}", f"{value:.4f}", delta=f"{percent:.1f}%")
        
        # Graphique de décomposition
        if 'effects' in results:
            effects_data = []
            for key, value in results['effects'].items():
                if key != 'total_effect':
                    effects_data.append({
                        'Composante': key.replace('effect_', '').upper(),
                        'Valeur': abs(value),
                        'Signe': 'Positive' if value > 0 else 'Negative'
                    })
            
            if effects_data:
                effects_df = pd.DataFrame(effects_data)
                fig = px.bar(
                    effects_df,
                    x='Composante',
                    y='Valeur',
                    color='Signe',
                    title='Décomposition des effets',
                    color_discrete_map={'Positive': '#10B981', 'Negative': '#EF4444'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Interprétation
        st.markdown("""
        <div class="info-box">
        <strong>Interprétation :</strong> La décomposition mathématique montre comment chaque variable 
        contribue au changement total, en tenant compte de sa position dans la formule. Les contributions 
        sont calculées exactement à partir des dérivées partielles de la formule.
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# MODULE DÉCOMPOSITION DE RÉGRESSION
# ============================================================================
elif analysis_type == "📈 Décomposition de Régression":
    st.markdown('<h2 class="sub-header">📈 Décomposition de Régression (Oaxaca-Blinder)</h2>', unsafe_allow_html=True)
    
    # Description
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("""
        <div class="info-box">
        <strong>Définition :</strong> Méthode Oaxaca-Blinder pour décomposer les écarts entre groupes.<br><br>
        <strong>Applications typiques :</strong><br>
        • Écarts salariaux Hommes/Femmes<br>
        • Discrimination sur le marché du travail<br>
        • Différences régionales de revenus<br>
        • Inégalités éducatives
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="formula-box">
        <strong>Formule Oaxaca-Blinder :</strong><br><br>
        ΔY = Δα + β̄ΔX + X̄Δβ<br><br>
        <em>où :<br>
        • Δα = différence d'intercept<br>
        • β̄ΔX = effet des caractéristiques<br>
        • X̄Δβ = effet des rendements (discrimination)</em>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Chargement des données
    st.markdown('<h3 class="sub-header">📥 Données pour analyse Oaxaca-Blinder</h3>', unsafe_allow_html=True)
    
    if st.session_state.current_data is not None:
        df = st.session_state.current_data
        
        with st.expander("🔍 Aperçu des données", expanded=True):
            st.dataframe(df.head(10), use_container_width=True)
            
            # Statistiques par groupe potentiel
            if 'gender' in df.columns or 'sexe' in df.columns or 'genre' in df.columns:
                group_col = next((col for col in ['gender', 'sexe', 'genre'] if col in df.columns), None)
                if group_col:
                    st.markdown(f"**Distribution par {group_col} :**")
                    group_counts = df[group_col].value_counts()
                    st.bar_chart(group_counts)
    
    else:
        st.warning("⚠️ Aucune donnée chargée. Importez un fichier ou utilisez un exemple.")
        
        if st.button("📋 Charger un exemple Oaxaca-Blinder"):
            # Créer un exemple de données salariales
            np.random.seed(42)
            n = 300
            
            example_df = pd.DataFrame({
                'genre': np.random.choice(['Homme', 'Femme'], n, p=[0.6, 0.4]),
                'education': np.random.normal(14, 3, n).clip(8, 20),
                'experience': np.random.exponential(12, n).clip(0, 40),
                'secteur': np.random.choice(['Public', 'Privé', 'Mixte'], n),
                'salaire': 30000 + 5000*(np.random.choice([0, 1], n, p=[0.4, 0.6])) + 
                          2000*np.random.normal(14, 3, n).clip(8, 20) + 
                          800*np.random.exponential(12, n).clip(0, 40) +
                          np.random.normal(0, 3000, n)
            })
            
            st.session_state.current_data = example_df
            st.success("✅ Exemple Oaxaca-Blinder chargé!")
            st.dataframe(example_df.head(10), use_container_width=True)
    
    # Configuration de l'analyse
    if st.session_state.current_data is not None:
        st.markdown("---")
        st.markdown('<h3 class="sub-header">⚙️ Configuration Oaxaca-Blinder</h3>', unsafe_allow_html=True)
        
        df = st.session_state.current_data
        col_names = list(df.columns)
        
        col_config1, col_config2 = st.columns(2)
        
        with col_config1:
            st.markdown("**Variables principales :**")
            
            outcome_var = st.selectbox(
                "Variable dépendante (Y) :",
                col_names,
                help="Variable à expliquer (ex: salaire, revenu)"
            )
            
            group_var = st.selectbox(
                "Variable de groupe :",
                col_names,
                help="Variable catégorielle avec 2 groupes (ex: genre, région)"
            )
            
            # Vérifier le nombre de groupes
            if group_var:
                unique_groups = df[group_var].nunique()
                if unique_groups < 2:
                    st.error(f"❌ La variable '{group_var}' a moins de 2 groupes uniques")
                elif unique_groups > 2:
                    st.warning(f"⚠️ La variable '{group_var}' a {unique_groups} groupes. Seuls les 2 premiers seront utilisés.")
                
                groups = df[group_var].dropna().unique()[:2]
                group1 = st.selectbox("Groupe 1 :", groups, index=0)
                group2 = st.selectbox("Groupe 2 :", [g for g in groups if g != group1], index=0)
        
        with col_config2:
            st.markdown("**Variables explicatives :**")
            
            # Sélection multiple des prédicteurs
            available_predictors = [col for col in col_names if col not in [outcome_var, group_var]]
            
            predictors = st.multiselect(
                "Variables indépendantes (X) :",
                available_predictors,
                default=available_predictors[:min(3, len(available_predictors))],
                help="Variables explicatives pour la régression"
            )
            
            # Méthode de décomposition
            method = st.selectbox(
                "Méthode de décomposition :",
                ["oaxaca", "oaxaca_reverse", "cotton", "neumark"],
                format_func=lambda x: {
                    "oaxaca": "Oaxaca standard (groupe 1 comme référence)",
                    "oaxaca_reverse": "Oaxaca inverse (groupe 2 comme référence)",
                    "cotton": "Cotton (moyenne pondérée)",
                    "neumark": "Neumark (régression poolée)"
                }[x]
            )
        
        # Options avancées
        with st.expander("⚙️ Options avancées"):
            col_adv1, col_adv2 = st.columns(2)
            
            with col_adv1:
                include_constant = st.checkbox("Inclure une constante", value=True)
                robust_errors = st.checkbox("Erreurs robustes", value=False)
            
            with col_adv2:
                confidence_level = st.slider("Niveau de confiance", 0.90, 0.99, 0.95, 0.01)
                random_seed = st.number_input("Seed aléatoire", value=42, min_value=0)
        
        # Bouton d'analyse
        if st.button("🚀 Lancer l'analyse Oaxaca-Blinder", type="primary", use_container_width=True):
            if not predictors:
                st.error("❌ Sélectionnez au moins une variable explicative")
            else:
                with st.spinner("🔍 Exécution de l'analyse Oaxaca-Blinder..."):
                    try:
                        analyzer = RegressionDecomposition()
                        
                        # Filtrer les données pour les deux groupes
                        group1_data = df[df[group_var] == group1].copy()
                        group2_data = df[df[group_var] == group2].copy()
                        
                        # Vérifier les tailles d'échantillon
                        if len(group1_data) < 10 or len(group2_data) < 10:
                            st.warning("⚠️ Attention : échantillon de petite taille")
                        
                        # Exécuter l'analyse
                        results = analyzer.oaxaca_blinder(
                            df=df,
                            outcome=outcome_var,
                            predictors=predictors,
                            group_var=group_var,
                            group1=group1,
                            group2=group2,
                            method=method
                        )
                        
                        st.session_state.results = results
                        st.session_state.analysis_type = "regression"
                        save_to_history("regression", results)
                        
                        st.success("✅ Analyse Oaxaca-Blinder terminée!")
                        
                    except Exception as e:
                        st.error(f"❌ Erreur lors de l'analyse: {str(e)}")
                        st.info("Vérifiez que vos données sont numériques et qu'il n'y a pas de valeurs manquantes.")
    
    # Affichage des résultats
    if st.session_state.results and st.session_state.analysis_type == "regression":
        st.markdown("---")
        st.markdown('<h2 class="sub-header">📊 Résultats Oaxaca-Blinder</h2>', unsafe_allow_html=True)
        
        results = st.session_state.results
        
        # Résumé principal
        decomp = results['decomposition']
        
        col_res1, col_res2, col_res3 = st.columns(3)
        
        with col_res1:
            st.metric(
                "Différence totale",
                f"{decomp['total_difference']:.2f}",
                delta=f"Groupe {results['groups']['group1']} → Groupe {results['groups']['group2']}"
            )
        
        with col_res2:
            st.metric(
                "Différence expliquée",
                f"{decomp['explained_difference']:.2f}",
                delta=f"{decomp['explained_percent']:.1f}%"
            )
        
        with col_res3:
            st.metric(
                "Différence non expliquée",
                f"{decomp['unexplained_difference']:.2f}",
                delta=f"{decomp['unexplained_percent']:.1f}%",
                delta_color="inverse" if decomp['unexplained_percent'] > 50 else "normal"
            )
        
        # Interprétation
        st.markdown("---")
        st.markdown("#### 🎯 Interprétation des résultats")
        
        interpretation = f"""
        **Analyse Oaxaca-Blinder : {results['groups']['group1']} vs {results['groups']['group2']}**
        
        La différence totale de **{decomp['total_difference']:.2f} unités** entre les deux groupes se décompose comme suit :
        
        • **{decomp['explained_percent']:.1f}%** ({decomp['explained_difference']:.2f} unités) sont expliqués par les **différences de caractéristiques** 
          observables (éducation, expérience, etc.). C'est la part "légitime" de l'écart.
        
        • **{decomp['unexplained_percent']:.1f}%** ({decomp['unexplained_difference']:.2f} unités) ne sont **pas expliqués** par les caractéristiques 
          observables. Cette part résiduelle peut refléter de la **discrimination**, des facteurs non mesurés, 
          ou des différences dans les rendements des caractéristiques.
        """
        
        if decomp['unexplained_percent'] > 50:
            interpretation += """
            
            **⚠️ Attention :** Plus de 50% de la différence n'est pas expliquée par les caractéristiques observables. 
            Cela suggère une **discrimination potentielle** ou l'importance de facteurs non mesurés.
            """
        elif decomp['unexplained_percent'] < 20:
            interpretation += """
            
            **✅ Bonne nouvelle :** Moins de 20% de la différence n'est pas expliquée. L'écart entre groupes 
            s'explique principalement par des différences dans les caractéristiques observables.
            """
        
        st.markdown(interpretation)
        
        # Détails par variable
        st.markdown("---")
        st.markdown("#### 📊 Contributions détaillées par variable")
        
        if 'detailed_contributions' in results and results['detailed_contributions']:
            contributions_data = []
            for var, contrib in results['detailed_contributions'].items():
                contributions_data.append({
                    'Variable': var,
                    'Expliquée': contrib['explained'],
                    'Non expliquée': contrib['unexplained'],
                    'Totale': contrib['explained'] + contrib['unexplained']
                })
            
            contributions_df = pd.DataFrame(contributions_data)
            st.dataframe(contributions_df, use_container_width=True)
            
            # Graphique des contributions
            fig = px.bar(
                contributions_df,
                x='Variable',
                y=['Expliquée', 'Non expliquée'],
                title='Contributions par variable',
                barmode='stack',
                color_discrete_map={'Expliquée': '#10B981', 'Non expliquée': '#EF4444'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Les contributions détaillées par variable ne sont pas disponibles pour cette méthode.")
        
        # Résultats de régression
        st.markdown("---")
        st.markdown("#### 📈 Résultats des régressions par groupe")
        
        reg_results = results['regression_results']
        
        tab_reg1, tab_reg2 = st.tabs([f"Groupe {results['groups']['group1']}", f"Groupe {results['groups']['group2']}"])
        
        with tab_reg1:
            group1 = results['groups']['group1']
            if group1 in reg_results:
                coefs = reg_results[group1]['coef']
                st.markdown(f"**Coefficients pour {group1} :**")
                for var, value in coefs.items():
                    st.metric(var, f"{value:.4f}")
        
        with tab_reg2:
            group2 = results['groups']['group2']
            if group2 in reg_results:
                coefs = reg_results[group2]['coef']
                st.markdown(f"**Coefficients pour {group2} :**")
                for var, value in coefs.items():
                    st.metric(var, f"{value:.4f}")

# ============================================================================
# MODULE DÉCOMPOSITION STRUCTURELLE
# ============================================================================
elif analysis_type == "🏗️ Décomposition Structurelle":
    st.markdown('<h2 class="sub-header">🏗️ Décomposition Structurelle</h2>', unsafe_allow_html=True)
    
    # Description
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("""
        <div class="info-box">
        <strong>Définition :</strong> Analyses complexes multi-niveaux et décompositions emboîtées.<br><br>
        <strong>Applications typiques :</strong><br>
        • Dividende démographique<br>
        • Analyses régionales hiérarchiques<br>
        • Décompositions par composantes (fécondité, mortalité, migration)<br>
        • Analyses de cheminement (Path Analysis)
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="formula-box">
        <strong>Exemple : Décomposition emboîtée</strong><br><br>
        ΔY = Σ[ΔY|Région] + Σ[ΔY|Sous-groupe]<br><br>
        <em>Analyse hiérarchique à plusieurs niveaux avec interactions</em>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sélection du type d'analyse structurelle
    structural_type = st.selectbox(
        "Type d'analyse structurelle :",
        [
            "Décomposition emboîtée hiérarchique",
            "Analyse des composantes démographiques",
            "Analyse de cheminement (Path Analysis)",
            "Modèles multi-niveaux"
        ],
        key="structural_type"
    )
    
    # Interface selon le type sélectionné
    if structural_type == "Décomposition emboîtée hiérarchique":
        st.markdown("#### Configuration de l'analyse emboîtée")
        
        if st.session_state.current_data is not None:
            df = st.session_state.current_data
            col_names = list(df.columns)
            
            col_struct1, col_struct2 = st.columns(2)
            
            with col_struct1:
                outcome_var = st.selectbox("Variable d'intérêt :", col_names, key="struct_outcome")
                primary_group = st.selectbox("Groupe principal :", col_names, key="struct_primary")
                
                # Détection automatique des périodes
                period_cols = [col for col in col_names if any(x in col.lower() for x in ['year', 'annee', 'periode', 'period'])]
                if period_cols:
                    period_var = st.selectbox("Variable temporelle :", period_cols, key="struct_period")
                else:
                    period_var = st.selectbox("Variable temporelle :", col_names, key="struct_period")
            
            with col_struct2:
                # Sélection des groupes secondaires
                available_secondary = [col for col in col_names if col not in [outcome_var, primary_group, period_var]]
                secondary_groups = st.multiselect(
                    "Groupes secondaires :",
                    available_secondary,
                    default=available_secondary[:min(2, len(available_secondary))],
                    key="struct_secondary"
                )
                
                # Périodes à comparer
                if period_var in df.columns:
                    periods = sorted(df[period_var].dropna().unique())
                    if len(periods) >= 2:
                        period1 = st.selectbox("Période 1 :", periods, index=0, key="struct_period1")
                        period2 = st.selectbox("Période 2 :", [p for p in periods if p != period1], 
                                              index=min(1, len(periods)-1), key="struct_period2")
            
            if st.button("🔍 Lancer l'analyse emboîtée", type="primary", use_container_width=True):
                with st.spinner("🔍 Exécution de l'analyse structurelle..."):
                    try:
                        analyzer = StructuralDecomposition()
                        
                        results = analyzer.nested_decomposition(
                            df=df,
                            outcome=outcome_var,
                            primary_group=primary_group,
                            secondary_groups=secondary_groups,
                            periods=(period1, period2)
                        )
                        
                        st.session_state.results = results
                        st.session_state.analysis_type = "structural"
                        save_to_history("structural", results)
                        
                        st.success("✅ Analyse structurelle terminée!")
                        
                    except Exception as e:
                        st.error(f"❌ Erreur : {str(e)}")
        
        else:
            st.warning("⚠️ Chargez d'abord des données pour utiliser cette fonctionnalité.")
    
    elif structural_type == "Analyse des composantes démographiques":
        st.markdown("#### Analyse par composantes démographiques")
        
        st.info("""
        Cette méthode décompose les changements démographiques en contributions des différentes 
        composantes : fécondité, mortalité, migration, et structure par âge.
        
        **Exemple :** Évolution du taux de dépendance
        """)
        
        # Interface simplifiée pour l'exemple
        col_demo1, col_demo2 = st.columns(2)
        
        with col_demo1:
            st.markdown("**Paramètres de base :**")
            initial_pop = st.number_input("Population initiale", value=1000000, key="init_pop")
            final_pop = st.number_input("Population finale", value=1200000, key="final_pop")
            
            fertility_rate1 = st.slider("Taux de fécondité initial", 1.0, 8.0, 4.0, 0.1, key="fert1")
            fertility_rate2 = st.slider("Taux de fécondité final", 1.0, 8.0, 2.5, 0.1, key="fert2")
        
        with col_demo2:
            st.markdown("**Autres paramètres :**")
            mortality_rate1 = st.slider("Taux de mortalité initial (%)", 0.1, 20.0, 10.0, 0.1, key="mort1")
            mortality_rate2 = st.slider("Taux de mortalité final (%)", 0.1, 20.0, 8.0, 0.1, key="mort2")
            
            migration_rate1 = st.slider("Taux de migration nette initial (%)", -5.0, 5.0, 0.0, 0.1, key="mig1")
            migration_rate2 = st.slider("Taux de migration nette final (%)", -5.0, 5.0, 0.5, 0.1, key="mig2")
        
        if st.button("🔍 Simuler la décomposition démographique", type="primary", use_container_width=True):
            with st.spinner("🔍 Simulation en cours..."):
                # Simulation simple
                total_change = final_pop - initial_pop
                
                # Contributions estimées (simulation)
                fertility_effect = (fertility_rate2 - fertility_rate1) * initial_pop * 0.1
                mortality_effect = -(mortality_rate2 - mortality_rate1) * initial_pop * 0.01
                migration_effect = (migration_rate2 - migration_rate1) * initial_pop * 0.01
                age_structure_effect = total_change - (fertility_effect + mortality_effect + migration_effect)
                
                results = {
                    'type': 'demographic_components',
                    'total_change': total_change,
                    'components': {
                        'fertility': {'effect': fertility_effect, 'percent': (fertility_effect/total_change*100)},
                        'mortality': {'effect': mortality_effect, 'percent': (mortality_effect/total_change*100)},
                        'migration': {'effect': migration_effect, 'percent': (migration_effect/total_change*100)},
                        'age_structure': {'effect': age_structure_effect, 'percent': (age_structure_effect/total_change*100)}
                    }
                }
                
                st.session_state.results = results
                st.session_state.analysis_type = "structural"
                
                st.success("✅ Simulation démographique terminée!")
    
    # Affichage des résultats structurels
    if st.session_state.results and st.session_state.analysis_type == "structural":
        st.markdown("---")
        st.markdown('<h3 class="sub-header">📊 Résultats structurels</h3>', unsafe_allow_html=True)
        
        results = st.session_state.results
        
        if results.get('type') == 'demographic_components':
            # Affichage pour la simulation démographique
            components = results['components']
            
            st.markdown(f"**Changement total de population :** {results['total_change']:,.0f}")
            
            # Graphique des contributions
            comp_data = []
            for name, comp in components.items():
                comp_data.append({
                    'Composante': name.capitalize(),
                    'Effet': comp['effect'],
                    'Pourcentage': comp['percent']
                })
            
            comp_df = pd.DataFrame(comp_data)
            
            col_comp1, col_comp2 = st.columns(2)
            
            with col_comp1:
                fig = px.bar(
                    comp_df,
                    x='Composante',
                    y='Effet',
                    title='Effets des composantes démographiques',
                    color='Composante'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col_comp2:
                fig = px.pie(
                    comp_df,
                    values='Effet',
                    names='Composante',
                    title='Répartition des contributions',
                    hole=0.3
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Tableau de synthèse
            st.markdown("**Synthèse des contributions :**")
            st.dataframe(comp_df, use_container_width=True)
        
        elif 'hierarchical_contributions' in results:
            # Affichage pour l'analyse emboîtée
            st.markdown("#### Contributions hiérarchiques")
            
            contribs = results['hierarchical_contributions']
            
            # Niveau primaire
            if 'primary' in contribs:
                primary = contribs['primary']
                st.markdown(f"**Niveau primaire ({results.get('primary_group', 'Global')}) :**")
                st.metric("Effet composition", f"{primary.get('composition', 0):.1f}%")
                st.metric("Effet comportement", f"{primary.get('behavior', 0):.1f}%")
            
            # Niveaux secondaires
            if 'secondary' in contribs:
                st.markdown("#### Niveaux secondaires")
                
                for category, vars_dict in contribs['secondary'].items():
                    with st.expander(f"Catégorie : {category}"):
                        for var_name, var_contrib in vars_dict.items():
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric(f"Composition {var_name}", f"{var_contrib.get('composition', 0):.1f}%")
                            with col2:
                                st.metric(f"Comportement {var_name}", f"{var_contrib.get('behavior', 0):.1f}%")

# ============================================================================
# PAGE DOCUMENTATION ET EXEMPLES
# ============================================================================
elif analysis_type == "📚 Documentation et Exemples":
    st.markdown('<h2 class="sub-header">📚 Documentation et Exemples</h2>', unsafe_allow_html=True)
    
    # Onglets de documentation
    tab_doc1, tab_doc2, tab_doc3, tab_doc4 = st.tabs([
        "📖 Manuel d'utilisation",
        "🎓 Tutoriels",
        "🧪 Exemples pratiques",
        "🔧 Guide méthodologique"
    ])
    
    with tab_doc1:
        st.markdown("""
        ### 📖 Manuel d'utilisation complet
        
        **1. Structure de l'application**
        
        L'application est organisée en 5 sections principales :
        
        ```python
        Application d'Analyse de Décomposition
        ├── 🏠 Accueil et Guide
        ├── 👥 Décomposition Démographique
        ├── ➗ Décomposition Mathématique
        ├── 📈 Décomposition de Régression
        ├── 🏗️ Décomposition Structurelle
        └── 📚 Documentation et Exemples
        ```
        
        **2. Workflow standard**
        
        1. **Sélectionnez** un type d'analyse dans la sidebar
        2. **Chargez** vos données (fichier CSV/Excel ou exemple)
        3. **Configurez** les paramètres spécifiques à l'analyse
        4. **Lancez l'analyse** et visualisez les résultats
        5. **Exportez** vos résultats dans le format souhaité
        
        **3. Formats de données acceptés**
        
        | Format | Description | Limitations |
        |--------|-------------|-------------|
        | CSV | Fichier texte avec séparateur virgule | Jusqu'à 100 MB |
        | Excel (.xlsx) | Fichier Microsoft Excel | Jusqu'à 50 MB |
        | Excel (.xls) | Ancien format Excel | Jusqu'à 20 MB |
        
        **4. Structure des données recommandée**
        
        Pour la décomposition démographique :
        ```
        Groupe, w_2015, y_2015, w_2020, y_2020
        Algérie, 3.2969, 3.2804, 3.1978, 4.0239
        Angola, 2.3451, 1.5274, 2.4601, 3.9343
        ```
        
        **5. Exports disponibles**
        
        • **Excel** : Fichier multi-feuilles avec résultats complets
        • **PDF** : Rapport professionnel formaté
        • **CSV** : Données brutes pour traitement ultérieur
        • **PNG** : Images des graphiques
        • **HTML** : Rapport web interactif
        
        **6. Sauvegarde et reproductibilité**
        
        Chaque analyse est automatiquement sauvegardée dans l'historique. 
        Vous pouvez reproduire exactement la même analyse en utilisant le code Python généré.
        """)
    
    with tab_doc2:
        st.markdown("""
        ### 🎓 Tutoriels pas à pas
        
        **Tutoriel 1 : Analyse démographique simple**
        
        **Objectif :** Analyser l'évolution des dépenses en éducation en Afrique (2015-2020)
        
        **Étapes :**
        
        1. **Accédez à** "👥 Décomposition Démographique"
        2. **Sélectionnez** "📋 Utiliser un exemple"
        3. **Choisissez** "Afrique: Dépenses éducation (2015-2020)"
        4. **Configurez** les colonnes :
           - Groupe : "Pays"
           - w₁ : "w_2015"
           - y₁ : "y_2015"
           - w₂ : "w_2020"
           - y₂ : "y_2020"
        5. **Lancez l'analyse**
        6. **Explorez les résultats** dans les différents onglets
        
        **Tutoriel 2 : Analyse des écarts salariaux**
        
        **Objectif :** Décomposer les écarts salariaux Hommes/Femmes
        
        **Étapes :**
        
        1. **Accédez à** "📈 Décomposition de Régression"
        2. **Chargez** l'exemple "Écarts salariaux H/F"
        3. **Configurez** l'analyse Oaxaca-Blinder :
           - Variable dépendante : "salaire"
           - Variable de groupe : "genre"
           - Variables explicatives : "education", "experience"
        4. **Lancez l'analyse**
        5. **Interprétez** la part expliquée vs non expliquée
        
        **Tutoriel 3 : Analyse mathématique de ratios**
        
        **Objectif :** Analyser l'évolution du PIB par habitant
        
        **Étapes :**
        
        1. **Accédez à** "➗ Décomposition Mathématique"
        2. **Sélectionnez** "Ratio simple (Y = A/B)"
        3. **Entrez les valeurs** :
           - A₁ = 1000 (PIB période 1)
           - B₁ = 50 (Population période 1)
           - A₂ = 1200 (PIB période 2)
           - B₂ = 55 (Population période 2)
        4. **Lancez l'analyse**
        5. **Visualisez** les contributions de A et B au changement
        """)
        
        # Vidéo de démonstration (placeholder)
        st.markdown("---")
        st.markdown("### 🎥 Démonstration vidéo")
        st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")  # URL exemple
    
    with tab_doc3:
        st.markdown("""
        ### 🧪 Exemples pratiques avec interprétation
        
        **Exemple 1 : Dépenses d'éducation en Afrique**
        
        **Contexte :** Analyse de l'évolution 2015-2020 des dépenses en éducation (% du PIB) dans 54 pays africains.
        
        **Résultats typiques :**
        ```
        Changement total : +0.23 points de pourcentage
        Effet de composition : 10.3% du changement
        Effet de comportement : 89.7% du changement
        ```
        
        **Interprétation :**
        L'augmentation des dépenses éducation est principalement due à un **effet de comportement** 
        (les pays augmentent leurs budgets éducation) plutôt qu'à un **effet de composition** 
        (changements dans la répartition de la population).
        
        **Implications politiques :**
        Les politiques de sensibilisation et d'engagement budgétaire ont été efficaces.
        
        ---
        
        **Exemple 2 : Opinion présidentielle féminine USA**
        
        **Contexte :** Évolution 1972-2010 de l'opinion favorable à une femme présidente.
        
        **Résultats typiques :**
        ```
        Contribution par niveau d'éducation :
        - High school : +51.7%
        - Bachelor : +49.4%
        - Graduate : +33.7%
        - Sans diplôme : -62.2%
        ```
        
        **Interprétation :**
        Les personnes éduquées ont fortement contribué à l'augmentation de l'acceptation, 
        tandis que les moins éduquées ont freiné le changement.
        
        **Implications politiques :**
        L'éducation joue un rôle clé dans l'évolution des attitudes politiques.
        
        ---
        
        **Exemple 3 : Écarts salariaux Hommes/Femmes**
        
        **Contexte :** Analyse Oaxaca-Blinder des salaires dans une entreprise.
        
        **Résultats typiques :**
        ```
        Différence totale : 15,000 €
        Différence expliquée : 9,000 € (60%)
        Différence non expliquée : 6,000 € (40%)
        ```
        
        **Interprétation :**
        60% de l'écart s'explique par des différences de caractéristiques (éducation, expérience), 
        mais 40% restent inexpliqués, suggérant une discrimination potentielle.
        
        **Implications politiques :**
        Nécessité d'audits d'équité salariale et de politiques de transparence.
        """)
        
        # Bouton pour charger les exemples
        st.markdown("---")
        st.markdown("### 🚀 Charger ces exemples")
        
        col_ex1, col_ex2, col_ex3 = st.columns(3)
        
        with col_ex1:
            if st.button("📥 Exemple Afrique", use_container_width=True):
                load_example_data("Afrique: Dépenses éducation (2015-2020)")
                st.rerun()
        
        with col_ex2:
            if st.button("📥 Exemple USA", use_container_width=True):
                load_example_data("USA: Opinion présidentielle (1972-2010)")
                st.rerun()
        
        with col_ex3:
            if st.button("📥 Exemple Salaires", use_container_width=True):
                load_example_data("Écarts salariaux H/F (Oaxaca-Blinder)")
                st.rerun()
    
    with tab_doc4:
        st.markdown("""
        ### 🔧 Guide méthodologique
        
        **1. Fondements théoriques**
        
        **Décomposition démographique (Kitagawa, 1955) :**
        ```
        ΔY = Σ[(y₂ᵢ + y₁ᵢ)/2 × (w₂ᵢ - w₁ᵢ)] + Σ[(w₂ᵢ + w₁ᵢ)/2 × (y₂ᵢ - y₁ᵢ)]
        ```
        
        **Oaxaca-Blinder (1973) :**
        ```
        ΔY = Δα + β̄ΔX + X̄Δβ
        ```
        
        **2. Choix des variables de groupe**
        
        Critères pour une bonne variable de classification :
        - **Exhaustivité** : Couvre toute la population
        - **Mutuelle exclusivité** : Chaque individu dans un seul groupe
        - **Variabilité temporelle** : Les poids des groupes changent dans le temps
        - **Pertinence théorique** : Lien avec le phénomène étudié
        - **Taille des groupes** : Ni trop petits, ni trop grands
        
        **3. Interprétation des résultats**
        
        **Effet de composition (%) :**
        - > 70% : Changement principalement structurel
        - 30-70% : Effets mixtes
        - < 30% : Changement principalement comportemental
        
        **Effet de comportement (%) :**
        - > 70% : Changement principalement comportemental
        - 30-70% : Effets mixtes
        - < 30% : Changement principalement structurel
        
        **4. Limitations et précautions**
        
        **Limitations méthodologiques :**
        1. La décomposition identifie les **sources** (par quoi), pas les **causes** (pourquoi)
        2. Sensible au choix des variables de groupe
        3. Ne capture pas les interactions entre groupes
        4. Suppose l'indépendance des effets
        
        **Précautions d'interprétation :**
        - Toujours considérer le contexte spécifique
        - Vérifier la qualité des données
        - Compléter par d'autres méthodes si possible
        - Interpréter avec prudence les pourcentages extrêmes
        
        **5. Références bibliographiques**
        
        ```bibtex
        @article{kitagawa1955,
          title={Components of a difference between two rates},
          author={Kitagawa, Evelyn M},
          journal={Journal of the American Statistical Association},
          year={1955}
        }
        
        @article{oaxaca1973,
          title={Male-female wage differentials in urban labor markets},
          author={Oaxaca, Ronald},
          journal={International Economic Review},
          year={1973}
        }
        
        @book{iford2017,
          title={Comprendre le changement social},
          author={IFORD},
          year={2017}
        }
        ```
        
        **6. Glossaire**
        
        | Terme | Définition |
        |-------|------------|
        | ΔY | Changement total de la variable d'intérêt |
        | wᵢ | Poids du groupe i (proportion de la population) |
        | yᵢ | Valeur moyenne du groupe i |
        | Effet de composition | Part du changement due aux modifications des poids des groupes |
        | Effet de comportement | Part du changement due aux modifications des valeurs moyennes |
        | Oaxaca-Blinder | Méthode de décomposition des écarts entre groupes |
        | Dividende démographique | Bénéfice économique lié aux changements de structure par âge |
        ```
        """)

# ============================================================================
# FOOTER GLOBAL
# ============================================================================
st.markdown("---")

# Footer avec informations de copyright et crédits
footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])

with footer_col2:
    st.markdown("""
    <div class="footer fade-in">
        <div style="margin-bottom: 10px;">
            <strong style="color: #1E3A8A; font-size: 1.1rem;">Power by Lab_Math and SCSM Group & CIE.</strong><br>
            <span style="color: #6B7280;">Copyright 2026, tous droits réservés.</span>
        </div>
        
        <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #E5E7EB;">
            <span style="color: #9CA3AF; font-size: 0.9rem;">
            📧 Contact : info@labmath-scsm.com | 
            🌐 Site : www.labmath-scsm.com | 
            📱 Support : +237 XXX XXX XXX
            </span>
        </div>
        
        <div style="margin-top: 10px; color: #9CA3AF; font-size: 0.8rem;">
            Application d'Analyse de Décomposition - Version 1.0.0<br>
            Dernière mise à jour : Novembre 2026<br>
            Développé par l'Équipe IFORD Groupe 4 avec ❤️
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# SCRIPT FINAL - MESSAGE DE CONFIRMATION
# ============================================================================
if st.session_state.get('show_welcome', True):
    with st.sidebar:
        st.balloons()
        st.session_state.show_welcome = False

# Affichage des statistiques d'utilisation en bas de page
if st.session_state.analysis_history:
    with st.sidebar.expander("📈 Statistiques d'utilisation", expanded=False):
        st.metric("Analyses réalisées", len(st.session_state.analysis_history))
        
        types = [h['type'] for h in st.session_state.analysis_history]
        type_counts = pd.Series(types).value_counts()
        
        for t, count in type_counts.items():
            st.metric(t.capitalize(), count)

# ============================================================================
# FIN DU FICHIER APP.PY
# ============================================================================