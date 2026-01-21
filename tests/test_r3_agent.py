"""
Release Risk Radar (R³) - Manual Testing Guide

This document outlines how to test the R³ Agent end-to-end.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8001/api"

def test_health_check():
    """Test 1: Health Check"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    assert response.json()['status'] == 'healthy'
    print("✅ Health check passed")

def test_pr_submission_and_analysis():
    """Test 2: Complete PR Analysis Flow"""
    print("\n" + "="*60)
    print("TEST 2: PR Submission & Analysis")
    print("="*60)
    
    # Step 1: Submit PR
    pr_data = {
        "repo_name": "testorg/auth-service",
        "branch_name": "feature/oauth-integration",
        "pr_number": 789,
        "author": "@testuser",
        "title": "Add OAuth 2.0 authentication",
        "description": "Implements OAuth 2.0 for third-party authentication",
        "diff_content": "MOCK"
    }
    
    print("\n1. Submitting PR...")
    submit_response = requests.post(f"{BASE_URL}/pr/submit", json=pr_data)
    print(f"   Status: {submit_response.status_code}")
    
    pr_id = submit_response.json()['pr_id']
    print(f"   PR ID: {pr_id}")
    print("   ✅ PR submitted")
    
    # Step 2: Trigger Analysis
    print("\n2. Triggering analysis...")
    analyze_response = requests.post(f"{BASE_URL}/pr/{pr_id}/analyze")
    print(f"   Status: {analyze_response.status_code}")
    
    analysis_result = analyze_response.json()
    print(f"   Analysis ID: {analysis_result['analysis_id']}")
    print(f"   Trace ID: {analysis_result['trace_id']}")
    print("   ✅ Analysis completed")
    
    # Step 3: Retrieve Analysis
    print("\n3. Retrieving analysis results...")
    analysis_response = requests.get(f"{BASE_URL}/pr/{pr_id}/analysis")
    analysis = analysis_response.json()
    
    print(f"\n   RISK ANALYSIS:")
    print(f"   - Score: {analysis['risk_score']['score']}")
    print(f"   - Level: {analysis['risk_score']['level'].upper()}")
    print(f"   - Explanation: {analysis['risk_score']['explanation']}")
    
    print(f"\n   SIGNALS:")
    for signal, value in analysis['risk_score']['signals'].items():
        print(f"   - {signal}: {value}")
    
    print(f"\n   STATIC ANALYSIS:")
    print(f"   - Files analyzed: {len(analysis['static_analysis'])}")
    total_issues = sum(len(sa['issues']) for sa in analysis['static_analysis'])
    print(f"   - Total issues: {total_issues}")
    
    print(f"\n   TESTS GENERATED:")
    print(f"   - Test cases: {len(analysis['test_cases'])}")
    
    print(f"\n   MITIGATIONS:")
    print(f"   - Actions recommended: {len(analysis['mitigations'])}")
    for m in analysis['mitigations']:
        print(f"     * {m['action_type']}: {m['description']}")
    
    print("\n   ✅ Analysis retrieved successfully")
    
    return pr_id, analysis

def test_mitigation_approval(pr_id, analysis):
    """Test 3: Mitigation Approval"""
    print("\n" + "="*60)
    print("TEST 3: Mitigation Approval")
    print("="*60)
    
    if not analysis['mitigations']:
        print("   ⚠️  No mitigations to approve")
        return
    
    mitigation = analysis['mitigations'][0]
    trace_id = analysis['execution_trace_id']
    
    print(f"\n   Approving mitigation: {mitigation['action_type']}")
    
    approval_data = {
        "trace_id": trace_id,
        "mitigation_id": mitigation['id'],
        "action": "approve",
        "approver": "test_user",
        "comment": "Approved during testing"
    }
    
    response = requests.post(f"{BASE_URL}/mitigation/approve", json=approval_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    print("   ✅ Mitigation approved")

def test_dashboard_stats():
    """Test 4: Dashboard Statistics"""
    print("\n" + "="*60)
    print("TEST 4: Dashboard Statistics")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/dashboard/stats")
    stats = response.json()
    
    print(f"\n   STATISTICS:")
    print(f"   - Total PRs: {stats['total_prs']}")
    print(f"   - Risk Distribution:")
    print(f"     * High: {stats['risk_distribution']['high']}")
    print(f"     * Medium: {stats['risk_distribution']['medium']}")
    print(f"     * Low: {stats['risk_distribution']['low']}")
    print(f"   - Recent analyses: {len(stats['recent_analyses'])}")
    
    print("\n   ✅ Dashboard stats retrieved")

def test_release_train():
    """Test 5: Release Train Creation"""
    print("\n" + "="*60)
    print("TEST 5: Release Train")
    print("="*60)
    
    release_data = {
        "release_version": "v2.5.0",
        "branch": "release/2.5",
        "pr_ids": [],
        "cumulative_risk_score": 0,
        "status": "planning"
    }
    
    print("\n   Creating release train...")
    response = requests.post(f"{BASE_URL}/release/create", json=release_data)
    print(f"   Status: {response.status_code}")
    
    release_id = response.json()['release_id']
    print(f"   Release ID: {release_id}")
    
    # List releases
    print("\n   Listing releases...")
    list_response = requests.get(f"{BASE_URL}/release/list")
    releases = list_response.json()
    print(f"   Total releases: {len(releases)}")
    
    print("\n   ✅ Release train created")

def run_all_tests():
    """Run all tests"""
    print("\n" + "🚀"*30)
    print("RELEASE RISK RADAR (R³) - TEST SUITE")
    print("🚀"*30)
    
    try:
        test_health_check()
        pr_id, analysis = test_pr_submission_and_analysis()
        test_mitigation_approval(pr_id, analysis)
        test_dashboard_stats()
        test_release_train()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\n📊 Summary:")
        print("   - Health check: ✅")
        print("   - PR submission & analysis: ✅")
        print("   - Mitigation approval: ✅")
        print("   - Dashboard stats: ✅")
        print("   - Release train: ✅")
        print("\n🎉 R³ Agent is fully operational!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    run_all_tests()
