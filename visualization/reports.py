"""
Module de génération de rapports professionnels
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Union
from io import BytesIO
import base64
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import plotly.io as pio

class ReportGenerator:
    """
    Génère des rapports PDF professionnels à partir des résultats
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Crée des styles personnalisés pour les rapports"""
        # Style pour le titre principal
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1E3A8A'),
            spaceAfter=12,
            alignment=1  # Centré
        ))
        
        # Style pour les sous-titres
        self.styles.add(ParagraphStyle(
            name='SubTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#3B82F6'),
            spaceAfter=8,
            spaceBefore=12
        ))
        
        # Style pour le texte de conclusion
        self.styles.add(ParagraphStyle(
            name='Conclusion',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#6B7280'),
            backColor=colors.HexColor('#F3F4F6'),
            borderPadding=5,
            spaceBefore=10,
            spaceAfter=10
        ))
    
    def generate_pdf_report(self, results: Dict, analysis_type: str, 
                           metadata: Dict = None) -> BytesIO:
        """
        Génère un rapport PDF complet
        
        Args:
            results: Résultats de l'analyse
            analysis_type: Type d'analyse ('demographic', 'regression', etc.)
            metadata: Métadonnées supplémentaires
            
        Returns:
            Buffer BytesIO avec le PDF
        """
        buffer = BytesIO()
        
        # Créer le document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        # 1. En-tête
        story.append(self._create_header(metadata))
        story.append(Spacer(1, 20))
        
        # 2. Titre
        title = f"Rapport d'analyse de décomposition - {analysis_type.capitalize()}"
        story.append(Paragraph(title, self.styles['MainTitle']))
        story.append(Spacer(1, 20))
        
        # 3. Métadonnées
        if metadata:
            story.append(self._create_metadata_section(metadata))
            story.append(Spacer(1, 15))
        
        # 4. Résumé exécutif
        story.append(self._create_executive_summary(results, analysis_type))
        story.append(Spacer(1, 15))
        
        # 5. Résultats détaillés
        story.append(self._create_detailed_results(results, analysis_type))
        story.append(Spacer(1, 15))
        
        # 6. Interprétation
        story.append(self._create_interpretation_section(results, analysis_type))
        story.append(Spacer(1, 15))
        
        # 7. Méthodologie
        story.append(self._create_methodology_section(analysis_type))
        story.append(Spacer(1, 15))
        
        # 8. Conclusion
        story.append(self._create_conclusion_section(results))
        story.append(Spacer(1, 20))
        
        # 9. Pied de page
        story.append(self._create_footer())
        
        # Construire le PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    def _create_header(self, metadata: Dict = None) -> Table:
        """Crée l'en-tête du rapport"""
        date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        header_data = [
            ["APPLICATION D'ANALYSE DE DÉCOMPOSITION", f"Date: {date_str}"],
            ["IFORD Groupe 4", f"Version: 1.0.0"]
        ]
        
        header_table = Table(header_data, colWidths=[4*inch, 2*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1E3A8A')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        return header_table
    
    def _create_metadata_section(self, metadata: Dict) -> List:
        """Crée la section des métadonnées"""
        elements = []
        
        elements.append(Paragraph("Informations sur l'analyse", self.styles['SubTitle']))
        
        # Tableau des métadonnées
        meta_data = []
        for key, value in metadata.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    meta_data.append([f"{key}.{subkey}", str(subvalue)])
            else:
                meta_data.append([key, str(value)])
        
        if meta_data:
            meta_table = Table(meta_data, colWidths=[2*inch, 3*inch])
            meta_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E5E7EB')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('PADDING', (0, 0), (-1, -1), 3),
            ]))
            
            elements.append(meta_table)
        
        return elements
    
    def _create_executive_summary(self, results: Dict, analysis_type: str) -> List:
        """Crée le résumé exécutif"""
        elements = []
        
        elements.append(Paragraph("Résumé exécutif", self.styles['SubTitle']))
        
        summary_text = ""
        
        if analysis_type == 'demographic' and 'aggregate_results' in results:
            agg = results['aggregate_results']
            summary_text = f"""
            Cette analyse de décomposition démographique révèle un changement total de 
            <b>{agg['total_change']:.4f}</b> unités. Ce changement est attribuable à 
            <b>{agg['composition_percent']:.1f}%</b> à un effet de composition (changement 
            dans la structure de la population) et à <b>{agg['behavior_percent']:.1f}%</b> 
            à un effet de comportement (changement dans les comportements moyens).
            """
        
        elif analysis_type == 'regression' and 'decomposition' in results:
            decomp = results['decomposition']
            summary_text = f"""
            La décomposition de régression montre une différence totale de 
            <b>{decomp['total_difference']:.4f}</b> unités entre les groupes. 
            <b>{decomp['explained_percent']:.1f}%</b> de cette différence s'explique par 
            les caractéristiques observables, tandis que <b>{decomp['unexplained_percent']:.1f}%</b> 
            reste non expliqué (potentiellement dû à la discrimination ou à des facteurs non observés).
            """
        
        elements.append(Paragraph(summary_text, self.styles['Normal']))
        
        return elements
    
    def _create_detailed_results(self, results: Dict, analysis_type: str) -> List:
        """Crée la section des résultats détaillés"""
        elements = []
        
        elements.append(Paragraph("Résultats détaillés", self.styles['SubTitle']))
        
        # Tableau des résultats principaux
        if analysis_type == 'demographic':
            table_data = self._prepare_demographic_table_data(results)
        elif analysis_type == 'regression':
            table_data = self._prepare_regression_table_data(results)
        elif analysis_type == 'mathematical':
            table_data = self._prepare_mathematical_table_data(results)
        else:
            table_data = [["Résultats non disponibles dans ce format"]]
        
        if table_data:
            results_table = Table(table_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch])
            results_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('PADDING', (0, 0), (-1, -1), 4),
            ]))
            
            elements.append(results_table)
        
        return elements
    
    def _prepare_demographic_table_data(self, results: Dict) -> List:
        """Prépare les données pour le tableau démographique"""
        if 'group_results' not in results:
            return []
        
        df = results['group_results'].head(10)  # Limiter à 10 groupes
        
        table_data = [["Groupe", "Effet Composition", "Effet Comportement", "Total"]]
        
        for _, row in df.iterrows():
            table_data.append([
                str(row['group'])[:20],  # Tronquer les noms longs
                f"{row['effect_composition']:.4f}",
                f"{row['effect_behavior']:.4f}",
                f"{row['total_contribution']:.4f}"
            ])
        
        return table_data
    
    def _prepare_regression_table_data(self, results: Dict) -> List:
        """Prépare les données pour le tableau de régression"""
        if 'decomposition' not in results:
            return []
        
        decomp = results['decomposition']
        
        table_data = [
            ["Composante", "Valeur", "Pourcentage"],
            ["Différence totale", f"{decomp['total_difference']:.4f}", "100.0%"],
            ["Différence expliquée", f"{decomp['explained_difference']:.4f}", 
             f"{decomp['explained_percent']:.1f}%"],
            ["Différence non expliquée", f"{decomp['unexplained_difference']:.4f}", 
             f"{decomp['unexplained_percent']:.1f}%"]
        ]
        
        return table_data
    
    def _prepare_mathematical_table_data(self, results: Dict) -> List:
        """Prépare les données pour le tableau mathématique"""
        table_data = [["Variable", "Période 1", "Période 2", "Δ"]]
        
        if 'values' in results:
            p1 = results['values']['period1']
            p2 = results['values']['period2']
            
            for key in p1.keys():
                if key != 'Y':
                    table_data.append([
                        key,
                        f"{p1[key]:.4f}",
                        f"{p2[key]:.4f}",
                        f"{p2[key] - p1[key]:.4f}"
                    ])
            
            # Ajouter Y
            table_data.append([
                "Y (résultat)",
                f"{p1.get('Y', 0):.4f}",
                f"{p2.get('Y', 0):.4f}",
                f"{results['changes'].get('delta_Y', 0):.4f}"
            ])
        
        return table_data
    
    def _create_interpretation_section(self, results: Dict, analysis_type: str) -> List:
        """Crée la section d'interprétation"""
        elements = []
        
        elements.append(Paragraph("Interprétation des résultats", self.styles['SubTitle']))
        
        interpretation = ""
        
        if analysis_type == 'demographic':
            if results.get('aggregate_results', {}).get('composition_percent', 0) > 70:
                interpretation = """
                <b>Interprétation principale : Effet de composition dominant</b><br/>
                Le changement observé est principalement dû à des modifications dans la 
                structure de la population (effet de composition > 70%). Cela suggère que 
                les politiques ciblant les groupes spécifiques pourraient être efficaces.
                """
            elif results.get('aggregate_results', {}).get('behavior_percent', 0) > 70:
                interpretation = """
                <b>Interprétation principale : Effet de comportement dominant</b><br/>
                Le changement observé est principalement dû à des modifications dans les 
                comportements individuels (effet de comportement > 70%). Des politiques 
                générales affectant l'ensemble de la population pourraient être appropriées.
                """
            else:
                interpretation = """
                <b>Interprétation principale : Effets combinés</b><br/>
                Le changement résulte d'une combinaison d'effets de composition et de 
                comportement. Une approche mixte de politiques publiques pourrait être nécessaire.
                """
        
        elif analysis_type == 'regression':
            if results.get('decomposition', {}).get('unexplained_percent', 0) > 50:
                interpretation = """
                <b>Attention : Discrimination potentielle</b><br/>
                Plus de 50% de la différence entre les groupes n'est pas expliquée par 
                les caractéristiques observables. Cela pourrait indiquer une discrimination 
                ou l'effet de facteurs non mesurés.
                """
            else:
                interpretation = """
                <b>Différences principalement expliquées</b><br/>
                La majorité de la différence entre les groupes s'explique par les 
                caractéristiques observables. Les politiques devraient se concentrer sur 
                la réduction des écarts dans ces caractéristiques.
                """
        
        elements.append(Paragraph(interpretation, self.styles['Normal']))
        
        return elements
    
    def _create_methodology_section(self, analysis_type: str) -> List:
        """Crée la section méthodologique"""
        elements = []
        
        elements.append(Paragraph("Méthodologie", self.styles['SubTitle']))
        
        methodology = ""
        
        if analysis_type == 'demographic':
            methodology = """
            <b>Méthode de décomposition démographique (Kitagawa, 1955)</b><br/>
            Formule : ΔY = Σ[(y₂ᵢ + y₁ᵢ)/2 × (w₂ᵢ - w₁ᵢ)] + Σ[(w₂ᵢ + w₁ᵢ)/2 × (y₂ᵢ - y₁ᵢ)]<br/>
            où y est la variable d'intérêt et w est le poids démographique du groupe i.
            """
        elif analysis_type == 'regression':
            methodology = """
            <b>Méthode Oaxaca-Blinder (1973)</b><br/>
            Formule : ΔY = Δα + β̄ΔX + X̄Δβ<br/>
            Cette méthode décompose les écarts entre groupes en différences expliquées 
            (caractéristiques) et non expliquées (discrimination potentielle).
            """
        elif analysis_type == 'mathematical':
            methodology = """
            <b>Décomposition mathématique exacte</b><br/>
            Basée sur la différenciation des formules mathématiques. Chaque variable 
            contribue proportionnellement à son changement et à sa position dans la formule.
            """
        
        elements.append(Paragraph(methodology, self.styles['Normal']))
        
        return elements
    
    def _create_conclusion_section(self, results: Dict) -> List:
        """Crée la section de conclusion"""
        elements = []
        
        elements.append(Paragraph("Conclusion et recommandations", self.styles['SubTitle']))
        
        conclusion = """
        <b>Points clés :</b><br/>
        1. Cette analyse identifie les sources principales du changement observé<br/>
        2. Les résultats permettent de cibler les interventions politiques<br/>
        3. La méthode garantit une attribution rigoureuse des contributions<br/>
        <br/>
        <b>Limitations :</b><br/>
        • La décomposition identifie les sources, pas les causes ultimes<br/>
        • Les résultats dépendent de la qualité et de la complétude des données<br/>
        • L'interprétation nécessite une connaissance du contexte<br/>
        """
        
        elements.append(Paragraph(conclusion, self.styles['Conclusion']))
        
        return elements
    
    def _create_footer(self) -> Paragraph:
        """Crée le pied de page"""
        footer_text = """
        <b>Power by Lab_Math and SCSM Group & CIE.</b><br/>
        Copyright 2026, tous droits réservés.<br/>
        Ce rapport a été généré automatiquement par l'Application d'Analyse de Décomposition IFORD.<br/>
        Pour plus d'informations : contact@iford-decomposition.org
        """
        
        footer = Paragraph(footer_text, ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=1,  # Centré
            spaceBefore=20
        ))
        
        return footer
    
    def generate_html_report(self, results: Dict, analysis_type: str) -> str:
        """
        Génère un rapport HTML (pour l'interface web)
        """
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Rapport de décomposition - {analysis_type}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    color: #333;
                }}
                .header {{
                    background-color: #1E3A8A;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px;
                }}
                .section {{
                    margin: 20px 0;
                    padding: 15px;
                    border-left: 4px solid #3B82F6;
                    background-color: #F9FAFB;
                }}
                .section-title {{
                    color: #3B82F6;
                    font-size: 18px;
                    margin-bottom: 10px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 10px 0;
                }}
                th {{
                    background-color: #3B82F6;
                    color: white;
                    padding: 10px;
                    text-align: left;
                }}
                td {{
                    padding: 8px;
                    border-bottom: 1px solid #ddd;
                }}
                tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    text-align: center;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Rapport d'analyse de décomposition</h1>
                <p>{analysis_type_cap} - Généré le {date}</p>
            </div>
            
            {content}
            
            <div class="footer">
                <p><strong>Power by Lab_Math and SCSM Group & CIE.</strong></p>
                <p>Copyright 2026, tous droits réservés.</p>
                <p>Rapport généré automatiquement par l'Application d'Analyse de Décomposition IFORD</p>
            </div>
        </body>
        </html>
        """
        
        # Préparer le contenu selon le type d'analyse
        content = self._generate_html_content(results, analysis_type)
        
        # Remplir le template
        html = html_template.format(
            analysis_type=analysis_type,
            analysis_type_cap=analysis_type.capitalize(),
            date=datetime.now().strftime("%d/%m/%Y %H:%M"),
            content=content
        )
        
        return html
    
    def _generate_html_content(self, results: Dict, analysis_type: str) -> str:
        """Génère le contenu HTML pour le rapport"""
        content_parts = []
        
        # Résumé exécutif
        if analysis_type == 'demographic' and 'aggregate_results' in results:
            agg = results['aggregate_results']
            summary = f"""
            <div class="section">
                <div class="section-title">📋 Résumé exécutif</div>
                <p>Changement total : <strong>{agg['total_change']:.4f}</strong> unités</p>
                <p>Effet de composition : <strong>{agg['composition_percent']:.1f}%</strong></p>
                <p>Effet de comportement : <strong>{agg['behavior_percent']:.1f}%</strong></p>
            </div>
            """
            content_parts.append(summary)
        
        # Tableau des résultats
        if 'group_results' in results and analysis_type == 'demographic':
            df = results['group_results'].head(10)
            
            table_rows = ""
            for _, row in df.iterrows():
                table_rows += f"""
                <tr>
                    <td>{row['group']}</td>
                    <td>{row['effect_composition']:.4f}</td>
                    <td>{row['effect_behavior']:.4f}</td>
                    <td>{row['total_contribution']:.4f}</td>
                </tr>
                """
            
            table = f"""
            <div class="section">
                <div class="section-title">📊 Résultats détaillés par groupe</div>
                <table>
                    <tr>
                        <th>Groupe</th>
                        <th>Effet Composition</th>
                        <th>Effet Comportement</th>
                        <th>Contribution totale</th>
                    </tr>
                    {table_rows}
                </table>
            </div>
            """
            content_parts.append(table)
        
        return '\n'.join(content_parts)

# Export simple pour Excel
class ExcelExporter:
    """Export des résultats vers Excel avec formatage"""
    
    @staticmethod
    def export_to_excel(results: Dict, filename: str):
        """Exporte les résultats vers un fichier Excel"""
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Feuille principale
            if 'group_results' in results:
                results['group_results'].to_excel(writer, sheet_name='Résultats détaillés', index=False)
            
            # Feuille de synthèse
            summary_data = []
            if 'aggregate_results' in results:
                agg = results['aggregate_results']
                summary_data.append(['Changement total', agg['total_change']])
                summary_data.append(['Effet de composition', agg['composition_effect']])
                summary_data.append(['Effet de comportement', agg['behavior_effect']])
                summary_data.append(['% Composition', f"{agg['composition_percent']:.1f}%"])
                summary_data.append(['% Comportement', f"{agg['behavior_percent']:.1f}%"])
            
            summary_df = pd.DataFrame(summary_data, columns=['Description', 'Valeur'])
            summary_df.to_excel(writer, sheet_name='Synthèse', index=False)
            
            # Ajouter le footer
            workbook = writer.book
            for sheet in workbook.worksheets:
                sheet.cell(row=sheet.max_row + 3, column=1, 
                          value="Power by Lab_Math and SCSM Group & CIE. Copyright 2026, tous droits réservés.")
        
        return filename