"""Mitigation recommendation engine"""
from typing import List, Dict, Any
from backend.models import Mitigation, RiskScore
import uuid

class MitigationEngine:
    """Generate mitigation recommendations based on risk level"""
    
    def generate_mitigations(self, risk_score: RiskScore, 
                            pr_data: Dict[str, Any]) -> List[Mitigation]:
        """Generate mitigation plan based on risk level"""
        mitigations = []
        level = risk_score.level
        signals = risk_score.signals
        
        if level == "low":
            mitigations.extend(self._low_risk_mitigations(signals, pr_data))
        elif level == "medium":
            mitigations.extend(self._medium_risk_mitigations(signals, pr_data))
        else:  # high
            mitigations.extend(self._high_risk_mitigations(signals, pr_data))
        
        return mitigations
    
    def _low_risk_mitigations(self, signals, pr_data) -> List[Mitigation]:
        """Low risk: Proceed with normal CI"""
        return [
            Mitigation(
                action_type="ci_run",
                description="Run standard CI pipeline with smoke tests",
                required=True,
                status="draft",
                confidence=0.9
            ),
            Mitigation(
                action_type="review",
                description="Standard code review by one team member",
                required=True,
                status="draft",
                confidence=0.9
            )
        ]
    
    def _medium_risk_mitigations(self, signals, pr_data) -> List[Mitigation]:
        """Medium risk: Enhanced testing and optional canary"""
        mitigations = [
            Mitigation(
                action_type="ci_run",
                description="Run impacted test suite + safety regression tests",
                required=True,
                status="draft",
                confidence=0.85
            )
        ]
        
        # Coverage gap mitigation
        if signals.coverage_gap > 0.4:
            mitigations.append(Mitigation(
                action_type="test_coverage",
                description="Add unit tests for uncovered code paths (target 70% coverage)",
                required=True,
                status="draft",
                confidence=0.8
            ))
        
        # Canary deployment
        if signals.diff_risk > 0.3 or signals.incident_hotspot > 0.3:
            mitigations.append(Mitigation(
                action_type="canary",
                description="Deploy to canary environment for validation (12h)",
                required=False,
                status="draft",
                confidence=0.75
            ))
        
        # Extra review
        mitigations.append(Mitigation(
            action_type="extra_review",
            description="Review by senior engineer or domain expert",
            required=True,
            status="draft",
            confidence=0.85
        ))
        
        return mitigations
    
    def _high_risk_mitigations(self, signals, pr_data) -> List[Mitigation]:
        """High risk: Comprehensive mitigations required"""
        mitigations = [
            Mitigation(
                action_type="ci_run",
                description="Run full test suite in parallel (unit + integration + e2e)",
                required=True,
                status="draft",
                confidence=0.9
            )
        ]
        
        # Mandatory test coverage
        if signals.coverage_gap > 0.3:
            mitigations.append(Mitigation(
                action_type="test_coverage",
                description="Add comprehensive unit tests (target 85% coverage minimum)",
                required=True,
                status="draft",
                confidence=0.85
            ))
        
        # Mandatory canary
        if signals.diff_risk > 0.4 or signals.incident_hotspot > 0.5:
            mitigations.append(Mitigation(
                action_type="canary",
                description="Mandatory canary deployment with monitoring (24h minimum)",
                required=True,
                status="draft",
                confidence=0.9
            ))
        
        # Integration tests for incident hotspots
        if signals.incident_hotspot > 0.4:
            mitigations.append(Mitigation(
                action_type="integration_test",
                description="Run targeted integration tests for previously failed paths",
                required=True,
                status="draft",
                confidence=0.85
            ))
        
        # Multiple reviewers
        mitigations.append(Mitigation(
            action_type="extra_review",
            description="Require 2+ reviewers including domain expert/architect",
            required=True,
            status="draft",
            confidence=0.9
        ))
        
        # Release note
        mitigations.append(Mitigation(
            action_type="documentation",
            description="Add detailed release notes with rollback plan",
            required=True,
            status="draft",
            confidence=0.8
        ))
        
        # Consider blocking
        if signals.time_pressure > 0.5:
            mitigations.append(Mitigation(
                action_type="freeze_exception",
                description="Request freeze exception approval from release manager",
                required=True,
                status="draft",
                confidence=0.75
            ))
        
        return mitigations
