"""
Module de visualisation pour l'application de décomposition
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict

def create_decomposition_charts(results: Dict):
    """
    Crée les visualisations pour la décomposition démographique
    """
    df = results['group_results']
    agg = results['aggregate_results']
    
    # 1. Graphique à barres des contributions par groupe
    fig1 = go.Figure()
    
    # Tri par contribution absolue
    df_sorted = df.sort_values('contribution_abs', ascending=False)
    
    # Barres pour l'effet de composition
    fig1.add_trace(go.Bar(
        x=df_sorted['group'],
        y=df_sorted['effect_composition'],
        name='Effet de Composition',
        marker_color='#3B82F6',
        hovertemplate='<b>%{x}</b><br>Composition: %{y:.3f}<extra></extra>'
    ))
    
    # Barres pour l'effet de comportement
    fig1.add_trace(go.Bar(
        x=df_sorted['group'],
        y=df_sorted['effect_behavior'],
        name='Effet de Comportement',
        marker_color='#10B981',
        hovertemplate='<b>%{x}</b><br>Comportement: %{y:.3f}<extra></extra>'
    ))
    
    # Configuration
    fig1.update_layout(
        title='Contributions par Groupe',
        xaxis_title='Groupes',
        yaxis_title='Contribution',
        barmode='stack',
        hovermode='x unified',
        height=500,
        showlegend=True,
        template='plotly_white'
    )
    
    # 2. Camembert des effets totaux
    fig2 = go.Figure()
    
    labels = ['Effet de Composition', 'Effet de Comportement']
    values = [agg['composition_effect'], agg['behavior_effect']]
    percents = [agg['composition_percent'], agg['behavior_percent']]
    
    # Texte des pourcentages
    text = [f'{p:.1f}%' for p in percents]
    
    fig2.add_trace(go.Pie(
        labels=labels,
        values=values,
        text=text,
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Valeur: %{value:.3f}<br>Pourcentage: %{percent}<extra></extra>',
        marker_colors=['#3B82F6', '#10B981']
    ))
    
    fig2.update_layout(
        title='Répartition des Effets Totaux',
        height=400,
        showlegend=True,
        template='plotly_white'
    )
    
    return fig1, fig2

def create_regression_charts(results: Dict):
    """Visualisations pour la décomposition de régression"""
    # À implémenter
    pass

def create_time_series_chart(df: pd.DataFrame, time_col: str, value_col: str, 
                             group_col: str = None):
    """Crée un graphique de séries temporelles"""
    if group_col:
        fig = px.line(df, x=time_col, y=value_col, color=group_col,
                     title='Évolution temporelle par groupe')
    else:
        fig = px.line(df, x=time_col, y=value_col, title='Évolution temporelle')
    
    fig.update_layout(
        xaxis_title='Période',
        yaxis_title='Valeur',
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig