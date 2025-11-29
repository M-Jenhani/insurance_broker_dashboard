"""
Synthetic Data Generator for French Insurance Broker Dashboard
Generates realistic prospect data matching the original schema
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# French names and locations
FIRST_NAMES = [
    'Jean', 'Marie', 'Pierre', 'Sophie', 'Michel', 'Nathalie', 'Philippe', 'Isabelle',
    'Laurent', 'Christine', 'François', 'Catherine', 'Nicolas', 'Sylvie', 'Alain', 'Martine',
    'Olivier', 'Véronique', 'Stéphane', 'Patricia', 'Thierry', 'Monique', 'Bernard', 'Nicole',
    'Bruno', 'Françoise', 'Pascal', 'Chantal', 'Didier', 'Jacqueline', 'Eric', 'Annie',
    'Jacques', 'Valérie', 'Christian', 'Sandrine', 'Gérard', 'Corinne', 'Patrick', 'Brigitte',
    'David', 'Caroline', 'Alexandre', 'Céline', 'Thomas', 'Audrey', 'Julien', 'Émilie',
    'Vincent', 'Laetitia', 'Sébastien', 'Julie', 'Marc', 'Delphine', 'Christophe', 'Karine'
]

LAST_NAMES = [
    'Martin', 'Bernard', 'Dubois', 'Thomas', 'Robert', 'Richard', 'Petit', 'Durand',
    'Leroy', 'Moreau', 'Simon', 'Laurent', 'Lefebvre', 'Michel', 'Garcia', 'David',
    'Bertrand', 'Roux', 'Vincent', 'Fournier', 'Morel', 'Girard', 'André', 'Lefevre',
    'Mercier', 'Dupont', 'Lambert', 'Bonnet', 'François', 'Martinez', 'Legrand', 'Garnier',
    'Faure', 'Rousseau', 'Blanc', 'Guerin', 'Muller', 'Henry', 'Roussel', 'Nicolas',
    'Perrin', 'Morin', 'Mathieu', 'Clement', 'Gauthier', 'Dumont', 'Lopez', 'Fontaine'
]

CITIES = [
    ('Paris', '75001'), ('Lyon', '69001'), ('Marseille', '13001'), ('Toulouse', '31000'),
    ('Nice', '06000'), ('Nantes', '44000'), ('Strasbourg', '67000'), ('Montpellier', '34000'),
    ('Bordeaux', '33000'), ('Lille', '59000'), ('Rennes', '35000'), ('Reims', '51100'),
    ('Saint-Étienne', '42000'), ('Le Havre', '76600'), ('Toulon', '83000'), ('Grenoble', '38000'),
    ('Dijon', '21000'), ('Angers', '49000'), ('Nîmes', '30000'), ('Villeurbanne', '69100'),
    ('Créteil', '94000'), ('Versailles', '78000'), ('Boulogne-Billancourt', '92100'),
    ('Montreuil', '93100'), ('Argenteuil', '95100'), ('Saint-Denis', '93200')
]

REGIMES = [
    'Régime général', 'Alsace-Moselle', 'Régime TNS', 
    'Régime agricole', 'Hors sécu', 'Régime CFE'
]

REGIME_WEIGHTS = [0.70, 0.05, 0.10, 0.08, 0.05, 0.02]

COVERAGE_LEVELS = ['ECO', 'MOYEN', 'ELEVE', 'MAXI']

SOURCES = [
    'web', 'zra-sept', 'MH-12M', 'MH-50M-Eric', 'MH-30M', 'PROGES', 'MH-32MC', 'DR',
    'MH50-Eric', 'MH-60S', 'ERIC', 'MH2', 'MH1', 'MH-80', 'MH-42',
    'Celibataire_178_Vital', 'Celibataire_45_Eric', 'fb-compagne-2023',
    'fb-mutuelle-senior-mars-1', 'couple30_54_Vital', 'couple30_54_Eric', 'MH80',
    'ORANGE_01_09'
]

SOURCE_WEIGHTS = [0.65] + [0.35 / 22] * 22  # Web is 65%, others split remaining


def generate_birth_date(min_age=18, max_age=80, reference_date=None):
    """Generate a random birth date"""
    if reference_date is None:
        reference_date = datetime.now()
    age = random.randint(min_age, max_age)
    birth_year = reference_date.year - age
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)  # Safe for all months
    return f"{birth_day:02d}/{birth_month:02d}/{birth_year}"


def generate_coverage_level(age, num_children, has_spouse):
    """Generate coverage level based on profile (higher coverage for older/families)"""
    base_weights = [0.15, 0.35, 0.30, 0.20]  # ECO, MOYEN, ELEVE, MAXI
    
    # Adjust for age (older people tend to choose better coverage)
    if age > 55:
        base_weights = [0.05, 0.25, 0.35, 0.35]
    elif age > 45:
        base_weights = [0.10, 0.30, 0.35, 0.25]
    
    # Adjust for family (families tend to choose better coverage)
    if num_children > 1 or has_spouse:
        base_weights = [w * 0.8 if i == 0 else w * 1.1 for i, w in enumerate(base_weights)]
    
    # Normalize
    total = sum(base_weights)
    base_weights = [w / total for w in base_weights]
    
    return np.random.choice(COVERAGE_LEVELS, p=base_weights)


def generate_phone():
    """Generate French phone number"""
    prefix = random.choice(['06', '07'])  # Mobile prefixes
    return prefix + ''.join([str(random.randint(0, 9)) for _ in range(8)])


def generate_email(first_name, last_name):
    """Generate email address"""
    domains = ['gmail.com', 'yahoo.fr', 'orange.fr', 'free.fr', 'sfr.fr', 'laposte.net', 'hotmail.fr']
    separators = ['.', '_', '']
    
    first = first_name.lower().replace('é', 'e').replace('è', 'e').replace('ê', 'e')
    last = last_name.lower().replace('é', 'e').replace('è', 'e').replace('ê', 'e')
    
    separator = random.choice(separators)
    domain = random.choice(domains)
    
    # Sometimes add numbers
    suffix = str(random.randint(1, 99)) if random.random() < 0.3 else ''
    
    return f"{first}{separator}{last}{suffix}@{domain}"


def generate_prospects(n=16000, start_date='2019-01-01', end_date='2025-09-13'):
    """Generate synthetic prospect data"""
    
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    prospects = []
    
    for i in range(n):
        # Submission date
        days_diff = (end - start).days
        submission_date = start + timedelta(days=random.randint(0, days_diff))
        
        # Basic info
        title = random.choice(['M', 'Mme'])
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        city, zip_code = random.choice(CITIES)
        
        # Age and birth date
        age = random.randint(18, 80)
        birth_year = submission_date.year - age
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        birth_date = f"{birth_day:02d}/{birth_month:02d}/{birth_year}"
        
        # Spouse (40% have spouse, more likely if older)
        has_spouse = random.random() < (0.3 if age < 35 else 0.5)
        spouse_birth_date = None
        if has_spouse:
            spouse_age = age + random.randint(-5, 5)  # Similar age
            spouse_age = max(18, min(80, spouse_age))
            spouse_year = submission_date.year - spouse_age
            spouse_month = random.randint(1, 12)
            spouse_day = random.randint(1, 28)
            spouse_birth_date = f"{spouse_day:02d}/{spouse_month:02d}/{spouse_year}"
        
        # Children (distribution based on age)
        if age < 25:
            num_children = np.random.choice([0, 1, 2], p=[0.8, 0.15, 0.05])
        elif age < 35:
            num_children = np.random.choice([0, 1, 2, 3], p=[0.3, 0.35, 0.25, 0.1])
        elif age < 50:
            num_children = np.random.choice([0, 1, 2, 3, 4], p=[0.2, 0.25, 0.35, 0.15, 0.05])
        else:
            num_children = np.random.choice([0, 1, 2, 3], p=[0.5, 0.2, 0.2, 0.1])
        
        # Generate children birth dates
        children_dates = [None] * 5
        if num_children > 0:
            min_parent_age = min(age, spouse_age if has_spouse else 100)
            for j in range(num_children):
                child_age = random.randint(0, min(25, min_parent_age - 18))
                child_year = submission_date.year - child_age
                child_month = random.randint(1, 12)
                child_day = random.randint(1, 28)
                children_dates[j] = f"{child_day:02d}/{child_month:02d}/{child_year}"
        
        # Social security regime
        regime = np.random.choice(REGIMES, p=REGIME_WEIGHTS)
        
        # Source
        source = np.random.choice(SOURCES, p=SOURCE_WEIGHTS)
        
        # Coverage levels
        medical_care = generate_coverage_level(age, num_children, has_spouse)
        hospitalization = generate_coverage_level(age, num_children, has_spouse)
        optical = generate_coverage_level(age, num_children, has_spouse)
        dental = generate_coverage_level(age, num_children, has_spouse)
        
        # Effective date (usually 1-90 days after submission, some immediate)
        if random.random() < 0.3:  # 30% want immediate coverage
            days_to_effective = random.randint(0, 15)
        else:
            days_to_effective = random.randint(15, 90)
        effective_date = submission_date + timedelta(days=days_to_effective)
        
        # Format dates
        submission_str = submission_date.strftime('%d/%m/%Y %H:%M:%S')
        effective_str = effective_date.strftime('%d/%m/%Y')
        
        prospect = {
            'id': i + 1,
            'nom': last_name,
            'prenom': first_name,
            'civilite': title,
            'adresse': f"{random.randint(1, 200)} Rue {random.choice(['de la Paix', 'Victor Hugo', 'République', 'Nationale', 'des Fleurs'])}",
            'ville': city,
            'zipcode': zip_code,
            'num_tel': generate_phone(),
            'email': generate_email(first_name, last_name),
            'regime': regime,
            'date_naiss': birth_date,
            'date_effect': effective_str,
            'conjointbirthdate': spouse_birth_date if spouse_birth_date else '',
            'nbrenfants': num_children,
            'source': source,
            'birthdatechild1': children_dates[0] if children_dates[0] else '',
            'birthdatechild2': children_dates[1] if children_dates[1] else '',
            'birthdatechild3': children_dates[2] if children_dates[2] else '',
            'birthdatechild4': children_dates[3] if children_dates[3] else '',
            'birthdatechild5': children_dates[4] if children_dates[4] else '',
            'dcr': submission_str,
            'soin_medical': medical_care,
            'hospitalisation': hospitalization,
            'optique': optical,
            'dentaire': dental
        }
        
        prospects.append(prospect)
    
    df = pd.DataFrame(prospects)
    
    # Add some messy data (5% of records)
    n_messy = int(n * 0.05)
    messy_indices = random.sample(range(n), n_messy)
    
    for idx in messy_indices[:n_messy // 5]:
        # Duplicate some entries (form bugs)
        duplicate_idx = random.choice(range(len(df)))
        df = pd.concat([df, df.iloc[[duplicate_idx]]], ignore_index=True)
    
    # Reset IDs
    df['id'] = range(1, len(df) + 1)
    
    return df


if __name__ == '__main__':
    print("Generating synthetic insurance prospect data...")
    df = generate_prospects(n=16000)
    
    # Save to CSV
    df.to_csv('data/prospects.csv', index=False)
    print(f"Generated {len(df)} prospect records")
    print("\nDataFrame Info:")
    print(df.info())
    print("\nSample data:")
    print(df.head())
    print("\nSource distribution:")
    print(df['source'].value_counts())
