"""
Module de décomposition structurelle
Analyses multi-niveaux, décomposition emboîtée et modèles structurels
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import warnings
from scipy import stats

class StructuralDecomposition:
    """
    Classe pour les décompositions structurelles complexes
    """
    
    def __init__(self):
        self.methods = {
            'nested': "Décomposition emboîtée",
            'multi_level': "Analyse multi-niveaux",
            'demographic_components': "Composantes démographiques",
            'path_analysis': "Analyse des chemins"
        }
    
    def nested_decomposition(self, df: pd.DataFrame, outcome: str, 
                            primary_group: str, secondary_groups: List[str],
                            periods: Tuple[str, str]) -> Dict:
        """
        Décomposition emboîtée hiérarchique
        
        Args:
            df: DataFrame avec les données
            outcome: Variable d'intérêt
            primary_group: Groupe principal (ex: région)
            secondary_groups: Groupes secondaires (ex: sexe, éducation)
            periods: Périodes à comparer
            
        Returns:
            Résultats de la décomposition emboîtée
        """
        period1, period2 = periods
        
        # Filtrage des périodes
        df1 = df[df['period'] == period1].copy()
        df2 = df[df['period'] == period2].copy()
        
        results = {
            'primary_group': primary_group,
            'secondary_groups': secondary_groups,
            'periods': periods,
            'levels': {}
        }
        
        # Niveau 1: Groupe principal
        primary_results = self._decompose_by_group(df1, df2, outcome, primary_group)
        results['levels']['primary'] = primary_results
        
        # Niveaux secondaires pour chaque catégorie du groupe principal
        for category in df[primary_group].unique():
            sub_df1 = df1[df1[primary_group] == category]
            sub_df2 = df2[df2[primary_group] == category]
            
            category_results = {}
            for secondary in secondary_groups:
                decomp = self._decompose_by_group(sub_df1, sub_df2, outcome, secondary)
                category_results[secondary] = decomp
            
            results['levels']['secondary'][category] = category_results
        
        # Calcul des contributions hiérarchiques
        contributions = self._calculate_hierarchical_contributions(results)
        results['hierarchical_contributions'] = contributions
        
        return results
    
    def _decompose_by_group(self, df1: pd.DataFrame, df2: pd.DataFrame, 
                           outcome: str, group_var: str) -> Dict:
        """Décomposition simple par groupe"""
        results = {}
        
        for group in pd.concat([df1[group_var], df2[group_var]]).unique():
            group1 = df1[df1[group_var] == group][outcome].mean() if group in df1[group_var].values else np.nan
            group2 = df2[df2[group_var] == group][outcome].mean() if group in df2[group_var].values else np.nan
            
            # Poids (proportion dans la population)
            weight1 = len(df1[df1[group_var] == group]) / len(df1) if len(df1) > 0 else 0
            weight2 = len(df2[df2[group_var] == group]) / len(df2) if len(df2) > 0 else 0
            
            results[group] = {
                'mean_period1': group1,
                'mean_period2': group2,
                'change': group2 - group1 if not np.isnan(group1) and not np.isnan(group2) else np.nan,
                'weight_period1': weight1,
                'weight_period2': weight2
            }
        
        # Calcul de la décomposition globale pour ce niveau
        global_result = self._calculate_global_decomposition(df1, df2, outcome, group_var)
        results['_global'] = global_result
        
        return results
    
    def _calculate_global_decomposition(self, df1, df2, outcome, group_var):
        """Calcule la décomposition globale pour un niveau"""
        # Moyenne globale
        Y1 = df1[outcome].mean()
        Y2 = df2[outcome].mean()
        delta_Y = Y2 - Y1
        
        # Décomposition par groupe
        composition_effect = 0
        behavior_effect = 0
        
        all_groups = set(df1[group_var].unique()) | set(df2[group_var].unique())
        
        for group in all_groups:
            # Valeurs du groupe
            y1 = df1[df1[group_var] == group][outcome].mean() if group in df1[group_var].values else Y1
            y2 = df2[df2[group_var] == group][outcome].mean() if group in df2[group_var].values else Y2
            
            # Poids
            w1 = len(df1[df1[group_var] == group]) / len(df1) if len(df1) > 0 else 0
            w2 = len(df2[df2[group_var] == group]) / len(df2) if len(df2) > 0 else 0
            
            # Contributions
            composition_effect += ((y1 + y2) / 2) * (w2 - w1)
            behavior_effect += ((w1 + w2) / 2) * (y2 - y1)
        
        return {
            'Y1': Y1,
            'Y2': Y2,
            'delta_Y': delta_Y,
            'composition_effect': composition_effect,
            'behavior_effect': behavior_effect,
            'composition_percent': (composition_effect / delta_Y * 100) if delta_Y != 0 else 0,
            'behavior_percent': (behavior_effect / delta_Y * 100) if delta_Y != 0 else 0
        }
    
    def _calculate_hierarchical_contributions(self, results: Dict) -> Dict:
        """Calcule les contributions hiérarchiques"""
        contributions = {}
        
        # Contribution du niveau primaire
        primary_global = results['levels']['primary']['_global']
        contributions['primary'] = {
            'composition': primary_global['composition_percent'],
            'behavior': primary_global['behavior_percent']
        }
        
        # Contributions conditionnelles des niveaux secondaires
        contributions['secondary'] = {}
        
        for category, secondary_results in results['levels']['secondary'].items():
            category_contrib = {}
            for var_name, var_results in secondary_results.items():
                if '_global' in var_results:
                    global_res = var_results['_global']
                    category_contrib[var_name] = {
                        'composition': global_res['composition_percent'],
                        'behavior': global_res['behavior_percent']
                    }
            contributions['secondary'][category] = category_contrib
        
        return contributions
    
    def demographic_components_decomposition(self, df: pd.DataFrame, outcome: str,
                                           age_var: str, period_var: str,
                                           components: List[str] = None) -> Dict:
        """
        Décomposition par composantes démographiques (fécondité, mortalité, migration)
        
        Args:
            df: DataFrame avec données démographiques
            outcome: Variable d'intérêt (ex: taux de dépendance)
            age_var: Variable d'âge
            period_var: Variable temporelle
            components: Composantes à inclure (fertility, mortality, migration)
            
        Returns:
            Résultats de la décomposition démographique
        """
        if components is None:
            components = ['fertility', 'mortality', 'migration']
        
        periods = sorted(df[period_var].unique())
        if len(periods) < 2:
            raise ValueError("Au moins deux périodes sont nécessaires")
        
        results = {
            'components': components,
            'periods': periods,
            'decompositions': {}
        }
        
        # Pour chaque paire de périodes consécutives
        for i in range(len(periods) - 1):
            p1, p2 = periods[i], periods[i+1]
            
            df1 = df[df[period_var] == p1].copy()
            df2 = df[df[period_var] == p2].copy()
            
            decomposition = {}
            
            # Effet de structure par âge (composition)
            age_effect = self._calculate_age_structure_effect(df1, df2, outcome, age_var)
            decomposition['age_structure'] = age_effect
            
            # Effets spécifiques des composantes
            if 'fertility' in components:
                fertility_effect = self._estimate_fertility_effect(df1, df2, outcome)
                decomposition['fertility'] = fertility_effect
            
            if 'mortality' in components:
                mortality_effect = self._estimate_mortality_effect(df1, df2, outcome)
                decomposition['mortality'] = mortality_effect
            
            if 'migration' in components:
                migration_effect = self._estimate_migration_effect(df1, df2, outcome)
                decomposition['migration'] = migration_effect
            
            # Effet comportemental résiduel
            total_change = df2[outcome].mean() - df1[outcome].mean()
            explained_change = sum(effect['contribution'] for effect in decomposition.values())
            residual_effect = total_change - explained_change
            
            decomposition['residual'] = {
                'contribution': residual_effect,
                'percent': (residual_effect / total_change * 100) if total_change != 0 else 0,
                'interpretation': "Effet comportemental et autres facteurs non démographiques"
            }
            
            results['decompositions'][f'{p1}-{p2}'] = {
                'total_change': total_change,
                'components': decomposition,
                'summary': self._summarize_demographic_decomposition(decomposition)
            }
        
        return results
    
    def _calculate_age_structure_effect(self, df1, df2, outcome, age_var):
        """Calcule l'effet de la structure par âge"""
        # Groupement par âge
        age_groups = sorted(set(df1[age_var].unique()) | set(df2[age_var].unique()))
        
        effect = 0
        for age in age_groups:
            # Valeur moyenne pour cet âge (moyenne sur les deux périodes)
            y1 = df1[df1[age_var] == age][outcome].mean() if age in df1[age_var].values else 0
            y2 = df2[df2[age_var] == age][outcome].mean() if age in df2[age_var].values else 0
            y_bar = (y1 + y2) / 2
            
            # Poids (proportion de la population)
            w1 = len(df1[df1[age_var] == age]) / len(df1) if len(df1) > 0 else 0
            w2 = len(df2[df2[age_var] == age]) / len(df2) if len(df2) > 0 else 0
            
            effect += y_bar * (w2 - w1)
        
        return {
            'contribution': effect,
            'interpretation': "Effet du changement dans la structure par âge de la population"
        }
    
    def _estimate_fertility_effect(self, df1, df2, outcome):
        """Estime l'effet de la fécondité (version simplifiée)"""
        # Dans une vraie implémentation, utiliserait les taux de fécondité par âge
        return {
            'contribution': 0,  # Placeholder
            'interpretation': "Effet du changement dans les taux de fécondité"
        }
    
    def _estimate_mortality_effect(self, df1, df2, outcome):
        """Estime l'effet de la mortalité"""
        return {
            'contribution': 0,  # Placeholder
            'interpretation': "Effet du changement dans les taux de mortalité"
        }
    
    def _estimate_migration_effect(self, df1, df2, outcome):
        """Estime l'effet des migrations"""
        return {
            'contribution': 0,  # Placeholder
            'interpretation': "Effet des migrations nettes"
        }
    
    def _summarize_demographic_decomposition(self, decomposition):
        """Résume la décomposition démographique"""
        total = sum(comp['contribution'] for comp in decomposition.values())
        
        summary = {}
        for name, comp in decomposition.items():
            percent = (comp['contribution'] / total * 100) if total != 0 else 0
            summary[name] = {
                'contribution': comp['contribution'],
                'percent': percent,
                'interpretation': comp.get('interpretation', '')
            }
        
        return summary
    
    def path_analysis_decomposition(self, df: pd.DataFrame, outcome: str,
                                   paths: Dict[str, List[str]]) -> Dict:
        """
        Décomposition par analyse des chemins (Path Analysis)
        
        Args:
            df: DataFrame avec les données
            outcome: Variable dépendante finale
            paths: Dictionnaire des chemins {nom_chemin: [variables]}
            
        Returns:
            Résultats de l'analyse des chemins
        """
        # Cette méthode implémente une version simplifiée de l'analyse des chemins
        # Pour une implémentation complète, utiliser un package comme semopy
        
        results = {
            'paths': {},
            'total_effects': {}
        }
        
        # Pour chaque chemin
        for path_name, variables in paths.items():
            path_results = []
            
            # Régression pour chaque étape du chemin
            for i in range(len(variables)):
                if i == 0:
                    # Première étape: variable initiale -> première variable médiatrice
                    X = df[variables[0]].values.reshape(-1, 1)
                    y = df[variables[1]].values
                elif i < len(variables) - 1:
                    # Étapes intermédiaires
                    X = df[variables[i]].values.reshape(-1, 1)
                    y = df[variables[i+1]].values
                else:
                    # Dernière étape: dernière variable médiatrice -> outcome
                    X = df[variables[-1]].values.reshape(-1, 1)
                    y = df[outcome].values
                
                # Régression simple
                if len(set(X.flatten())) > 1:
                    slope = np.cov(X.flatten(), y)[0, 1] / np.var(X.flatten())
                    path_results.append(slope)
                else:
                    path_results.append(0)
            
            # Effet total du chemin (produit des coefficients)
            total_path_effect = np.prod(path_results)
            
            results['paths'][path_name] = {
                'variables': variables,
                'coefficients': path_results,
                'total_effect': total_path_effect
            }
        
        # Effets totaux
        total_variance = df[outcome].var()
        
        for path_name, path_info in results['paths'].items():
            explained_variance = (path_info['total_effect'] ** 2) * df[path_info['variables'][0]].var()
            percent_explained = (explained_variance / total_variance * 100) if total_variance != 0 else 0
            
            results['total_effects'][path_name] = {
                'explained_variance': explained_variance,
                'percent_explained': percent_explained
            }
        
        return results

# Classe pour les analyses multi-niveaux
class MultiLevelDecomposition:
    """Décomposition multi-niveaux (individu, groupe, société)"""
    
    @staticmethod
    def hierarchical_linear_model(df, outcome, level1_vars, level2_vars, group_var):
        """Modèle linéaire hiérarchique"""
        # Implémentation simplifiée
        pass