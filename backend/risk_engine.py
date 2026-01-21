"""Risk scoring engine based on R³ methodology"""
import math
from typing import List, Dict, Any
from models import RiskSignals, RiskScore
import re

# Weights for risk formula (tunable)
WEIGHTS = {
    'churn': 0.20,
    'coverage_gap': 0.25,
    'incident_hotspot': 0.20,
    'flake_proximity': 0.15,
    'diff_risk': 0.15,
    'time_pressure': 0.05
}

# Risky paths patterns
RISKY_PATHS = [
    r'payment', r'billing', r'checkout',
    r'auth', r'authentication', r'login',
    r'database', r'migration', r'schema',
    r'security', r'encryption', r'crypto',
    r'infra', r'infrastructure', r'config'
]

class RiskEngine:
    """Calculate risk scores for PRs"""
    
    def __init__(self):
        self.weights = WEIGHTS
        self.risky_paths = RISKY_PATHS
    
    def compute_churn(self, files: List[Dict[str, Any]], recent_hours: int = 72) -> float:
        """Compute normalized code churn"""
        total_changes = sum(f.get('additions', 0) + f.get('deletions', 0) for f in files)
        num_files = len(files)
        
        # Normalize by a reasonable baseline (e.g., 500 lines, 5 files)
        churn_score = min(1.0, (total_changes / 500) * (num_files / 5))
        return round(churn_score, 3)
    
    def compute_coverage_gap(self, files: List[Dict[str, Any]], 
                            coverage_data: Dict[str, float] = None) -> float:
        """Compute coverage gap (1 - coverage)"""
        # MOCK DATA NOTE: Using simulated coverage data
        # TODO: Replace with actual coverage reports from CI
        if not coverage_data:
            # Simulate coverage based on file types and paths
            coverage_data = self._simulate_coverage(files)
        
        if not files:
            return 0.0
        
        total_coverage = sum(coverage_data.get(f.get('file_path', ''), 0.7) for f in files)
        avg_coverage = total_coverage / len(files)
        
        gap = 1.0 - avg_coverage
        return round(gap, 3)
    
    def _simulate_coverage(self, files: List[Dict[str, Any]]) -> Dict[str, float]:
        """Simulate coverage data - MOCK"""
        coverage = {}
        for f in files:
            path = f.get('file_path', '')
            # Lower coverage for risky paths
            if any(re.search(pattern, path, re.IGNORECASE) for pattern in self.risky_paths):
                coverage[path] = 0.4  # Low coverage
            elif 'test' in path.lower():
                coverage[path] = 0.95  # High coverage for tests
            else:
                coverage[path] = 0.75  # Average coverage
        return coverage
    
    def compute_incident_hotspot(self, files: List[Dict[str, Any]], 
                                incident_data: Dict[str, int] = None) -> float:
        """Compute incident hotspot score"""
        # MOCK DATA NOTE: Using simulated incident data
        # TODO: Replace with actual incident tracking from Jira/ServiceNow
        if not incident_data:
            incident_data = self._simulate_incidents(files)
        
        if not files:
            return 0.0
        
        total_incidents = sum(incident_data.get(f.get('file_path', ''), 0) for f in files)
        # Normalize by assuming max 5 incidents per file is high risk
        hotspot_score = min(1.0, total_incidents / (len(files) * 5))
        return round(hotspot_score, 3)
    
    def _simulate_incidents(self, files: List[Dict[str, Any]]) -> Dict[str, int]:
        """Simulate incident data - MOCK"""
        incidents = {}
        for f in files:
            path = f.get('file_path', '')
            # Higher incidents for risky paths
            if any(re.search(pattern, path, re.IGNORECASE) for pattern in self.risky_paths):
                incidents[path] = 3
            else:
                incidents[path] = 0
        return incidents
    
    def compute_flake_proximity(self, files: List[Dict[str, Any]], 
                               flake_data: Dict[str, float] = None) -> float:
        """Compute flake proximity (historical failure rate)"""
        # MOCK DATA NOTE: Using simulated flake data
        # TODO: Replace with actual test flake history from CI
        if not flake_data:
            flake_data = self._simulate_flakes(files)
        
        if not files:
            return 0.0
        
        total_flake = sum(flake_data.get(f.get('file_path', ''), 0) for f in files)
        avg_flake = total_flake / len(files)
        return round(avg_flake, 3)
    
    def _simulate_flakes(self, files: List[Dict[str, Any]]) -> Dict[str, float]:
        """Simulate flake data - MOCK"""
        flakes = {}
        for f in files:
            path = f.get('file_path', '')
            # Higher flake rate for integration tests and complex modules
            if 'integration' in path.lower() or 'e2e' in path.lower():
                flakes[path] = 0.3
            elif any(re.search(pattern, path, re.IGNORECASE) for pattern in self.risky_paths):
                flakes[path] = 0.2
            else:
                flakes[path] = 0.05
        return flakes
    
    def compute_diff_risk(self, files: List[Dict[str, Any]]) -> float:
        """Compute risk based on risky directories and patterns"""
        if not files:
            return 0.0
        
        risky_files = 0
        for f in files:
            path = f.get('file_path', '')
            if any(re.search(pattern, path, re.IGNORECASE) for pattern in self.risky_paths):
                risky_files += 1
        
        risk_ratio = risky_files / len(files)
        return round(risk_ratio, 3)
    
    def compute_time_pressure(self, commit_time: str = None, 
                            is_stacked: bool = False,
                            is_near_freeze: bool = False) -> float:
        """Compute time pressure score"""
        # MOCK DATA NOTE: Using heuristics
        # TODO: Integrate with release calendar and commit timestamps
        score = 0.0
        
        if is_near_freeze:
            score += 0.5
        
        if is_stacked:
            score += 0.3
        
        # Check if weekend or night commit (would need actual timestamp)
        # For now, use mock value
        score += 0.1
        
        return round(min(1.0, score), 3)
    
    def calculate_risk_score(self, signals: RiskSignals) -> RiskScore:
        """Calculate overall risk score using weighted formula"""
        # R = w1*churn + w2*coverage_gap + w3*incident_hotspot + 
        #     w4*flake_proximity + w5*diff_risk + w6*time_pressure
        
        score = (
            self.weights['churn'] * signals.churn +
            self.weights['coverage_gap'] * signals.coverage_gap +
            self.weights['incident_hotspot'] * signals.incident_hotspot +
            self.weights['flake_proximity'] * signals.flake_proximity +
            self.weights['diff_risk'] * signals.diff_risk +
            self.weights['time_pressure'] * signals.time_pressure
        )
        
        # Determine level
        if score < 0.3:
            level = "low"
        elif score < 0.6:
            level = "medium"
        else:
            level = "high"
        
        # Generate explanation
        explanation = self._generate_explanation(signals, score, level)
        citations = self._generate_citations(signals)
        
        return RiskScore(
            score=round(score, 3),
            level=level,
            signals=signals,
            explanation=explanation,
            citations=citations,
            confidence=0.78
        )
    
    def _generate_explanation(self, signals: RiskSignals, score: float, level: str) -> str:
        """Generate human-readable explanation"""
        parts = [f"Risk: {level.upper()} ({score:.2f})."]
        
        reasons = []
        if signals.churn > 0.5:
            reasons.append("high code churn")
        if signals.coverage_gap > 0.5:
            reasons.append(f"low coverage ({(1-signals.coverage_gap)*100:.0f}%)")
        if signals.incident_hotspot > 0.3:
            reasons.append("incident-prone paths")
        if signals.flake_proximity > 0.2:
            reasons.append("flaky tests nearby")
        if signals.diff_risk > 0.3:
            reasons.append("changes in critical paths (auth/payment/infra)")
        if signals.time_pressure > 0.3:
            reasons.append("time pressure (near freeze/stacked)")
        
        if reasons:
            parts.append("Why: " + ", ".join(reasons) + ".")
        
        return " ".join(parts)
    
    def _generate_citations(self, signals: RiskSignals) -> List[str]:
        """Generate citations for risk score"""
        citations = []
        
        # MOCK DATA NOTE: These are simulated citations
        # TODO: Replace with actual commit hashes, CI run IDs, ticket numbers
        if signals.churn > 0.3:
            citations.append("commit:abc123")
        if signals.coverage_gap > 0.3:
            citations.append("coverage-report:#412")
        if signals.incident_hotspot > 0.2:
            citations.append("incident:INC-231")
        if signals.flake_proximity > 0.2:
            citations.append("ci-runs:#319102,#319098")
        
        return citations
    
    def compute_signals(self, pr_data: Dict[str, Any]) -> RiskSignals:
        """Compute all risk signals from PR data"""
        files = pr_data.get('files', [])
        
        return RiskSignals(
            churn=self.compute_churn(files),
            coverage_gap=self.compute_coverage_gap(files),
            incident_hotspot=self.compute_incident_hotspot(files),
            flake_proximity=self.compute_flake_proximity(files),
            diff_risk=self.compute_diff_risk(files),
            time_pressure=self.compute_time_pressure(
                is_near_freeze=pr_data.get('is_near_freeze', False),
                is_stacked=pr_data.get('is_stacked', False)
            )
        )
