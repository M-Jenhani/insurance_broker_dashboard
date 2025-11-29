"""
Data Processing Pipeline for Insurance Broker Dashboard
Handles data cleaning, feature engineering, and score calculation
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re
from html import unescape
import warnings
warnings.filterwarnings('ignore')


class ProspectDataProcessor:
    """Process and clean prospect data"""
    
    def __init__(self):
        self.level_map = {'ECO': 1, 'MOYEN': 2, 'ELEVE': 3, 'MAXI': 4}
        self.regime_map = {
            'Régime général': 1,
            'Alsace-Moselle': 2,
            'Régime TNS': 3,
            'Régime agricole': 4,
            'Hors sécu': 5,
            'Régime CFE': 6
        }
        self.regime_weight_map = {
            'Régime général': 0.5,
            'Alsace-Moselle': 0,
            'Régime TNS': 1,
            'Régime agricole': 0.5,
            'Hors sécu': 0.8,
            'Régime CFE': 0.5
        }
        self.urban_zipcodes = ['75', '77', '92', '93', '94', '95']  # Île-de-France
    
    def load_data(self, file_path):
        """Load prospect data from CSV"""
        df = pd.read_csv(file_path, dtype={'zipcode': str, 'num_tel': str})
        print(f"Loaded {len(df)} records")
        return df
    
    def rename_columns(self, df):
        """Rename French columns to English"""
        column_mapping = {
            'nom': 'last_name',
            'prenom': 'first_name',
            'civilite': 'title',
            'adresse': 'address',
            'ville': 'city',
            'zipcode': 'zip_code',
            'num_tel': 'phone_number',
            'email': 'email',
            'regime': 'social_security_regime',
            'date_naiss': 'birth_date',
            'date_effect': 'effective_date',
            'conjointbirthdate': 'spouse_birth_date',
            'nbrenfants': 'num_children',
            'source': 'source',
            'birthdatechild1': 'child1_birth_date',
            'birthdatechild2': 'child2_birth_date',
            'birthdatechild3': 'child3_birth_date',
            'birthdatechild4': 'child4_birth_date',
            'birthdatechild5': 'child5_birth_date',
            'dcr': 'submission_date',
            'soin_medical': 'medical_care',
            'hospitalisation': 'hospitalization',
            'optique': 'optical',
            'dentaire': 'dental'
        }
        df.rename(columns=column_mapping, inplace=True)
        return df
    
    def handle_missing_values(self, df):
        """Handle missing values"""
        # Drop rows with no name
        df.dropna(subset=['last_name'], inplace=True)
        
        # Fill missing title
        df['title'].fillna('M', inplace=True)
        df.loc[df['title'] == 'Mr', 'title'] = 'M'
        
        # Fill missing phone
        df.dropna(subset=['phone_number'], inplace=True)
        
        # Fill missing regime
        df['social_security_regime'].fillna('Régime général', inplace=True)
        
        # Fill missing children count
        df['num_children'].fillna(0, inplace=True)
        
        # Drop missing medical care
        df.dropna(subset=['medical_care'], inplace=True)
        
        # Fill missing optical/dental
        df['optical'].fillna('ECO', inplace=True)
        df['dental'].fillna('ECO', inplace=True)
        
        return df
    
    def clean_messy_data(self, df):
        """Clean messy and inconsistent data"""
        # Decode HTML entities
        string_cols = ['last_name', 'first_name', 'title', 'address', 'city', 'email',
                      'zip_code', 'phone_number', 'social_security_regime', 'birth_date',
                      'effective_date', 'spouse_birth_date', 'source', 'child1_birth_date',
                      'child2_birth_date', 'child3_birth_date', 'child4_birth_date',
                      'child5_birth_date', 'submission_date', 'medical_care',
                      'hospitalization', 'optical', 'dental']
        
        for col in string_cols:
            if col in df.columns and df[col].dtype == 'object':
                df[col] = df[col].apply(lambda x: unescape(str(x)) if pd.notna(x) else x)
                df[col] = df[col].astype(str).str.replace(r'\\\'', "'", regex=True)
        
        # Standardize regime values
        regime_fixes = {
            'General scheme': 'Régime général',
            'General Diet': 'Régime général',
            'Esquema geral': 'Régime général',
            'Általános séma': 'Régime général',
            '??????-??????': 'Régime général',
            '??????????? ?????': 'Régime général'
        }
        for old, new in regime_fixes.items():
            df.loc[df['social_security_regime'] == old, 'social_security_regime'] = new
        
        # Standardize source values
        df.loc[df['source'] == 'Proges', 'source'] = 'PROGES'
        
        # Fix coverage level typos
        coverage_fixes = {
            '3': 'ELEVE',
            'Medium.': 'MOYEN',
            'High.': 'ELEVE'
        }
        for col in ['medical_care', 'hospitalization', 'optical', 'dental']:
            for old, new in coverage_fixes.items():
                df.loc[df[col] == old, col] = new
        
        return df
    
    def is_random_name(self, s, min_length=3):
        """Detect fake/test names"""
        if pd.isna(s):
            return False
        
        pattern = r"[^a-zA-ZÀ-ÖØ-öø-ÿ0-9 @\'\-\.]"
        if re.search(pattern, s):
            return True
        
        s = s.strip().lower()
        if len(s) < min_length:
            return True
        
        # Repeated characters
        if len(s) > 0 and len(set(s)) / len(s) < 0.4:
            return True
        
        # Test patterns
        keyboard_patterns = ['t+e+s+t+', 'j+a+k+e+', 'd+o+e+']
        if any(re.search(pattern, s) for pattern in keyboard_patterns):
            return True
        
        return False
    
    def remove_fake_data(self, df):
        """Remove fake/test submissions"""
        # Remove fake names
        fake_mask = df['last_name'].apply(self.is_random_name) | df['first_name'].apply(self.is_random_name)
        df = df[~fake_mask].copy()
        
        # Remove test emails
        test_patterns = ['test', 'jake.doe', 'example.com']
        for pattern in test_patterns:
            df = df[~df['email'].str.contains(pattern, case=False, na=False)]
        
        return df
    
    def remove_duplicates(self, df):
        """Remove duplicate submissions"""
        df['submission_date'] = pd.to_datetime(df['submission_date'], errors='coerce')
        df_sorted = df.sort_values(['email', 'submission_date']).reset_index(drop=True)
        
        # Mark duplicates
        df_sorted['is_duplicate'] = df_sorted['email'].duplicated(keep=False)
        df_sorted['submission_date_diff'] = (df_sorted.groupby('email')['submission_date']
                                             .diff().dt.total_seconds() / 3600)
        
        # Find close duplicates (within 72 hours)
        close_duplicates = df_sorted[
            df_sorted['is_duplicate'] & 
            (df_sorted['submission_date_diff'].notnull()) & 
            (df_sorted['submission_date_diff'] <= 72)
        ]
        
        # Keep only the last submission for each duplicate
        if len(close_duplicates) > 0:
            result_last = close_duplicates.sort_values(['email', 'submission_date']).drop_duplicates(
                subset=['email'], keep='last'
            )
            rows_to_drop = close_duplicates[~close_duplicates['id'].isin(result_last['id'])]
            df_sorted = df_sorted[~df_sorted['id'].isin(rows_to_drop['id'])]
        
        return df_sorted.drop(columns=['is_duplicate', 'submission_date_diff'])
    
    def convert_dates(self, df):
        """Convert date columns to datetime"""
        date_columns = ['birth_date', 'effective_date', 'spouse_birth_date',
                       'child1_birth_date', 'child2_birth_date', 'child3_birth_date',
                       'child4_birth_date', 'child5_birth_date']
        
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], format='%d/%m/%Y', errors='coerce', dayfirst=True)
        
        return df
    
    def calculate_ages(self, df):
        """Calculate ages at submission and current ages"""
        date_cols = ['birth_date', 'spouse_birth_date', 'child1_birth_date',
                    'child2_birth_date', 'child3_birth_date', 'child4_birth_date',
                    'child5_birth_date']
        
        reference_date = datetime.now()
        
        for col in date_cols:
            age_at_sub_col = col.replace('birth_date', 'age_at_submission')
            current_age_col = col.replace('birth_date', 'current_age')
            
            df[age_at_sub_col] = ((df['submission_date'] - df[col]).dt.days // 365).fillna(-999).astype(int)
            df[current_age_col] = ((pd.Timestamp(reference_date) - df[col]).dt.days // 365).fillna(-999).astype(int)
        
        return df
    
    def validate_ages(self, df):
        """Validate and clean age data"""
        # Fix prospect ages
        valid_mask = (df['age_at_submission'] >= 18) & (df['age_at_submission'] <= 100)
        if not valid_mask.all():
            median_age = df.loc[valid_mask, 'age_at_submission'].median()
            df.loc[~valid_mask & (df['age_at_submission'] != -999), 'age_at_submission'] = median_age
        
        # Fix spouse ages
        spouse_valid = (df['spouse_age_at_submission'] >= 18) & (df['spouse_age_at_submission'] <= 100)
        if not spouse_valid.all():
            median_spouse = df.loc[spouse_valid, 'spouse_age_at_submission'].median()
            df.loc[~spouse_valid & (df['spouse_age_at_submission'] != -999), 'spouse_age_at_submission'] = median_spouse
        
        # Fix children ages (must be 0-25)
        child_cols = ['child1_age_at_submission', 'child2_age_at_submission',
                     'child3_age_at_submission', 'child4_age_at_submission',
                     'child5_age_at_submission']
        
        for col in child_cols:
            invalid_mask = ((df[col] < 0) | (df[col] > 25)) & (df[col] != -999)
            df.loc[invalid_mask, col] = -999
        
        # Update num_children based on valid ages
        df['num_children'] = df[child_cols].apply(
            lambda x: ((x >= 0) & (x <= 25)).sum(), axis=1
        ).astype('Int64')
        
        return df
    
    def derive_features(self, df):
        """Derive additional features"""
        # Spouse age difference
        df['spouse_age_diff'] = abs(df['age_at_submission'] - df['spouse_age_at_submission'])
        df.loc[df['spouse_age_at_submission'] == -999, 'spouse_age_diff'] = np.nan
        
        # Child age difference (oldest child)
        child_cols = ['child1_age_at_submission', 'child2_age_at_submission',
                     'child3_age_at_submission', 'child4_age_at_submission',
                     'child5_age_at_submission']
        
        def calc_child_age_diff(row):
            child_ages = [row[col] for col in child_cols if row[col] > 0]
            if child_ages:
                return row['age_at_submission'] - max(child_ages)
            return 0
        
        df['child_age_diff'] = df.apply(calc_child_age_diff, axis=1)
        
        # Days to effective date
        df['days_to_effective'] = (df['effective_date'] - df['submission_date'].dt.normalize()).dt.days
        df['days_to_effective'] = df['days_to_effective'].fillna(0).clip(lower=0).astype('Int64')
        
        return df
    
    def calculate_contact_quality(self, df):
        """Calculate contact quality score based on email and phone"""
        # Email domain quality
        def email_quality(email):
            if pd.isna(email):
                return 0
            
            email = str(email).lower()
            domain = email.split('@')[-1] if '@' in email else ''
            
            # Corporate/professional domains (best quality)
            corporate_indicators = ['.fr', '.com', '.eu', '.org']
            if any(domain.endswith(corp) for corp in corporate_indicators):
                # Check if it's not a free email provider
                free_providers = ['gmail', 'yahoo', 'hotmail', 'outlook', 'free', 'orange', 'sfr', 'laposte']
                if not any(provider in domain for provider in free_providers):
                    return 1.0  # Corporate email
            
            # Professional free emails (medium quality)
            if any(provider in domain for provider in ['gmail', 'yahoo', 'outlook', 'hotmail']):
                return 0.5  # Personal but legitimate
            
            # French providers (medium quality)
            if any(provider in domain for provider in ['orange', 'free', 'sfr', 'laposte', 'wanadoo']):
                return 0.5
            
            # Disposable/suspicious (low quality)
            disposable = ['yopmail', 'temp', 'trash', 'jetable', '10minute', 'guerrilla']
            if any(disp in domain for disp in disposable):
                return 0
            
            return 0.3  # Unknown domain
        
        df['email_quality'] = df['email'].apply(email_quality)
        
        # Phone validation (French format)
        def phone_quality(phone):
            if pd.isna(phone):
                return 0
            
            phone_str = str(phone).replace(' ', '').replace('.', '').replace('-', '')
            
            # Valid French mobile (06, 07) or landline (01-05, 09)
            if len(phone_str) == 10 and phone_str.startswith(('01', '02', '03', '04', '05', '06', '07', '09')):
                # Check for fake patterns
                fake_patterns = ['0000000000', '0600000000', '0700000000', '0123456789', '1234567890']
                if phone_str in fake_patterns:
                    return 0
                return 1.0
            
            return 0.3  # Potentially invalid
        
        df['phone_quality'] = df['phone_number'].apply(phone_quality)
        
        # Combined contact quality score (0-2 points)
        df['contact_quality_score'] = df['email_quality'] + df['phone_quality']
        
        return df
    
    def encode_and_score(self, df):
        """Encode categorical variables and calculate priority score"""
        # Encode coverage levels
        for col in ['medical_care', 'hospitalization', 'optical', 'dental']:
            df[col] = df[col].map(self.level_map)
        
        # Encode regime
        df['social_security_regime_encoded'] = df['social_security_regime'].map(self.regime_map)
        df['regime_score'] = df['social_security_regime'].map(self.regime_weight_map)
        
        # Source score (campaigns get bonus)
        df['source_score'] = df['source'].apply(lambda x: 1 if x != 'web' else 0)
        
        # Zip code score (urban areas)
        df['zip_score'] = df['zip_code'].str[:2].apply(
            lambda x: 1 if x in self.urban_zipcodes else 0
        )
        
        # Calculate coverage score (capped at 12 to prevent dominance)
        df['coverage_score'] = (
            df['medical_care'] + 
            df['hospitalization'] + 
            df['optical'] + 
            df['dental']
        ).clip(upper=12)
        
        # Non-linear children score (1 child=+1, 2-3=+2, 4+=+3)
        def children_score(n):
            if n == 0:
                return 0
            elif n == 1:
                return 1
            elif n <= 3:
                return 2
            else:
                return 3
        
        df['children_score'] = df['num_children'].apply(children_score)
        
        # Age buckets instead of binary (graduated scoring)
        def age_score(age):
            if age < 36:
                return 0
            elif age <= 50:
                return 0.5
            elif age <= 65:
                return 1
            else:
                return 1.5
        
        df['age_score'] = df['age_at_submission'].apply(age_score)
        
        # Calculate contact quality first
        df = self.calculate_contact_quality(df)
        
        # Calculate priority score with improved formula
        df['priority_score'] = (
            df['coverage_score'] +  # Max 12 points (was 16)
            df['children_score'] +  # 0-3 points (was 0-2)
            df['regime_score'] +    # 0-1 points
            df['age_score'] +       # 0-1.5 points (was 0-1)
            df['spouse_age_at_submission'].apply(lambda x: 1 if x != -999 else 0) +  # 0-1 points
            df['days_to_effective'].apply(lambda x: 1 if 0 <= x <= 90 else 0) +  # 0-1 points
            df['source_score'] +    # 0-1 points
            df['contact_quality_score']  # 0-2 points (NEW)
        )
        
        return df
    
    def apply_time_decay(self, df):
        """Apply time decay to reduce score for older leads"""
        from datetime import datetime
        
        today = pd.Timestamp(datetime.now())
        days_old = (today - df['submission_date']).dt.days
        
        # Decay formula: 100% at day 0, ~60% at day 30, ~37% at day 60, ~25% at day 90
        # Using exponential decay: e^(-days/60)
        freshness_multiplier = np.exp(-days_old / 60)
        
        # Minimum multiplier of 0.2 (don't completely dismiss old leads)
        freshness_multiplier = np.maximum(0.2, freshness_multiplier)
        
        df['days_since_submission'] = days_old
        df['freshness_multiplier'] = freshness_multiplier
        df['adjusted_score'] = (df['priority_score'] * freshness_multiplier).round(2)
        
        return df
    
    def process_pipeline(self, file_path):
        """Run complete processing pipeline"""
        print("Starting data processing pipeline...")
        
        # Load data
        df = self.load_data(file_path)
        initial_count = len(df)
        
        # Process
        df = self.rename_columns(df)
        print(f"✓ Renamed columns")
        
        df = self.handle_missing_values(df)
        print(f"✓ Handled missing values ({initial_count - len(df)} rows removed)")
        
        df = self.clean_messy_data(df)
        print(f"✓ Cleaned messy data")
        
        df = self.remove_fake_data(df)
        print(f"✓ Removed fake data ({initial_count - len(df)} total removed)")
        
        df = self.remove_duplicates(df)
        print(f"✓ Removed duplicates ({initial_count - len(df)} total removed)")
        
        df = self.convert_dates(df)
        print(f"✓ Converted dates")
        
        df['num_children'] = df['num_children'].astype('Int64')
        
        df = self.calculate_ages(df)
        print(f"✓ Calculated ages")
        
        df = self.validate_ages(df)
        print(f"✓ Validated ages")
        
        df = self.derive_features(df)
        print(f"✓ Derived features")
        
        df = self.encode_and_score(df)
        print(f"✓ Encoded and scored")
        
        df = self.apply_time_decay(df)
        print(f"✓ Applied time decay")
        
        print(f"\nProcessing complete! Final count: {len(df)} records")
        print(f"Removed: {initial_count - len(df)} records ({(initial_count - len(df)) / initial_count * 100:.1f}%)")
        print(f"\nScore Statistics:")
        print(f"  Priority Score: {df['priority_score'].mean():.2f} (mean), {df['priority_score'].std():.2f} (std)")
        print(f"  Adjusted Score: {df['adjusted_score'].mean():.2f} (mean), {df['adjusted_score'].std():.2f} (std)")
        print(f"  Contact Quality: {df['contact_quality_score'].mean():.2f} (mean)")
        
        return df


if __name__ == '__main__':
    processor = ProspectDataProcessor()
    df = processor.process_pipeline('data/prospects.csv')
    
    # Save cleaned data
    df.to_csv('data/cleaned_prospects.csv', index=False)
    print("\nSaved to 'data/cleaned_prospects.csv'")
    
    # Display info
    print("\n" + "="*50)
    print("CLEANED DATA SUMMARY")
    print("="*50)
    print(df.info())
    print("\nPriority Score Distribution:")
    print(df['priority_score'].describe())
