"""
Business Intelligence Module
Generates insights, recommendations, and email templates
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class BusinessIntelligence:
    """Generate business insights and recommendations"""
    
    def __init__(self, df):
        self.df = df
        self.current_date = datetime.now()
    
    def analyze_seasonal_trends(self):
        """Analyze seasonal submission patterns"""
        self.df['month'] = pd.to_datetime(self.df['submission_date']).dt.month
        self.df['year'] = pd.to_datetime(self.df['submission_date']).dt.year
        
        monthly_submissions = self.df.groupby('month').size()
        peak_months = monthly_submissions.nlargest(3).index.tolist()
        
        month_names = {
            1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
            5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
            9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
        }
        
        peak_month_names = [month_names[m] for m in peak_months]
        
        return {
            'peak_months': peak_month_names,
            'monthly_distribution': monthly_submissions.to_dict(),
            'recommendation': f"Les mois de forte demande sont {', '.join(peak_month_names)}. Planifiez des campagnes marketing 1-2 mois avant."
        }
    
    def identify_high_demand_areas(self):
        """Identify geographic areas with high demand"""
        # Group by department (first 2 digits of zip code)
        self.df['department'] = self.df['zip_code'].astype(str).str[:2]
        
        dept_analysis = self.df.groupby('department').agg({
            'id': 'count',
            'priority_score': 'mean'
        }).rename(columns={'id': 'count', 'priority_score': 'avg_score'})
        
        dept_analysis = dept_analysis.sort_values('count', ascending=False).head(10)
        
        top_dept = dept_analysis.head(3).index.tolist()
        
        # French department names (partial)
        dept_names = {
            '75': 'Paris', '13': 'Bouches-du-Rhône', '69': 'Rhône',
            '92': 'Hauts-de-Seine', '93': 'Seine-Saint-Denis', '94': 'Val-de-Marne',
            '95': 'Val-d\'Oise', '77': 'Seine-et-Marne', '78': 'Yvelines',
            '59': 'Nord', '31': 'Haute-Garonne', '44': 'Loire-Atlantique',
            '33': 'Gironde', '06': 'Alpes-Maritimes'
        }
        
        top_areas = [dept_names.get(d, f'Département {d}') for d in top_dept]
        
        return {
            'top_departments': dept_analysis,
            'recommendation': f"Concentrez vos efforts marketing sur : {', '.join(top_areas)}. Ces zones montrent la plus forte demande."
        }
    
    def analyze_campaign_performance(self):
        """Analyze which campaigns perform best"""
        campaign_stats = self.df.groupby('source').agg({
            'id': 'count',
            'priority_score': 'mean'
        }).rename(columns={'id': 'leads', 'priority_score': 'avg_score'})
        
        campaign_stats['quality_index'] = campaign_stats['avg_score'] / campaign_stats['avg_score'].mean()
        campaign_stats = campaign_stats.sort_values('quality_index', ascending=False)
        
        top_campaigns = campaign_stats.head(5)
        
        return {
            'campaign_stats': campaign_stats,
            'top_campaigns': top_campaigns,
            'recommendation': f"Les campagnes les plus performantes sont : {', '.join(top_campaigns.index[:3].tolist())}. Investissez davantage dans ces canaux."
        }
    
    def identify_underserved_segments(self):
        """Identify market segments with low coverage"""
        segment_coverage = self.df.groupby('social_security_regime').size()
        total = len(self.df)
        
        # Expected market share (approximate French market)
        expected_share = {
            'Régime général': 0.75,
            'Régime TNS': 0.08,
            'Régime agricole': 0.10,
            'Alsace-Moselle': 0.04,
            'Hors sécu': 0.02,
            'Régime CFE': 0.01
        }
        
        gaps = {}
        for regime, expected in expected_share.items():
            actual = segment_coverage.get(regime, 0) / total
            gap = expected - actual
            if gap > 0:
                gaps[regime] = {
                    'expected': expected * 100,
                    'actual': actual * 100,
                    'gap': gap * 100
                }
        
        if gaps:
            top_gap = max(gaps.items(), key=lambda x: x[1]['gap'])
            recommendation = f"Le segment '{top_gap[0]}' est sous-représenté ({top_gap[1]['actual']:.1f}% vs {top_gap[1]['expected']:.1f}% attendu). Opportunité de croissance."
        else:
            recommendation = "Bonne couverture de tous les segments."
        
        return {
            'gaps': gaps,
            'recommendation': recommendation
        }
    
    def predict_upcoming_high_season(self):
        """Predict upcoming high-demand periods"""
        current_month = self.current_date.month
        
        # Analyze historical patterns
        monthly_avg = self.df.groupby(
            pd.to_datetime(self.df['submission_date']).dt.month
        ).size()
        
        # Next 3 months
        upcoming_months = [(current_month + i - 1) % 12 + 1 for i in range(1, 4)]
        upcoming_demand = [monthly_avg.get(m, 0) for m in upcoming_months]
        
        month_names = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                      'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        
        forecast = {
            month_names[m-1]: demand 
            for m, demand in zip(upcoming_months, upcoming_demand)
        }
        
        peak_next = max(forecast.items(), key=lambda x: x[1])
        
        return {
            'forecast': forecast,
            'recommendation': f"Pic de demande attendu en {peak_next[0]} (~{peak_next[1]:.0f} leads). Préparez une campagne maintenant."
        }
    
    def get_all_recommendations(self):
        """Get comprehensive business recommendations"""
        recommendations = []
        
        # Seasonal trends
        seasonal = self.analyze_seasonal_trends()
        recommendations.append({
            'category': 'Tendances Saisonnières',
            'insight': seasonal['recommendation'],
            'priority': 'High'
        })
        
        # Geographic
        geographic = self.identify_high_demand_areas()
        recommendations.append({
            'category': 'Ciblage Géographique',
            'insight': geographic['recommendation'],
            'priority': 'High'
        })
        
        # Campaigns
        campaigns = self.analyze_campaign_performance()
        recommendations.append({
            'category': 'Performance des Campagnes',
            'insight': campaigns['recommendation'],
            'priority': 'Medium'
        })
        
        # Underserved segments
        segments = self.identify_underserved_segments()
        recommendations.append({
            'category': 'Segments de Marché',
            'insight': segments['recommendation'],
            'priority': 'Medium'
        })
        
        # Upcoming season
        forecast = self.predict_upcoming_high_season()
        recommendations.append({
            'category': 'Prévisions',
            'insight': forecast['recommendation'],
            'priority': 'High'
        })
        
        return pd.DataFrame(recommendations)


class EmailGenerator:
    """Generate personalized email templates"""
    
    @staticmethod
    def generate_high_priority_alert(prospects_df):
        """Generate alert email for high-priority leads"""
        count = len(prospects_df)
        avg_score = prospects_df['priority_score'].mean()
        
        top_3 = prospects_df.head(3)
        
        email = f"""
