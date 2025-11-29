"""
Machine Learning Models for Lead Analysis
Clustering, Anomaly Detection, and Feature Analysis
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import joblib
import warnings
warnings.filterwarnings('ignore')


class ProspectSegmentation:
    """Segment prospects into meaningful groups using K-Means clustering"""
    
    def __init__(self, n_clusters=5):
        self.n_clusters = n_clusters
        self.kmeans = None
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.segment_profiles = None
    
    def prepare_features(self, df):
        """Prepare features for clustering"""
        features = df.copy()
        
        # Select relevant features
        feature_cols = [
            'age_at_submission', 'spouse_age_at_submission', 'num_children',
            'medical_care', 'hospitalization', 'optical', 'dental',
            'social_security_regime_encoded', 'days_to_effective',
            'source_score', 'zip_score', 'priority_score'
        ]
        
        X = features[feature_cols].copy()
        
        # Handle -999 values (missing spouse/children)
        X['has_spouse'] = (X['spouse_age_at_submission'] != -999).astype(int)
        X['spouse_age_at_submission'] = X['spouse_age_at_submission'].replace(-999, 0)
        
        # Calculate total coverage score
        X['coverage_total'] = X['medical_care'] + X['hospitalization'] + X['optical'] + X['dental']
        
        self.feature_columns = X.columns.tolist()
        
        return X
    
    def train_segmentation(self, df):
        """Train K-Means clustering model"""
        print(f"\nTraining K-Means clustering (k={self.n_clusters})...")
        
        X = self.prepare_features(df)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train K-Means
        self.kmeans = KMeans(
            n_clusters=self.n_clusters,
            random_state=42,
            n_init=10,
            max_iter=300
        )
        
        cluster_labels = self.kmeans.fit_predict(X_scaled)
        
        # Add cluster labels to dataframe
        df['segment'] = cluster_labels
        
        # Analyze segment profiles
        self.segment_profiles = self._analyze_segments(df)
        
        print(f"✓ Segmentation complete - {self.n_clusters} clusters identified")
        
        # Print segment summary
        print("\n📊 Segment Overview:")
        for segment_id, profile in self.segment_profiles.items():
            print(f"\nSegment {segment_id}: {profile['name']}")
            print(f"  Size: {profile['size']} prospects ({profile['percentage']:.1f}%)")
            print(f"  Avg Score: {profile['avg_score']:.1f}")
            print(f"  Avg Age: {profile['avg_age']:.1f}")
            print(f"  Characteristics: {profile['description']}")
        
        return cluster_labels
    
    def _analyze_segments(self, df):
        """Analyze and profile each segment"""
        profiles = {}
        
        for segment_id in range(self.n_clusters):
            segment_data = df[df['segment'] == segment_id]
            
            # Calculate statistics
            size = len(segment_data)
            percentage = (size / len(df)) * 100
            avg_score = segment_data['priority_score'].mean()
            avg_age = segment_data['age_at_submission'].mean()
            avg_children = segment_data['num_children'].mean()
            pct_spouse = (segment_data['spouse_age_at_submission'] != -999).mean() * 100
            avg_coverage = (
                segment_data['medical_care'].mean() +
                segment_data['hospitalization'].mean() +
                segment_data['optical'].mean() +
                segment_data['dental'].mean()
            )
            top_regime = segment_data['social_security_regime'].mode()[0] if len(segment_data) > 0 else 'N/A'
            
            # Generate name and description
            name, description = self._generate_segment_profile(
                avg_age, avg_children, pct_spouse, avg_coverage, top_regime, avg_score
            )
            
            profiles[segment_id] = {
                'name': name,
                'size': size,
                'percentage': percentage,
                'avg_score': avg_score,
                'avg_age': avg_age,
                'avg_children': avg_children,
                'pct_spouse': pct_spouse,
                'avg_coverage': avg_coverage,
                'top_regime': top_regime,
                'description': description
            }
        
        return profiles
    
    def _generate_segment_profile(self, age, children, pct_spouse, coverage, regime, score):
        """Generate human-readable segment name and description"""
        
        # Determine age group
        if age < 35:
            age_group = "Jeunes"
        elif age < 50:
            age_group = "Actifs"
        elif age < 65:
            age_group = "Seniors actifs"
        else:
            age_group = "Retraités"
        
        # Determine family status
        if children >= 2:
            family_status = "Familles nombreuses"
        elif children >= 1:
            family_status = "Familles"
        elif pct_spouse > 60:
            family_status = "Couples"
        else:
            family_status = "Célibataires"
        
        # Determine coverage level
        if coverage >= 12:
            coverage_level = "Couverture premium"
        elif coverage >= 8:
            coverage_level = "Couverture élevée"
        elif coverage >= 6:
            coverage_level = "Couverture moyenne"
        else:
            coverage_level = "Couverture économique"
        
        # Generate name
        name = f"{age_group} - {family_status}"
        
        # Generate description
        description = f"{coverage_level}, principalement {regime}"
        if score > 15:
            description += " - Priorité élevée"
        elif score > 12:
            description += " - Priorité moyenne"
        else:
            description += " - Priorité standard"
        
        return name, description
    
    def predict_segment(self, df):
        """Predict segment for new prospects"""
        X = self.prepare_features(df)
        X_scaled = self.scaler.transform(X[self.feature_columns])
        segments = self.kmeans.predict(X_scaled)
        return segments
    
    def get_segment_profile(self, segment_id):
        """Get profile for a specific segment"""
        return self.segment_profiles.get(segment_id, None)
    
    def save_model(self, filepath):
        """Save the trained model"""
        model_data = {
            'kmeans': self.kmeans,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'segment_profiles': self.segment_profiles,
            'n_clusters': self.n_clusters
        }
        joblib.dump(model_data, filepath)
    
    def load_model(self, filepath):
        """Load a trained model"""
        model_data = joblib.load(filepath)
        self.kmeans = model_data['kmeans']
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']
        self.segment_profiles = model_data['segment_profiles']
        self.n_clusters = model_data['n_clusters']


class AnomalyDetector:
    """Detect unusual prospects that might be hidden opportunities"""
    
    def __init__(self, contamination=0.05):
        self.contamination = contamination
        self.iso_forest = None
        self.scaler = StandardScaler()
        self.feature_columns = None
    
    def prepare_features(self, df):
        """Prepare features for anomaly detection"""
        feature_cols = [
            'age_at_submission', 'spouse_age_at_submission', 'num_children',
            'medical_care', 'hospitalization', 'optical', 'dental',
            'social_security_regime_encoded', 'days_to_effective',
            'priority_score'
        ]
        
        X = df[feature_cols].copy()
        X['spouse_age_at_submission'] = X['spouse_age_at_submission'].replace(-999, 0)
        
        self.feature_columns = feature_cols
        return X
    
    def detect_anomalies(self, df):
        """Detect anomalous prospects"""
        print(f"\nDetecting anomalies (threshold={self.contamination*100:.0f}%)...")
        
        X = self.prepare_features(df)
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Isolation Forest
        self.iso_forest = IsolationForest(
            contamination=self.contamination,
            random_state=42,
            n_estimators=100
        )
        
        # Predict (-1 for anomalies, 1 for normal)
        predictions = self.iso_forest.fit_predict(X_scaled)
        anomaly_scores = self.iso_forest.score_samples(X_scaled)
        
        df['is_anomaly'] = (predictions == -1).astype(int)
        df['anomaly_score'] = anomaly_scores
        
        n_anomalies = df['is_anomaly'].sum()
        print(f"✓ Found {n_anomalies} anomalous prospects ({n_anomalies/len(df)*100:.1f}%)")
        
        return df
    
    def get_anomalies(self, df, top_n=50):
        """Get top N most anomalous prospects"""
        anomalies = df[df['is_anomaly'] == 1].copy()
        anomalies = anomalies.sort_values('anomaly_score', ascending=True)
        
        return anomalies.head(top_n)
    
    def explain_anomaly(self, prospect_row, df):
        """Explain why a prospect is anomalous"""
        explanations = []
        
        # Compare to population means
        for col in ['age_at_submission', 'num_children', 'priority_score']:
            prospect_val = prospect_row[col]
            mean_val = df[col].mean()
            std_val = df[col].std()
            z_score = (prospect_val - mean_val) / std_val
            
            if abs(z_score) > 2:
                if z_score > 0:
                    explanations.append(f"{col}: très élevé ({prospect_val:.1f} vs moyenne {mean_val:.1f})")
                else:
                    explanations.append(f"{col}: très faible ({prospect_val:.1f} vs moyenne {mean_val:.1f})")
        
        return explanations if explanations else ["Combinaison inhabituelle de caractéristiques"]
    
    def save_model(self, filepath):
        """Save the trained anomaly detection model"""
        model_data = {
            'iso_forest': self.iso_forest,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'contamination': self.contamination
        }
        joblib.dump(model_data, filepath)
    
    def load_model(self, filepath):
        """Load a trained anomaly detection model"""
        model_data = joblib.load(filepath)
        self.iso_forest = model_data['iso_forest']
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']
        self.contamination = model_data['contamination']


class FeatureAnalyzer:
    """Analyze feature importance and correlations"""
    
    def __init__(self):
        self.feature_importance = None
        self.correlations = None
    
    def save_model(self, filepath):
        """Save the analysis results"""
        model_data = {
            'feature_importance': self.feature_importance,
            'correlations': self.correlations
        }
        joblib.dump(model_data, filepath)
    
    def load_model(self, filepath):
        """Load the analysis results"""
        model_data = joblib.load(filepath)
        self.feature_importance = model_data['feature_importance']
        self.correlations = model_data['correlations']
    
    def analyze_feature_importance(self, df):
        """Calculate feature importance relative to priority score"""
        print("\nAnalyzing feature importance...")
        
        feature_cols = [
            'age_at_submission', 'num_children', 'medical_care', 
            'hospitalization', 'optical', 'dental',
            'social_security_regime_encoded', 'days_to_effective',
            'source_score', 'zip_score'
        ]
        
        # Calculate correlations with priority score
        correlations = []
        for col in feature_cols:
            if col in df.columns:
                # Handle -999 values
                clean_data = df[[col, 'priority_score']].copy()
                if col == 'spouse_age_at_submission':
                    clean_data = clean_data[clean_data[col] != -999]
                
                corr = clean_data[col].corr(clean_data['priority_score'])
                correlations.append({
                    'feature': col,
                    'correlation': abs(corr),
                    'direction': 'positive' if corr > 0 else 'negative'
                })
        
        self.feature_importance = pd.DataFrame(correlations).sort_values(
            'correlation', ascending=False
        )
        
        print("\n📊 Feature Importance (Correlation with Priority Score):")
        for _, row in self.feature_importance.head(10).iterrows():
            direction = "↑" if row['direction'] == 'positive' else "↓"
            print(f"  {row['feature']}: {row['correlation']:.3f} {direction}")
        
        return self.feature_importance
    
    def analyze_correlations(self, df):
        """Analyze feature correlations"""
        feature_cols = [
            'age_at_submission', 'num_children', 'medical_care', 
            'hospitalization', 'optical', 'dental', 'priority_score'
        ]
        
        self.correlations = df[feature_cols].corr()
        return self.correlations


def save_models(segmentation, anomaly_detector, feature_analyzer, output_dir='models'):
    """Save trained models"""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    segmentation.save_model(f'{output_dir}/segmentation_model.pkl')
    anomaly_detector.save_model(f'{output_dir}/anomaly_detector.pkl')
    feature_analyzer.save_model(f'{output_dir}/feature_analyzer.pkl')
    
    print(f"\n✓ Models saved to '{output_dir}/'")


def load_models(models_dir='models'):
    """Load trained models"""
    segmentation = joblib.load(f'{models_dir}/segmentation_model.pkl')
    anomaly_detector = joblib.load(f'{models_dir}/anomaly_detector.pkl')
    feature_analyzer = joblib.load(f'{models_dir}/feature_analyzer.pkl')
    
    print(f"✓ Models loaded from '{models_dir}/'")
    return segmentation, anomaly_detector, feature_analyzer


if __name__ == "__main__":
    # Train models on processed data
    print("="*60)
    print("Training ML Models: Segmentation & Anomaly Detection")
    print("="*60)
    
    # Load processed data
    df = pd.read_csv('data/processed_prospects.csv')
    print(f"\nLoaded {len(df)} processed prospects")
    
    # 1. Segmentation
    segmentation = ProspectSegmentation(n_clusters=5)
    df['segment'] = segmentation.train_segmentation(df)
    
    # 2. Anomaly Detection
    anomaly_detector = AnomalyDetector(contamination=0.05)
    df = anomaly_detector.detect_anomalies(df)
    
    # Show some anomalies
    anomalies = anomaly_detector.get_anomalies(df, top_n=10)
    print("\n🔍 Top 10 Anomalous Prospects:")
    for idx, row in anomalies.head(10).iterrows():
        explanations = anomaly_detector.explain_anomaly(row, df)
        print(f"\nID {row['id']}: {row['first_name']} {row['last_name']}")
        print(f"  Score: {row['priority_score']:.1f}")
        print(f"  Why unusual: {', '.join(explanations)}")
    
    # 3. Feature Analysis
    feature_analyzer = FeatureAnalyzer()
    feature_analyzer.analyze_feature_importance(df)
    
    # Save models
    save_models(segmentation, anomaly_detector, feature_analyzer)
    
    # Save updated data with segments and anomaly flags
    df.to_csv('data/processed_prospects.csv', index=False)
    print(f"\n✓ Updated data saved with segments and anomaly flags")
    
    print("\n" + "="*60)
    print("Model Training Complete!")
    print("="*60)
