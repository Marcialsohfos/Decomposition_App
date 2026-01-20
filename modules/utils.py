"""
Fonctions utilitaires pour l'application de décomposition
"""

import pandas as pd
import numpy as np
from io import BytesIO
import warnings
from typing import Union, Dict, List
from pathlib import Path

class DataLoader:
    """Classe pour le chargement et la validation des données"""
    
    @staticmethod
    def load(file_object) -> pd.DataFrame:
        """Charge un fichier Excel ou CSV"""
        file_type = file_object.name.split('.')[-1].lower()
        
        if file_type in ['xlsx', 'xls']:
            return pd.read_excel(file_object)
        elif file_type == 'csv':
            return pd.read_csv(file_object)
        else:
            raise ValueError(f"Format non supporté: {file_type}")
    
    @staticmethod
    def validate_structure(df: pd.DataFrame, required_columns: List[str]) -> bool:
        """Valide la structure des données"""
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"Colonnes manquantes: {missing}")
        return True

class Validator:
    """Classe pour la validation des données et des paramètres"""
    
    @staticmethod
    def check_percentages(series, tolerance=0.1):
        """Vérifie si une série somme à 100% (avec tolérance)"""
        total = series.sum()
        return abs(total - 100) < tolerance
    
    @staticmethod
    def check_positive(series, allow_zero=False):
        """Vérifie que les valeurs sont positives"""
        if allow_zero:
            return (series >= 0).all()
        return (series > 0).all()

class Exporter:
    """Classe pour l'export des résultats"""
    
    @staticmethod
    def to_excel(results: Dict) -> BytesIO:
        """Export vers Excel"""
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Feuille des résultats par groupe
            results['group_results'].to_excel(
                writer, 
                sheet_name='Par Groupe', 
                index=False
            )
            
            # Feuille des résultats agrégés
            agg_df = pd.DataFrame([results['aggregate_results']])
            agg_df.to_excel(
                writer, 
                sheet_name='Résumé', 
                index=False
            )
            
            # Feuille des métadonnées
            meta_df = pd.DataFrame([results['metadata']])
            meta_df.to_excel(
                writer, 
                sheet_name='Métadonnées', 
                index=False
            )
        
        output.seek(0)
        return output
    
    @staticmethod
    def to_csv(results: Dict) -> Dict[str, BytesIO]:
        """Export vers CSV multiples"""
        buffers = {}
        
        # Group results
        group_buffer = BytesIO()
        results['group_results'].to_csv(group_buffer, index=False)
        group_buffer.seek(0)
        buffers['group_results.csv'] = group_buffer
        
        # Aggregate results
        agg_buffer = BytesIO()
        pd.DataFrame([results['aggregate_results']]).to_csv(agg_buffer, index=False)
        agg_buffer.seek(0)
        buffers['aggregate_results.csv'] = agg_buffer
        
        return buffers

# Fonctions mathématiques utiles
def calculate_contributions(composition_effects, behavior_effects, total_change):
    """Calcule les contributions en pourcentage"""
    total_composition = sum(composition_effects)
    total_behavior = sum(behavior_effects)
    
    comp_percent = (total_composition / total_change * 100) if total_change != 0 else 0
    beh_percent = (total_behavior / total_change * 100) if total_change != 0 else 0
    
    return comp_percent, beh_percent

def format_number(value, decimals=4, percent=False):
    """Formate un nombre pour l'affichage"""
    if pd.isna(value):
        return "N/A"
    
    if percent:
        return f"{value:.{decimals}f}%"
    return f"{value:.{decimals}f}"