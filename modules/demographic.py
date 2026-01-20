"""
Module de décomposition démographique
Implémente la méthode de décomposition démographique selon Kitagawa (1955)
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
import warnings

class DemographicDecomposition:
    """
    Classe pour la décomposition démographique
    """
    
    def __init__(self):
        self.version = "1.0.0"
        self.author = "IFORD Groupe 4"
    
    def analyze(self, df: pd.DataFrame, group_col: str, w1_col: str, y1_col: str, 
                w2_col: str, y2_col: str, normalize: bool = True) -> Dict:
        """
        Exécute l'analyse de décomposition démographique
        
        Args:
            df: DataFrame contenant les données
            group_col: Nom de la colonne des groupes
            w1_col: Poids période 1
            y1_col: Variable d'intérêt période 1
            w2_col: Poids période 2
            y2_col: Variable d'intérêt période 2
            normalize: Si True, normalise les poids à 100%
            
        Returns:
            Dict contenant les résultats de l'analyse
        """
        
        # Validation des données
        self._validate_data(df, group_col, w1_col, y1_col, w2_col, y2_col)
        
        # Copie des données
        data = df.copy()
        
        # Normalisation des poids si demandé
        if normalize:
            total_w1 = data[w1_col].sum()
            total_w2 = data[w2_col].sum()
            
            if abs(total_w1 - 100) > 0.1:
                data[w1_col] = (data[w1_col] / total_w1) * 100
            
            if abs(total_w2 - 100) > 0.1:
                data[w2_col] = (data[w2_col] / total_w2) * 100
        
        # Calcul des moyennes pondérées pour chaque période
        Y1 = self._weighted_mean(data[w1_col], data[y1_col])
        Y2 = self._weighted_mean(data[w2_col], data[y2_col])
        
        # Changement total
        delta_Y = Y2 - Y1
        
        # Initialisation des résultats par groupe
        group_results = []
        
        for idx, row in data.iterrows():
            # Extraire les valeurs
            w1 = row[w1_col]
            y1 = row[y1_col]
            w2 = row[w2_col]
            y2 = row[y2_col]
            
            # Calcul des effets
            effect_composition = ((y2 + y1) / 2) * (w2 - w1) / 100
            effect_behavior = ((w2 + w1) / 2) * (y2 - y1) / 100
            total_effect = effect_composition + effect_behavior
            
            # Pourcentage de contribution
            contribution_percent = (total_effect / delta_Y * 100) if delta_Y != 0 else 0
            
            group_results.append({
                'group': row[group_col],
                'w1': w1,
                'y1': y1,
                'w2': w2,
                'y2': y2,
                'effect_composition': effect_composition,
                'effect_behavior': effect_behavior,
                'total_contribution': total_effect,
                'contribution_percent': contribution_percent,
                'contribution_abs': abs(total_effect)
            })
        
        # Créer le DataFrame des résultats
        results_df = pd.DataFrame(group_results)
        
        # Calcul des totaux
        total_composition = results_df['effect_composition'].sum()
        total_behavior = results_df['effect_behavior'].sum()
        total_contrib = results_df['total_contribution'].sum()
        
        # Vérification de la cohérence
        if abs(total_contrib - delta_Y) > 0.0001:
            warnings.warn(f"Différence détectée: delta_Y={delta_Y}, sum_contrib={total_contrib}")
        
        # Pourcentages des effets globaux
        composition_percent = (total_composition / delta_Y * 100) if delta_Y != 0 else 0
        behavior_percent = (total_behavior / delta_Y * 100) if delta_Y != 0 else 0
        
        # Préparer les résultats
        results = {
            'group_results': results_df,
            'aggregate_results': {
                'Y1': Y1,
                'Y2': Y2,
                'total_change': delta_Y,
                'composition_effect': total_composition,
                'behavior_effect': total_behavior,
                'composition_percent': composition_percent,
                'behavior_percent': behavior_percent,
                'verification': abs(total_contrib - delta_Y)
            },
            'metadata': {
                'num_groups': len(data),
                'variables': {
                    'group': group_col,
                    'w1': w1_col,
                    'y1': y1_col,
                    'w2': w2_col,
                    'y2': y2_col
                },
                'normalized': normalize
            }
        }
        
        return results
    
    def _validate_data(self, df: pd.DataFrame, *columns):
        """Valide l'intégrité des données"""
        for col in columns:
            if col not in df.columns:
                raise ValueError(f"Colonne '{col}' non trouvée dans les données")
            
            if df[col].isnull().any():
                raise ValueError(f"Valeurs manquantes détectées dans la colonne '{col}'")
    
    def _weighted_mean(self, weights, values):
        """Calcule la moyenne pondérée"""
        return np.average(values, weights=weights)
    
    def decompose_inequality(self, df: pd.DataFrame, group_col: str, value_col: str, 
                             weight_col: str, inequality_measure: str = 'MLD') -> Dict:
        """
        Décomposition des inégalités (extension)
        """
        # Implémentation de la décomposition des inégalités
        # (Mean Log Deviation, Theil, etc.)
        pass
    
    def nested_decomposition(self, df: pd.DataFrame, primary_group: str, 
                             secondary_group: str, **kwargs) -> Dict:
        """
        Décomposition emboîtée (groupes hiérarchiques)
        """
        pass

# Fonctions utilitaires
def kitagawa_decomposition(w1, y1, w2, y2):
    """
    Implémentation directe de la formule de Kitagawa
    """
    delta_w = w2 - w1
    delta_y = y2 - y1
    w_bar = (w1 + w2) / 2
    y_bar = (y1 + y2) / 2
    
    composition_effect = y_bar * delta_w
    behavior_effect = w_bar * delta_y
    
    return composition_effect, behavior_effect