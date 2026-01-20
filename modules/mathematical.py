"""
Module de décomposition mathématique
Implémente les décompositions basées sur des formules mathématiques exactes
"""

import pandas as pd
import numpy as np
import sympy as sp
from typing import Dict, List, Tuple, Union, Optional
from dataclasses import dataclass
import re

@dataclass
class Formula:
    """Classe pour représenter une formule mathématique"""
    name: str
    expression: str
    variables: List[str]
    decomposition_rule: str
    
class MathematicalDecomposition:
    """
    Classe principale pour la décomposition mathématique
    """
    
    # Bibliothèque de formules prédéfinies
    FORMULAS = {
        'ratio': Formula(
            name="Ratio simple",
            expression="Y = A / B",
            variables=['A', 'B'],
            decomposition_rule="ΔY = (1/B̄)ΔA - (Ā/B̄²)ΔB"
        ),
        'product': Formula(
            name="Produit de ratios",
            expression="Y = (G * k) / P",
            variables=['G', 'k', 'P'],
            decomposition_rule="ΔY = (k̄/P̄)ΔG + (Ḡ/P̄)Δk - (Ḡ*k̄/P̄²)ΔP"
        ),
        'product_simple': Formula(
            name="Produit simple",
            expression="Y = A * B",
            variables=['A', 'B'],
            decomposition_rule="ΔY = B̄ΔA + ĀΔB"
        ),
        'demographic_dividend': Formula(
            name="Dividende démographique",
            expression="Y = (G/A) * (A/P)",
            variables=['G', 'A', 'P'],
            decomposition_rule="ΔY = π̄Δα + ᾱΔπ"
        ),
        'cobb_douglas': Formula(
            name="Fonction Cobb-Douglas",
            expression="Y = A * K^α * L^(1-α)",
            variables=['A', 'K', 'L', 'α'],
            decomposition_rule="ΔlnY = ΔlnA + αΔlnK + (1-α)ΔlnL"
        )
    }
    
    def __init__(self):
        self.formulas = self.FORMULAS
        self.custom_formulas = {}
    
    def analyze(self, formula_type: str, data: Dict, periods: Tuple[str, str]) -> Dict:
        """
        Exécute une décomposition mathématique
        
        Args:
            formula_type: Type de formule ('ratio', 'product', etc.)
            data: Dictionnaire avec les données par variable
            periods: Tuple avec les noms des périodes ('2015', '2020')
            
        Returns:
            Résultats de la décomposition
        """
        if formula_type not in self.formulas and formula_type not in self.custom_formulas:
            raise ValueError(f"Formule '{formula_type}' non reconnue")
        
        formula = self.formulas.get(formula_type) or self.custom_formulas[formula_type]
        
        # Validation des données
        self._validate_data(data, formula.variables, periods)
        
        # Extraction des valeurs
        period1, period2 = periods
        values_p1 = {var: data[var][period1] for var in formula.variables}
        values_p2 = {var: data[var][period2] for var in formula.variables}
        
        # Calcul selon le type de formule
        if formula_type == 'ratio':
            return self._decompose_ratio(values_p1, values_p2)
        elif formula_type == 'product':
            return self._decompose_product_ratio(values_p1, values_p2)
        elif formula_type == 'product_simple':
            return self._decompose_product(values_p1, values_p2)
        elif formula_type == 'demographic_dividend':
            return self._decompose_demographic_dividend(values_p1, values_p2)
        elif formula_type == 'cobb_douglas':
            return self._decompose_cobb_douglas(values_p1, values_p2)
        else:
            # Décomposition générique
            return self._decompose_generic(formula, values_p1, values_p2)
    
    def _decompose_ratio(self, p1: Dict, p2: Dict) -> Dict:
        """Décomposition d'un ratio Y = A/B"""
        A1, B1 = p1['A'], p1['B']
        A2, B2 = p2['A'], p2['B']
        
        # Valeurs initiales et finales
        Y1 = A1 / B1 if B1 != 0 else np.nan
        Y2 = A2 / B2 if B2 != 0 else np.nan
        delta_Y = Y2 - Y1
        
        # Moyennes
        A_bar = (A1 + A2) / 2
        B_bar = (B1 + B2) / 2
        Y_bar = (Y1 + Y2) / 2
        
        # Effets
        effect_A = (1 / B_bar) * (A2 - A1)
        effect_B = -(A_bar / (B_bar ** 2)) * (B2 - B1)
        
        # Contributions
        total_effect = effect_A + effect_B
        contribution_A = (effect_A / delta_Y * 100) if delta_Y != 0 else 0
        contribution_B = (effect_B / delta_Y * 100) if delta_Y != 0 else 0
        
        return {
            'formula': 'Y = A / B',
            'values': {
                'period1': {'A': A1, 'B': B1, 'Y': Y1},
                'period2': {'A': A2, 'B': B2, 'Y': Y2}
            },
            'changes': {
                'delta_A': A2 - A1,
                'delta_B': B2 - B1,
                'delta_Y': delta_Y
            },
            'effects': {
                'effect_A': effect_A,
                'effect_B': effect_B,
                'total_effect': total_effect
            },
            'contributions': {
                'A': contribution_A,
                'B': contribution_B
            },
            'averages': {
                'A_bar': A_bar,
                'B_bar': B_bar,
                'Y_bar': Y_bar
            }
        }
    
    def _decompose_product_ratio(self, p1: Dict, p2: Dict) -> Dict:
        """Décomposition Y = (G * k) / P"""
        G1, k1, P1 = p1['G'], p1['k'], p1['P']
        G2, k2, P2 = p2['G'], p2['k'], p2['P']
        
        # Valeurs initiales et finales
        Y1 = (G1 * k1) / P1 if P1 != 0 else np.nan
        Y2 = (G2 * k2) / P2 if P2 != 0 else np.nan
        delta_Y = Y2 - Y1
        
        # Moyennes
        G_bar = (G1 + G2) / 2
        k_bar = (k1 + k2) / 2
        P_bar = (P1 + P2) / 2
        Y_bar = (Y1 + Y2) / 2
        
        # Effets
        effect_G = (k_bar / P_bar) * (G2 - G1)
        effect_k = (G_bar / P_bar) * (k2 - k1)
        effect_P = -(G_bar * k_bar / (P_bar ** 2)) * (P2 - P1)
        
        # Contributions
        total_effect = effect_G + effect_k + effect_P
        
        return {
            'formula': 'Y = (G * k) / P',
            'values': {
                'period1': {'G': G1, 'k': k1, 'P': P1, 'Y': Y1},
                'period2': {'G': G2, 'k': k2, 'P': P2, 'Y': Y2}
            },
            'changes': {
                'delta_G': G2 - G1,
                'delta_k': k2 - k1,
                'delta_P': P2 - P1,
                'delta_Y': delta_Y
            },
            'effects': {
                'effect_G': effect_G,
                'effect_k': effect_k,
                'effect_P': effect_P,
                'total_effect': total_effect
            },
            'averages': {
                'G_bar': G_bar,
                'k_bar': k_bar,
                'P_bar': P_bar,
                'Y_bar': Y_bar
            }
        }
    
    def _decompose_demographic_dividend(self, p1: Dict, p2: Dict) -> Dict:
        """Décomposition du dividende démographique Y = π * α"""
        # π = G/A (productivité), α = A/P (structure par âge)
        G1, A1, P1 = p1['G'], p1['A'], p1['P']
        G2, A2, P2 = p2['G'], p2['A'], p2['P']
        
        # Calcul des composantes
        π1 = G1 / A1 if A1 != 0 else np.nan
        π2 = G2 / A2 if A2 != 0 else np.nan
        α1 = A1 / P1 if P1 != 0 else np.nan
        α2 = A2 / P2 if P2 != 0 else np.nan
        
        # Y = π * α
        Y1 = π1 * α1
        Y2 = π2 * α2
        delta_Y = Y2 - Y1
        
        # Moyennes
        π_bar = (π1 + π2) / 2
        α_bar = (α1 + α2) / 2
        
        # Effets
        effect_π = α_bar * (π2 - π1)
        effect_α = π_bar * (α2 - α1)
        
        # Contributions
        total_effect = effect_π + effect_α
        
        return {
            'formula': 'Y = (G/A) * (A/P) = π * α',
            'components': {
                'period1': {'π': π1, 'α': α1, 'Y': Y1},
                'period2': {'π': π2, 'α': α2, 'Y': Y2}
            },
            'raw_values': {
                'period1': {'G': G1, 'A': A1, 'P': P1},
                'period2': {'G': G2, 'A': A2, 'P': P2}
            },
            'effects': {
                'productivity_effect': effect_π,
                'structure_effect': effect_α,
                'total_effect': total_effect
            },
            'interpretation': {
                'productivity': "Effet de la productivité (π = G/A)",
                'structure': "Effet de la structure par âge (α = A/P)"
            }
        }
    
    def _decompose_cobb_douglas(self, p1: Dict, p2: Dict) -> Dict:
        """Décomposition de la fonction Cobb-Douglas"""
        A1, K1, L1, alpha = p1['A'], p1['K'], p1['L'], p1['α']
        A2, K2, L2, _ = p2['A'], p2['K'], p2['L'], p2['α']
        
        # Calcul en log
        lnY1 = np.log(A1) + alpha * np.log(K1) + (1 - alpha) * np.log(L1)
        lnY2 = np.log(A2) + alpha * np.log(K2) + (1 - alpha) * np.log(L2)
        delta_lnY = lnY2 - lnY1
        
        # Effets
        effect_A = np.log(A2) - np.log(A1)
        effect_K = alpha * (np.log(K2) - np.log(K1))
        effect_L = (1 - alpha) * (np.log(L2) - np.log(L1))
        
        # Vérification
        total_effect = effect_A + effect_K + effect_L
        
        return {
            'formula': 'Y = A * K^α * L^(1-α)',
            'log_changes': {
                'delta_lnY': delta_lnY,
                'delta_lnA': effect_A,
                'delta_lnK': np.log(K2) - np.log(K1),
                'delta_lnL': np.log(L2) - np.log(L1)
            },
            'effects': {
                'technology_effect': effect_A,
                'capital_effect': effect_K,
                'labor_effect': effect_L,
                'total_effect': total_effect
            },
            'contributions': {
                'technology': (effect_A / delta_lnY * 100) if delta_lnY != 0 else 0,
                'capital': (effect_K / delta_lnY * 100) if delta_lnY != 0 else 0,
                'labor': (effect_L / delta_lnY * 100) if delta_lnY != 0 else 0
            },
            'alpha_value': alpha
        }
    
    def create_custom_formula(self, expression: str, name: str = None) -> str:
        """
        Crée une formule personnalisée à partir d'une expression
        
        Args:
            expression: Expression mathématique (ex: "Y = A*B/C")
            name: Nom de la formule (optionnel)
            
        Returns:
            ID de la formule créée
        """
        # Analyse de l'expression avec sympy
        expr_str = expression.split('=')[1].strip()
        symbols = sp.symbols(re.findall(r'[A-Za-z][A-Za-z0-9_]*', expr_str))
        expr = sp.sympify(expr_str)
        
        # Création de la formule
        formula_id = name or f"custom_{len(self.custom_formulas) + 1}"
        
        formula = Formula(
            name=formula_id,
            expression=expression,
            variables=[str(s) for s in symbols],
            decomposition_rule=self._derive_decomposition_rule(expr, symbols)
        )
        
        self.custom_formulas[formula_id] = formula
        return formula_id
    
    def _derive_decomposition_rule(self, expr, symbols):
        """Dérive la règle de décomposition pour une expression"""
        # Implémentation simplifiée - pour une vraie application, 
        # utiliser sympy pour calculer les dérivées partielles
        return "Décomposition générique (calcul symbolique nécessaire)"
    
    def _validate_data(self, data: Dict, variables: List[str], periods: Tuple[str, str]):
        """Valide les données d'entrée"""
        period1, period2 = periods
        
        for var in variables:
            if var not in data:
                raise ValueError(f"Variable '{var}' manquante dans les données")
            
            var_data = data[var]
            if period1 not in var_data:
                raise ValueError(f"Période '{period1}' manquante pour la variable '{var}'")
            if period2 not in var_data:
                raise ValueError(f"Période '{period2}' manquante pour la variable '{var}'")
            
            # Vérifier que les valeurs sont numériques
            if not isinstance(var_data[period1], (int, float)):
                raise ValueError(f"Valeur non numérique pour {var}[{period1}]")
            if not isinstance(var_data[period2], (int, float)):
                raise ValueError(f"Valeur non numérique pour {var}[{period2}]")

# Fonctions utilitaires pour le module mathématique
def calculate_growth_rate(initial, final, periods=1):
    """Calcule le taux de croissance"""
    if initial == 0:
        return np.nan
    return ((final / initial) ** (1/periods) - 1) * 100

def decompose_logarithmic(variable, base_value, current_value):
    """Décomposition logarithmique pour les ratios"""
    return np.log(current_value) - np.log(base_value)