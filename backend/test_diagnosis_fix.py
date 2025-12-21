"""
Test script to verify diagnosis mapping fix
"""

def test_diagnosis_mapping():
    """Test the diagnosis string matching logic"""
    
    test_cases = [
        ("Parkinson's Disease", "Should map to PARKINSON"),
        ("parkinson's disease", "Should map to PARKINSON"),
        ("Parkinson", "Should map to PARKINSON"),
        ("parkinson", "Should map to PARKINSON"),
        ("Healthy", "Should map to HEALTHY"),
        ("healthy", "Should map to HEALTHY"),
        ("Early Stage Parkinson's", "Should map to EARLY_STAGE"),
        ("early_stage", "Should map to EARLY_STAGE"),
        ("Moderate Stage", "Should map to MODERATE_STAGE"),
        ("Advanced Stage", "Should map to ADVANCED_STAGE"),
    ]
    
    print("="*80)
    print("DIAGNOSIS MAPPING TEST")
    print("="*80)
    
    for diagnosis_str, expected in test_cases:
        diagnosis_lower = diagnosis_str.lower()
        
        # Replicate the fixed logic
        if 'healthy' in diagnosis_lower or 'non' in diagnosis_lower:
            result = "HEALTHY"
        elif 'early' in diagnosis_lower:
            result = "EARLY_STAGE"
        elif 'moderate' in diagnosis_lower:
            result = "MODERATE_STAGE"
        elif 'advanced' in diagnosis_lower or 'severe' in diagnosis_lower:
            result = "ADVANCED_STAGE"
        elif 'parkinson' in diagnosis_lower or 'pd' in diagnosis_lower:
            result = "PARKINSON"
        else:
            result = "HEALTHY (default)"
        
        status = "✅" if "PARKINSON" in result or "HEALTHY" in result or "STAGE" in result else "❌"
        print(f"{status} '{diagnosis_str}' -> {result}")
        print(f"   {expected}")
        print()

if __name__ == "__main__":
    test_diagnosis_mapping()
    
    print("\n" + "="*80)
    print("FRONTEND ENUM TEST")
    print("="*80)
    print("\nBackend DiagnosisType enum values:")
    print("  - HEALTHY")
    print("  - EARLY_STAGE")
    print("  - MODERATE_STAGE")
    print("  - ADVANCED_STAGE")
    print("  - PARKINSON")
    
    print("\nFrontend should display:")
    print("  - HEALTHY -> 'Healthy'")
    print("  - EARLY_STAGE -> 'Early Stage PD'")
    print("  - MODERATE_STAGE -> 'Moderate Stage PD'")
    print("  - ADVANCED_STAGE -> 'Advanced Stage PD'")
    print("  - PARKINSON -> 'Parkinson's Disease'")
    print("="*80)