Objet: 🔥 {count} Nouveaux Leads à Haute Priorité

Bonjour,

Vous avez {count} nouveaux prospects à forte valeur qui nécessitent une attention immédiate.

Score moyen de priorité: {avg_score:.1f}/25

📋 TOP 3 LEADS À CONTACTER AUJOURD'HUI:

"""
        
        for idx, row in top_3.iterrows():
            email += f"""
{row['title']} {row['first_name']} {row['last_name']}
   📞 {row['phone_number']}
   📧 {row['email']}
   ⭐ Score: {row['priority_score']:.1f}
   👨‍👩‍👧‍👦 Famille: {row['num_children']} enfant(s){' + conjoint' if row['spouse_age_at_submission'] != -999 else ''}
   📅 Date d'effet souhaitée: {row['effective_date']}
   
"""
        
        email += """
💡 ACTION REQUISE:
- Contacter ces prospects dans les 24 heures
- Préparer une proposition de couverture complète
- Souligner les avantages des garanties élevées

Cordialement,
Système de Gestion des Leads
"""
        
        return email
    
    @staticmethod
    def generate_re_engagement_email(prospect):
        """Generate re-engagement email for past leads"""
        months_since = (datetime.now() - pd.to_datetime(prospect['submission_date'])).days // 30
        
        email = f"""
Objet: Nouvelles offres de mutuelle santé 2025

Bonjour {prospect['title']} {prospect['last_name']},

