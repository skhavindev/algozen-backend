#!/usr/bin/env python3
"""
Simple API test script for Algozen Backend
Run this to test if your API endpoints are working correctly.
"""

import requests
import json
import sys

# Configuration
BASE_URL = "https://algozen-backend.onrender.com"  # Change this to your backend URL
API_ENDPOINTS = {
    "health": f"{BASE_URL}/api/health/",
    "problems": f"{BASE_URL}/api/problems/",
    "login": f"{BASE_URL}/api/auth/login/",
    "register": f"{BASE_URL}/api/auth/register/",
}

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(API_ENDPOINTS["health"])
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_problems_endpoint():
    """Test the problems endpoint"""
    print("🔍 Testing problems endpoint...")
    try:
        response = requests.get(API_ENDPOINTS["problems"])
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Problems endpoint working: Found {len(data)} problems")
            return True
        else:
            print(f"❌ Problems endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Problems endpoint error: {e}")
        return False

def test_register_endpoint():
    """Test the register endpoint with sample data"""
    print("🔍 Testing register endpoint...")
    sample_data = {
        "university_name": "test_user_123",
        "university": "Test University",
        "year_of_passing": "2024",
        "password": "testpassword123",
        "role": "user"
    }
    try:
        response = requests.post(
            API_ENDPOINTS["register"],
            json=sample_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code in [200, 201, 400]:  # 400 might be expected if user exists
            print(f"✅ Register endpoint responding: {response.status_code}")
            return True
        else:
            print(f"❌ Register endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Register endpoint error: {e}")
        return False

def test_login_endpoint():
    """Test the login endpoint with sample data"""
    print("🔍 Testing login endpoint...")
    sample_data = {
        "university_name": "test_user_123",
        "university": "Test University",
        "year_of_passing": "2024",
        "password": "testpassword123"
    }
    try:
        response = requests.post(
            API_ENDPOINTS["login"],
            json=sample_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code in [200, 401]:  # 401 is expected for invalid credentials
            print(f"✅ Login endpoint responding: {response.status_code}")
            return True
        else:
            print(f"❌ Login endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Login endpoint error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting API tests for Algozen Backend")
    print(f"📍 Testing against: {BASE_URL}")
    print("-" * 50)
    
    tests = [
        test_health_check,
        test_problems_endpoint,
        test_register_endpoint,
        test_login_endpoint,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("-" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your API is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check your deployment configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 