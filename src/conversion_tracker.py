"""
Conversion Tracking System
Track prospect contacts, conversions, and measure scoring effectiveness
"""

import pandas as pd
import os
from datetime import datetime


class ConversionTracker:
    """Track and analyze prospect conversions"""
    
    def __init__(self, conversions_file='data/conversions.csv'):
        self.conversions_file = conversions_file
        self._initialize_file()
    
    def _initialize_file(self):
        """Initialize conversions file if it doesn't exist"""
        if not os.path.exists(self.conversions_file):
            # Create empty conversions file with schema
            df = pd.DataFrame(columns=[
                'prospect_id', 'contact_date', 'contacted_by', 'contact_method',
                'status', 'converted', 'contract_value', 'conversion_date',
                'priority_score', 'adjusted_score', 'segment', 'notes'
            ])
            os.makedirs(os.path.dirname(self.conversions_file), exist_ok=True)
            df.to_csv(self.conversions_file, index=False)
            print(f"✓ Created conversions tracking file: {self.conversions_file}")
    
    def log_contact(self, prospect_id, contacted_by, contact_method='Phone', 
                    status='Contacted', priority_score=None, adjusted_score=None, 
                    segment=None, notes=''):
        """Log a contact attempt"""
        df = pd.read_csv(self.conversions_file)
        
        new_entry = {
            'prospect_id': prospect_id,
            'contact_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'contacted_by': contacted_by,
            'contact_method': contact_method,
            'status': status,
            'converted': False,
            'contract_value': 0,
            'conversion_date': '',
            'priority_score': priority_score,
            'adjusted_score': adjusted_score,
            'segment': segment,
            'notes': notes
        }
        
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        df.to_csv(self.conversions_file, index=False)
        
        return True
    
    def log_conversion(self, prospect_id, contract_value, notes=''):
        """Log a successful conversion"""
        df = pd.read_csv(self.conversions_file)
        
        # Find the prospect's last contact record
        prospect_records = df[df['prospect_id'] == prospect_id]
        
        if len(prospect_records) == 0:
            print(f"⚠️  No contact record found for prospect {prospect_id}")
            return False
        
        # Update the last record
        last_idx = prospect_records.index[-1]
        df.loc[last_idx, 'converted'] = True
        df.loc[last_idx, 'contract_value'] = contract_value
        df.loc[last_idx, 'conversion_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df.loc[last_idx, 'status'] = 'Converted'
        if notes:
            df.loc[last_idx, 'notes'] = notes
        
        df.to_csv(self.conversions_file, index=False)
        print(f"✓ Conversion logged for prospect {prospect_id}: {contract_value}€")
        
        return True
    
    def update_status(self, prospect_id, status, notes=''):
        """Update prospect status (e.g., 'No Answer', 'Not Interested', 'Follow-up Scheduled')"""
        df = pd.read_csv(self.conversions_file)
        
        prospect_records = df[df['prospect_id'] == prospect_id]
        
        if len(prospect_records) == 0:
            print(f"⚠️  No contact record found for prospect {prospect_id}")
            return False
        
        last_idx = prospect_records.index[-1]
        df.loc[last_idx, 'status'] = status
        if notes:
            df.loc[last_idx, 'notes'] = notes
        
        df.to_csv(self.conversions_file, index=False)
        
        return True
    
    def get_conversion_stats(self):
        """Get overall conversion statistics"""
        df = pd.read_csv(self.conversions_file)
        
        if len(df) == 0:
            return {
                'total_contacts': 0,
                'total_conversions': 0,
                'conversion_rate': 0,
                'total_revenue': 0,
                'avg_contract_value': 0
            }
        
        total_contacts = len(df['prospect_id'].unique())
        total_conversions = df['converted'].sum()
        conversion_rate = (total_conversions / total_contacts * 100) if total_contacts > 0 else 0
        total_revenue = df[df['converted'] == True]['contract_value'].sum()
        avg_contract_value = df[df['converted'] == True]['contract_value'].mean()
        
        stats = {
            'total_contacts': total_contacts,
            'total_conversions': int(total_conversions),
            'conversion_rate': conversion_rate,
            'total_revenue': total_revenue,
            'avg_contract_value': avg_contract_value if not pd.isna(avg_contract_value) else 0
        }
        
        return stats
    
    def analyze_score_effectiveness(self):
        """Analyze if high scores actually convert better"""
        df = pd.read_csv(self.conversions_file)
        
        if len(df) == 0 or df['priority_score'].isna().all():
            return None
        
        # Remove NaN scores
        df_clean = df[df['priority_score'].notna()].copy()
        
        if len(df_clean) == 0:
            return None
        
        # Create score bins
        df_clean['score_bin'] = pd.cut(
            df_clean['priority_score'],
            bins=[0, 12, 15, 18, 100],
            labels=['Low (0-12)', 'Medium (12-15)', 'High (15-18)', 'Very High (18+)']
        )
        
        # Calculate conversion rate by score bin
        effectiveness = df_clean.groupby('score_bin').agg({
            'prospect_id': 'count',
            'converted': ['sum', 'mean']
        }).reset_index()
        
        effectiveness.columns = ['Score Range', 'Total Contacts', 'Conversions', 'Conversion Rate']
        effectiveness['Conversion Rate'] = effectiveness['Conversion Rate'] * 100
        
        return effectiveness
    
    def analyze_by_segment(self):
        """Analyze conversion rates by prospect segment"""
        df = pd.read_csv(self.conversions_file)
        
        if len(df) == 0 or df['segment'].isna().all():
            return None
        
        df_clean = df[df['segment'].notna()].copy()
        
        if len(df_clean) == 0:
            return None
        
        segment_analysis = df_clean.groupby('segment').agg({
            'prospect_id': 'count',
            'converted': ['sum', 'mean'],
            'contract_value': 'sum'
        }).reset_index()
        
        segment_analysis.columns = ['Segment', 'Total Contacts', 'Conversions', 'Conversion Rate', 'Total Revenue']
        segment_analysis['Conversion Rate'] = segment_analysis['Conversion Rate'] * 100
        segment_analysis['Avg Contract Value'] = segment_analysis['Total Revenue'] / segment_analysis['Conversions']
        
        return segment_analysis.sort_values('Conversion Rate', ascending=False)
    
    def get_contact_history(self, prospect_id):
        """Get full contact history for a prospect"""
        df = pd.read_csv(self.conversions_file)
        history = df[df['prospect_id'] == prospect_id].sort_values('contact_date')
        
        return history
    
    def get_recent_contacts(self, days=7):
        """Get contacts from the last N days"""
        df = pd.read_csv(self.conversions_file)
        
        if len(df) == 0:
            return df
        
        df['contact_date'] = pd.to_datetime(df['contact_date'])
        cutoff_date = datetime.now() - pd.Timedelta(days=days)
        
        recent = df[df['contact_date'] >= cutoff_date].sort_values('contact_date', ascending=False)
        
        return recent
    
    def export_report(self, output_file='exports/conversion_report.csv'):
        """Export detailed conversion report"""
        df = pd.read_csv(self.conversions_file)
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df.to_csv(output_file, index=False)
        
        print(f"✓ Conversion report exported to: {output_file}")
        
        return output_file


if __name__ == '__main__':
    # Example usage
    tracker = ConversionTracker()
    
    print("\n" + "="*60)
    print("CONVERSION TRACKING SYSTEM - TEST")
    print("="*60)
    
    # Test logging a contact
    print("\nTest 1: Log a contact...")
    tracker.log_contact(
        prospect_id=123,
        contacted_by='Agent A',
        contact_method='Phone',
        status='Contacted',
        priority_score=18.5,
        adjusted_score=16.2,
        segment='Actifs - Familles',
        notes='Interested in premium coverage'
    )
    
    # Test logging a conversion
    print("\nTest 2: Log a conversion...")
    tracker.log_conversion(
        prospect_id=123,
        contract_value=2400,
        notes='Closed - 2 year contract'
    )
    
    # Get statistics
    print("\nTest 3: Get conversion statistics...")
    stats = tracker.get_conversion_stats()
    print("\nConversion Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*60)
    print("Conversion tracking system ready!")
    print("="*60)
