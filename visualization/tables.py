"""
Module de création de tableaux pour la visualisation des résultats
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Union
import textwrap

class TableGenerator:
    """
    Génère des tableaux interactifs pour les résultats de décomposition
    """
    
    @staticmethod
    def create_detailed_table(results: Dict, table_type: str = 'demographic') -> go.Figure:
        """
        Crée un tableau détaillé des résultats
        
        Args:
            results: Résultats de l'analyse
            table_type: Type de tableau ('demographic', 'regression', 'mathematical')
            
        Returns:
            Figure Plotly avec le tableau
        """
        if table_type == 'demographic':
            return TableGenerator._create_demographic_table(results)
        elif table_type == 'regression':
            return TableGenerator._create_regression_table(results)
        elif table_type == 'mathematical':
            return TableGenerator._create_mathematical_table(results)
        elif table_type == 'structural':
            return TableGenerator._create_structural_table(results)
        else:
            raise ValueError(f"Type de tableau non supporté: {table_type}")
    
    @staticmethod
    def _create_demographic_table(results: Dict) -> go.Figure:
        """Tableau pour la décomposition démographique"""
        df = results['group_results'].copy()
        
        # Formater les nombres
        for col in df.columns:
            if df[col].dtype in [np.float64, np.float32]:
                df[col] = df[col].apply(lambda x: f"{x:.4f}" if not pd.isna(x) else "N/A")
        
        # Créer le tableau
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=list(df.columns),
                fill_color='navy',
                align='left',
                font=dict(color='white', size=12),
                height=30
            ),
            cells=dict(
                values=[df[col] for col in df.columns],
                fill_color=['white', 'lightgrey'] * (len(df) // 2 + 1),
                align='left',
                font=dict(size=11),
                height=25
            )
        )])
        
        fig.update_layout(
            title=dict(
                text='📋 Tableau détaillé des contributions par groupe',
                x=0.5,
                font=dict(size=14)
            ),
            height=min(400, 50 + len(df) * 25),
            margin=dict(l=10, r=10, t=60, b=10)
        )
        
        return fig
    
    @staticmethod
    def _create_regression_table(results: Dict) -> go.Figure:
        """Tableau pour la décomposition de régression"""
        # Préparer les données pour le tableau
        rows = []
        
        # Informations sur les groupes
        rows.append(['Groupes comparés', f"{results['groups']['group1']} vs {results['groups']['group2']}"])
        rows.append(['Méthode', results['method']])
        rows.append(['', ''])
        
        # Moyennes
        means = results['means']
        rows.append(['Moyennes', f"Groupe {results['groups']['group1']}", f"Groupe {results['groups']['group2']}"])
        rows.append([f"{results.get('outcome', 'Y')}", 
                    f"{means[results['groups']['group1']]['Y']:.4f}",
                    f"{means[results['groups']['group2']]['Y']:.4f}"])
        
        # Différences
        decomp = results['decomposition']
        rows.append(['', ''])
        rows.append(['Décomposition', 'Valeur', '%'])
        rows.append(['Différence totale', f"{decomp['total_difference']:.4f}", '100.0%'])
        rows.append(['Différence expliquée', f"{decomp['explained_difference']:.4f}", 
                    f"{decomp['explained_percent']:.1f}%"])
        rows.append(['Différence non expliquée', f"{decomp['unexplained_difference']:.4f}", 
                    f"{decomp['unexplained_percent']:.1f}%"])
        
        # Créer le tableau
        header = ['Description', 'Valeur 1', 'Valeur 2'] if len(rows[0]) == 3 else ['Description', 'Valeur']
        cell_values = list(zip(*rows))
        
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=header,
                fill_color='darkblue',
                align='center',
                font=dict(color='white', size=12),
                height=30
            ),
            cells=dict(
                values=cell_values,
                fill_color=['lightblue', 'white'] * (len(rows) // 2 + 1),
                align=['left', 'center', 'center'],
                font=dict(size=11),
                height=25
            )
        )])
        
        fig.update_layout(
            title=dict(
                text='📈 Résultats de la décomposition de régression',
                x=0.5,
                font=dict(size=14)
            ),
            height=min(500, 100 + len(rows) * 25),
            margin=dict(l=10, r=10, t=60, b=10)
        )
        
        return fig
    
    @staticmethod
    def _create_mathematical_table(results: Dict) -> go.Figure:
        """Tableau pour la décomposition mathématique"""
        # Récupérer les données selon la structure des résultats
        if 'values' in results:
            # Format ratio/produit
            p1 = results['values']['period1']
            p2 = results['values']['period2']
            changes = results['changes']
            effects = results['effects']
            
            rows = []
            rows.append(['Variable', 'Période 1', 'Période 2', 'Δ', 'Effet', '%'])
            
            for var in p1.keys():
                if var != 'Y':
                    delta = changes.get(f'delta_{var}', p2[var] - p1[var])
                    effect = effects.get(f'effect_{var}', 0)
                    percent = (effect / changes['delta_Y'] * 100) if changes['delta_Y'] != 0 else 0
                    
                    rows.append([var, f"{p1[var]:.4f}", f"{p2[var]:.4f}", 
                                f"{delta:.4f}", f"{effect:.4f}", f"{percent:.1f}%"])
            
            # Ajouter Y
            rows.append(['Y (résultat)', f"{p1['Y']:.4f}", f"{p2['Y']:.4f}", 
                        f"{changes['delta_Y']:.4f}", f"{effects['total_effect']:.4f}", '100.0%'])
        
        else:
            # Format générique
            rows = [['Composante', 'Valeur', 'Contribution %']]
            for key, value in results.items():
                if isinstance(value, dict) and 'percent' in value:
                    rows.append([key, f"{value.get('contribution', 0):.4f}", f"{value['percent']:.1f}%"])
        
        # Créer le tableau
        header = rows[0]
        cell_values = list(zip(*rows[1:]))
        
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=header,
                fill_color='darkgreen',
                align='center',
                font=dict(color='white', size=12),
                height=30
            ),
            cells=dict(
                values=cell_values,
                fill_color=['lightgreen', 'white'] * (len(rows) // 2 + 1),
                align='center',
                font=dict(size=11),
                height=25
            )
        )])
        
        fig.update_layout(
            title=dict(
                text='🧮 Résultats de la décomposition mathématique',
                x=0.5,
                font=dict(size=14)
            ),
            height=min(400, 100 + len(rows) * 25),
            margin=dict(l=10, r=10, t=60, b=10)
        )
        
        return fig
    
    @staticmethod
    def _create_structural_table(results: Dict) -> go.Figure:
        """Tableau pour la décomposition structurelle"""
        # Tableau hiérarchique simplifié
        rows = [['Niveau', 'Composante', 'Effet composition', 'Effet comportement', 'Total']]
        
        if 'hierarchical_contributions' in results:
            contribs = results['hierarchical_contributions']
            
            # Niveau primaire
            primary = contribs['primary']
            rows.append(['Primaire', 'Global', 
                        f"{primary['composition']:.1f}%", 
                        f"{primary['behavior']:.1f}%", 
                        f"{primary['composition'] + primary['behavior']:.1f}%"])
            
            # Niveaux secondaires
            for category, vars_dict in contribs.get('secondary', {}).items():
                for var_name, var_contrib in vars_dict.items():
                    rows.append(['Secondaire', f"{category}: {var_name}",
                                f"{var_contrib['composition']:.1f}%",
                                f"{var_contrib['behavior']:.1f}%",
                                f"{var_contrib['composition'] + var_contrib['behavior']:.1f}%"])
        
        # Créer le tableau
        header = rows[0]
        cell_values = list(zip(*rows[1:]))
        
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=header,
                fill_color='darkred',
                align='center',
                font=dict(color='white', size=12),
                height=30
            ),
            cells=dict(
                values=cell_values,
                fill_color=['lightcoral', 'white'] * (len(rows) // 2 + 1),
                align='center',
                font=dict(size=11),
                height=25
            )
        )])
        
        fig.update_layout(
            title=dict(
                text='🏗️ Résultats de la décomposition structurelle',
                x=0.5,
                font=dict(size=14)
            ),
            height=min(400, 100 + len(rows) * 25),
            margin=dict(l=10, r=10, t=60, b=10)
        )
        
        return fig
    
    @staticmethod
    def create_summary_table(all_results: Dict) -> go.Figure:
        """
        Crée un tableau récapitulatif de toutes les analyses
        
        Args:
            all_results: Dictionnaire avec tous les résultats par type
            
        Returns:
            Figure Plotly avec le tableau récapitulatif
        """
        rows = [['Type d\'analyse', 'Changement total', 'Effet composition', 'Effet comportement', 'Date']]
        
        for analysis_type, results in all_results.items():
            if analysis_type == 'demographic' and 'aggregate_results' in results:
                agg = results['aggregate_results']
                rows.append(['Démographique', 
                           f"{agg['total_change']:.4f}",
                           f"{agg['composition_percent']:.1f}%",
                           f"{agg['behavior_percent']:.1f}%",
                           'N/A'])
            
            elif analysis_type == 'regression' and 'decomposition' in results:
                decomp = results['decomposition']
                rows.append(['Régression', 
                           f"{decomp['total_difference']:.4f}",
                           f"{decomp['explained_percent']:.1f}%",
                           f"{decomp['unexplained_percent']:.1f}%",
                           'N/A'])
        
        # Créer le tableau
        header = rows[0]
        cell_values = list(zip(*rows[1:]))
        
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=header,
                fill_color='purple',
                align='center',
                font=dict(color='white', size=12),
                height=30
            ),
            cells=dict(
                values=cell_values,
                fill_color=['lavender', 'white'] * (len(rows) // 2 + 1),
                align='center',
                font=dict(size=11),
                height=25
            )
        )])
        
        fig.update_layout(
            title=dict(
                text='📊 Récapitulatif de toutes les analyses',
                x=0.5,
                font=dict(size=14)
            ),
            height=min(300, 100 + len(rows) * 25),
            margin=dict(l=10, r=10, t=60, b=10)
        )
        
        return fig

class FormattingUtils:
    """Utilitaires de formatage pour les tableaux"""
    
    @staticmethod
    def format_percentage(value, decimals=1):
        """Formate un pourcentage"""
        if pd.isna(value):
            return "N/A"
        return f"{value:.{decimals}f}%"
    
    @staticmethod
    def format_number(value, decimals=4):
        """Formate un nombre"""
        if pd.isna(value):
            return "N/A"
        return f"{value:.{decimals}f}"
    
    @staticmethod
    def wrap_text(text, width=30):
        """Enveloppe le texte pour l'affichage dans les cellules"""
        return '<br>'.join(textwrap.wrap(str(text), width=width))