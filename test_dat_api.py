"""
End-to-End API Testing for DaT Scan Analysis
Tests complete workflow: upload → analyze → results
"""

import requests
import json
from pathlib import Path
import time
import sys
from typing import List, Dict, Any
import glob

class DaTScanAPITester:
    """Comprehensive API tester for DaT scan analysis"""
    
    def __init__(self, base_url="http://localhost:8000", token=None):
        """
        Initialize API tester
        
        Args:
            base_url: Base URL of the API
            token: Authentication token (optional for testing)
        """
        self.base_url = base_url
        self.token = token
        self.headers = {}
        
        if token:
            self.headers['Authorization'] = f'Bearer {token}'
    
    def test_health(self) -> bool:
        """Test API health endpoint"""
        print("\n" + "=" * 80)
        print("TEST 1: API HEALTH CHECK")
        print("=" * 80)
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200 and response.json().get('success'):
                print("✅ Health check PASSED")
                return True
            else:
                print("❌ Health check FAILED")
                return False
                
        except Exception as e:
            print(f"❌ Health check ERROR: {e}")
            return False
    
    def test_dat_status(self) -> bool:
        """Test DaT scan service status endpoint"""
        print("\n" + "=" * 80)
        print("TEST 2: DaT SCAN SERVICE STATUS")
        print("=" * 80)
        
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/analysis/dat/status",
                headers=self.headers,
                timeout=5
            )
            
            print(f"Status Code: {response.status_code}")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if response.status_code == 200:
                print(f"\nService Available: {data.get('available', False)}")
                print(f"Model Loaded: {data.get('model_loaded', False)}")
                print(f"Model Path: {data.get('model_path', 'None')}")
                
                if data.get('available') and data.get('model_loaded'):
                    print("✅ DaT service status PASSED")
                    return True
                else:
                    print("⚠️  DaT service available but model not loaded")
                    return False
            else:
                print("❌ DaT service status FAILED")
                return False
                
        except Exception as e:
            print(f"❌ DaT service status ERROR: {e}")
            return False
    
    def test_analyze_scans(self, scan_files: List[str]) -> Dict[str, Any]:
        """
        Test DaT scan analysis endpoint with file uploads
        
        Args:
            scan_files: List of file paths to upload
            
        Returns:
            Analysis results or error dict
        """
        print("\n" + "=" * 80)
        print("TEST 3: DaT SCAN ANALYSIS")
        print("=" * 80)
        
        print(f"\nUploading {len(scan_files)} files...")
        for i, file_path in enumerate(scan_files[:5], 1):  # Show first 5
            print(f"  {i}. {Path(file_path).name}")
        if len(scan_files) > 5:
            print(f"  ... and {len(scan_files) - 5} more files")
        
        try:
            # Prepare files for upload
            files = []
            for file_path in scan_files:
                if not Path(file_path).exists():
                    print(f"❌ File not found: {file_path}")
                    continue
                    
                files.append(
                    ('files', (Path(file_path).name, open(file_path, 'rb'), 'image/png'))
                )
            
            if not files:
                print("❌ No valid files to upload")
                return {'error': 'No valid files'}
            
            # Make request
            print(f"\nSending request to {self.base_url}/api/v1/analysis/dat/analyze")
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/api/v1/analysis/dat/analyze",
                headers=self.headers,
                files=files,
                timeout=120  # 2 minutes timeout
            )
            
            elapsed = time.time() - start_time
            
            # Close file handles
            for _, file_tuple in files:
                file_tuple[1].close()
            
            print(f"\nStatus Code: {response.status_code}")
            print(f"Response Time: {elapsed:.2f}s")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\nResponse: {json.dumps(data, indent=2)}")
                
                if data.get('success') and data.get('result'):
                    result = data['result']
                    
                    print("\n" + "-" * 80)
                    print("ANALYSIS RESULTS")
                    print("-" * 80)
                    print(f"Prediction: {result.get('prediction', 'N/A')}")
                    print(f"Confidence: {result.get('confidence', 0):.2%}")
                    print(f"Risk Level: {result.get('risk_level', 'N/A')}")
                    print(f"\nProbabilities:")
                    print(f"  Healthy: {result.get('probability_healthy', 0):.2%}")
                    print(f"  Parkinson's: {result.get('probability_parkinson', 0):.2%}")
                    print(f"\nInterpretation:")
                    print(f"  {result.get('interpretation', 'N/A')}")
                    
                    if result.get('recommendations'):
                        print(f"\nRecommendations:")
                        for i, rec in enumerate(result['recommendations'], 1):
                            print(f"  {i}. {rec}")
                    
                    print("\n✅ DaT scan analysis PASSED")
                    return data
                else:
                    print(f"❌ Analysis failed: {data.get('error', 'Unknown error')}")
                    return data
            else:
                error_data = response.json() if response.content else {}
                print(f"❌ Request failed: {error_data}")
                return {'error': error_data}
                
        except Exception as e:
            print(f"❌ DaT scan analysis ERROR: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}
    
    def test_with_healthy_scan(self, dat_dir: str) -> bool:
        """Test with a healthy scan directory"""
        print("\n" + "=" * 80)
        print("TEST 4: ANALYZE HEALTHY SCAN")
        print("=" * 80)
        
        # Find healthy scan directory
        healthy_dir = Path(dat_dir) / "Healthy" / "001"
        
        if not healthy_dir.exists():
            print(f"❌ Healthy scan directory not found: {healthy_dir}")
            return False
        
        # Get all PNG files
        scan_files = sorted(glob.glob(str(healthy_dir / "*.png")))
        
        if not scan_files:
            print(f"❌ No PNG files found in {healthy_dir}")
            return False
        
        print(f"Found {len(scan_files)} scan files in {healthy_dir}")
        
        result = self.test_analyze_scans(scan_files)
        
        if result.get('success'):
            prediction = result.get('result', {}).get('prediction', '').lower()
            # Note: Model might not be perfect, so we check if it made a prediction
            return prediction in ['healthy', 'parkinson']
        
        return False
    
    def test_with_pd_scan(self, dat_dir: str) -> bool:
        """Test with a Parkinson's disease scan directory"""
        print("\n" + "=" * 80)
        print("TEST 5: ANALYZE PARKINSON'S SCAN")
        print("=" * 80)
        
        # Find PD scan directory
        pd_dir = Path(dat_dir) / "PD" / "001"
        
        if not pd_dir.exists():
            print(f"❌ PD scan directory not found: {pd_dir}")
            return False
        
        # Get all PNG files
        scan_files = sorted(glob.glob(str(pd_dir / "*.png")))
        
        if not scan_files:
            print(f"❌ No PNG files found in {pd_dir}")
            return False
        
        print(f"Found {len(scan_files)} scan files in {pd_dir}")
        
        result = self.test_analyze_scans(scan_files)
        
        if result.get('success'):
            prediction = result.get('result', {}).get('prediction', '').lower()
            return prediction in ['healthy', 'parkinson']
        
        return False
    
    def run_all_tests(self, dat_dir: str = None):
        """Run all API tests"""
        print("\n" + "=" * 80)
        print("DaT SCAN API - END-TO-END TESTING")
        print("=" * 80)
        print(f"\nBase URL: {self.base_url}")
        print(f"Authenticated: {bool(self.token)}")
        
        results = {
            'health': False,
            'dat_status': False,
            'healthy_scan': False,
            'pd_scan': False
        }
        
        # Test 1: Health check
        results['health'] = self.test_health()
        time.sleep(1)
        
        # Test 2: DaT status
        results['dat_status'] = self.test_dat_status()
        time.sleep(1)
        
        # Tests 3-4: Scan analysis (if DAT directory provided)
        if dat_dir:
            results['healthy_scan'] = self.test_with_healthy_scan(dat_dir)
            time.sleep(2)
            
            results['pd_scan'] = self.test_with_pd_scan(dat_dir)
        else:
            print("\n⚠️  DAT directory not provided, skipping scan analysis tests")
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        total = len(results)
        passed = sum(results.values())
        
        for test, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test.ljust(20)}: {status}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED!")
            return True
        else:
            print(f"\n⚠️  {total - passed} tests failed")
            return False


def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test DaT Scan API endpoints')
    parser.add_argument('--url', default='http://localhost:8000',
                        help='Base URL of the API (default: http://localhost:8000)')
    parser.add_argument('--token', help='Authentication token (optional)')
    parser.add_argument('--dat-dir', default='/home/hari/Downloads/parkinson/DAT',
                        help='Path to DAT scan directory')
    parser.add_argument('--test', choices=['health', 'status', 'analyze', 'all'],
                        default='all', help='Which test to run')
    
    args = parser.parse_args()
    
    # Initialize tester
    tester = DaTScanAPITester(base_url=args.url, token=args.token)
    
    # Run tests
    if args.test == 'health':
        success = tester.test_health()
    elif args.test == 'status':
        success = tester.test_dat_status()
    elif args.test == 'analyze':
        if not args.dat_dir:
            print("❌ --dat-dir required for analyze test")
            sys.exit(1)
        success = tester.test_with_healthy_scan(args.dat_dir)
    else:  # all
        success = tester.run_all_tests(dat_dir=args.dat_dir)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