Il y a {months_since} mois, vous avez manifesté votre intérêt pour une complémentaire santé via notre site.

🎯 POURQUOI REPRENDRE CONTACT MAINTENANT?

✓ Nouvelles garanties 2025 plus avantageuses
✓ Tarifs spéciaux pour les familles (vous avez {prospect['num_children']} enfant(s))
✓ Prise en charge renforcée des soins optiques et dentaires

Votre profil:
- Âge: {prospect['age_at_submission']} ans
- Régime: {prospect['social_security_regime']}
- Situation familiale: {'Avec conjoint' if prospect['spouse_age_at_submission'] != -999 else 'Seul(e)'}

📞 Je reste à votre disposition pour vous présenter nos nouvelles offres adaptées à votre situation.

Cordialement,
Votre conseiller
{prospect['phone_number']}
"""
        
        return email
    
    @staticmethod
    def generate_personalized_advice(prospect):
        """Generate personalized coverage advice"""
        age = prospect['age_at_submission']
        has_family = prospect['num_children'] > 0 or prospect['spouse_age_at_submission'] != -999
        
        advice = f"""
Objet: Recommandations personnalisées pour votre mutuelle santé

Bonjour {prospect['title']} {prospect['last_name']},

Suite à votre demande, voici mes recommandations pour une couverture optimale:

📊 VOTRE PROFIL:
- Âge: {age} ans
- Situation: {'Famille (' + str(prospect['num_children']) + ' enfant(s))' if has_family else 'Personne seule'}
- Régime: {prospect['social_security_regime']}

💡 MES RECOMMANDATIONS:
"""
        
        # Age-based recommendations
        if age > 55:
            advice += """
✓ PRIORITÉ: Garanties MAXI en hospitalisation et soins médicaux
  → Risque accru de problèmes de santé avec l'âge
  → Remboursement optimal des dépassements d'honoraires
  → Chambre particulière en cas d'hospitalisation
"""
        elif age > 40:
            advice += """
✓ RECOMMANDÉ: Garanties ÉLEVÉES en optique et dentaire
  → Besoins croissants en soins préventifs
  → Meilleure prise en charge des prothèses
"""
        else:
            advice += """
✓ ÉQUILIBRÉ: Garanties MOYENNES à ÉLEVÉES
  → Bonne couverture pour les soins courants
  → Protection contre les imprévus
"""
        
        # Family recommendations
        if prospect['num_children'] > 1:
            advice += """
✓ FAMILLE: Garanties renforcées optique et dentaire
  → Orthodontie pour les enfants (jusqu'à 16 ans)
  → Lunettes et lentilles remboursées
  → Soins préventifs pris en charge
"""
        
        advice += f"""

💰 ESTIMATION MENSUELLE: 
Pour votre profil, comptez environ {50 + age * 0.5 + prospect['num_children'] * 20:.0f}€/mois
(cotisation indicative, devis personnalisé sur demande)

📞 Contactez-moi pour un devis détaillé et sans engagement.

Cordialement,
Votre conseiller
"""
        
        return advice


if __name__ == '__main__':
    # Load data
    df = pd.read_csv('data/cleaned_prospects.csv')
    
    # Business Intelligence
    bi = BusinessIntelligence(df)
    
    print("="*60)
    print("BUSINESS INTELLIGENCE REPORT")
    print("="*60)
    
    recommendations = bi.get_all_recommendations()
    print("\n📊 RECOMMANDATIONS STRATÉGIQUES:\n")
    for _, rec in recommendations.iterrows():
        print(f"[{rec['priority']}] {rec['category']}")
        print(f"   → {rec['insight']}\n")
    
    # Email examples
    print("\n" + "="*60)
    print("EXEMPLES D'EMAILS")
    print("="*60)
    
    high_priority = df.nlargest(5, 'priority_score')
    print("\n📧 EMAIL D'ALERTE HAUTE PRIORITÉ:")
    print(EmailGenerator.generate_high_priority_alert(high_priority))
    
    sample_prospect = df.iloc[0]
    print("\n📧 EMAIL DE RÉENGAGEMENT:")
    print(EmailGenerator.generate_re_engagement_email(sample_prospect))
