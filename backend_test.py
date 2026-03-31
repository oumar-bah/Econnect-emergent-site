#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime, timedelta

class VTCAPITester:
    def __init__(self, base_url="https://driver-platform-28.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.admin_token = None
        self.client_token = None
        self.driver_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.passed_tests = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            self.passed_tests.append(name)
            print(f"✅ {name}")
        else:
            self.failed_tests.append({"test": name, "details": details})
            print(f"❌ {name} - {details}")

    def make_request(self, method, endpoint, data=None, use_admin=False, use_client=False, use_driver=False):
        """Make API request with proper authentication"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        # Add authentication if needed
        if use_admin and self.admin_token:
            headers['Authorization'] = f'Bearer {self.admin_token}'
        elif use_client and self.client_token:
            headers['Authorization'] = f'Bearer {self.client_token}'
        elif use_driver and self.driver_token:
            headers['Authorization'] = f'Bearer {self.driver_token}'

        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers)
            
            return response
        except Exception as e:
            print(f"Request failed: {str(e)}")
            return None

    def test_root_endpoint(self):
        """Test root API endpoint"""
        response = self.make_request('GET', '')
        success = response and response.status_code == 200
        details = f"Status: {response.status_code if response else 'No response'}"
        self.log_test("Root API endpoint", success, details)
        return success

    def test_admin_login(self):
        """Test admin login"""
        data = {
            "email": "admin@econnect-vtc.com",
            "password": "admin123"
        }
        response = self.make_request('POST', 'auth/login', data)
        
        if response and response.status_code == 200:
            try:
                user_data = response.json()
                if user_data.get('role') == 'admin':
                    # Extract token from cookies if available
                    if 'access_token' in response.cookies:
                        self.admin_token = response.cookies['access_token']
                    self.log_test("Admin login", True)
                    return True
                else:
                    self.log_test("Admin login", False, f"Wrong role: {user_data.get('role')}")
                    return False
            except:
                self.log_test("Admin login", False, "Invalid JSON response")
                return False
        else:
            details = f"Status: {response.status_code if response else 'No response'}"
            if response:
                try:
                    error_detail = response.json().get('detail', 'Unknown error')
                    details += f", Error: {error_detail}"
                except:
                    pass
            self.log_test("Admin login", False, details)
            return False

    def test_client_registration(self):
        """Test client registration"""
        timestamp = datetime.now().strftime("%H%M%S")
        data = {
            "email": f"testclient{timestamp}@test.com",
            "password": "testpass123",
            "name": f"Test Client {timestamp}",
            "phone": "0612345678"
        }
        response = self.make_request('POST', 'auth/register', data)
        
        if response and response.status_code == 200:
            try:
                user_data = response.json()
                if user_data.get('role') == 'client':
                    # Extract token from cookies if available
                    if 'access_token' in response.cookies:
                        self.client_token = response.cookies['access_token']
                    self.log_test("Client registration", True)
                    return True
                else:
                    self.log_test("Client registration", False, f"Wrong role: {user_data.get('role')}")
                    return False
            except:
                self.log_test("Client registration", False, "Invalid JSON response")
                return False
        else:
            details = f"Status: {response.status_code if response else 'No response'}"
            if response:
                try:
                    error_detail = response.json().get('detail', 'Unknown error')
                    details += f", Error: {error_detail}"
                except:
                    pass
            self.log_test("Client registration", False, details)
            return False

    def test_admin_stats(self):
        """Test admin stats endpoint"""
        response = self.make_request('GET', 'admin/stats', use_admin=True)
        
        if response and response.status_code == 200:
            try:
                stats = response.json()
                required_fields = ['total_bookings', 'pending_bookings', 'total_clients', 'total_drivers']
                if all(field in stats for field in required_fields):
                    self.log_test("Admin stats", True)
                    return True
                else:
                    missing = [f for f in required_fields if f not in stats]
                    self.log_test("Admin stats", False, f"Missing fields: {missing}")
                    return False
            except:
                self.log_test("Admin stats", False, "Invalid JSON response")
                return False
        else:
            details = f"Status: {response.status_code if response else 'No response'}"
            self.log_test("Admin stats", False, details)
            return False

    def test_admin_bookings(self):
        """Test admin bookings endpoint"""
        response = self.make_request('GET', 'admin/bookings', use_admin=True)
        
        success = response and response.status_code == 200
        details = f"Status: {response.status_code if response else 'No response'}"
        if success:
            try:
                bookings = response.json()
                if isinstance(bookings, list):
                    details += f", Found {len(bookings)} bookings"
                else:
                    success = False
                    details += ", Response is not a list"
            except:
                success = False
                details += ", Invalid JSON response"
        
        self.log_test("Admin bookings list", success, details)
        return success

    def test_admin_drivers(self):
        """Test admin drivers endpoint"""
        response = self.make_request('GET', 'admin/drivers', use_admin=True)
        
        success = response and response.status_code == 200
        details = f"Status: {response.status_code if response else 'No response'}"
        if success:
            try:
                drivers = response.json()
                if isinstance(drivers, list):
                    details += f", Found {len(drivers)} drivers"
                else:
                    success = False
                    details += ", Response is not a list"
            except:
                success = False
                details += ", Invalid JSON response"
        
        self.log_test("Admin drivers list", success, details)
        return success

    def test_admin_clients(self):
        """Test admin clients endpoint"""
        response = self.make_request('GET', 'admin/clients', use_admin=True)
        
        success = response and response.status_code == 200
        details = f"Status: {response.status_code if response else 'No response'}"
        if success:
            try:
                clients = response.json()
                if isinstance(clients, list):
                    details += f", Found {len(clients)} clients"
                else:
                    success = False
                    details += ", Response is not a list"
            except:
                success = False
                details += ", Invalid JSON response"
        
        self.log_test("Admin clients list", success, details)
        return success

    def test_create_driver(self):
        """Test creating a new driver"""
        timestamp = datetime.now().strftime("%H%M%S")
        data = {
            "email": f"driver{timestamp}@test.com",
            "name": f"Test Driver {timestamp}",
            "phone": "0612345678",
            "password": "driverpass123",
            "vehicle_model": "Mercedes Classe E",
            "vehicle_plate": f"AB-{timestamp[-3:]}-CD"
        }
        response = self.make_request('POST', 'admin/drivers', data, use_admin=True)
        
        if response and response.status_code == 200:
            try:
                driver_data = response.json()
                if driver_data.get('role') == 'driver' and driver_data.get('email') == data['email']:
                    self.log_test("Create driver", True)
                    return driver_data
                else:
                    self.log_test("Create driver", False, "Invalid driver data returned")
                    return None
            except:
                self.log_test("Create driver", False, "Invalid JSON response")
                return None
        else:
            details = f"Status: {response.status_code if response else 'No response'}"
            if response:
                try:
                    error_detail = response.json().get('detail', 'Unknown error')
                    details += f", Error: {error_detail}"
                except:
                    pass
            self.log_test("Create driver", False, details)
            return None

    def test_client_booking(self):
        """Test creating a client booking"""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")
        data = {
            "pickup_address": "123 Rue de la Paix, Paris",
            "dropoff_address": "456 Avenue des Champs-Élysées, Paris",
            "pickup_date": tomorrow,
            "pickup_time": "14:30",
            "transfer_type": "simple",
            "notes": "Test booking"
        }
        response = self.make_request('POST', 'bookings', data, use_client=True)
        
        if response and response.status_code == 200:
            try:
                booking_data = response.json()
                if booking_data.get('status') == 'pending':
                    self.log_test("Create client booking", True)
                    return booking_data
                else:
                    self.log_test("Create client booking", False, f"Wrong status: {booking_data.get('status')}")
                    return None
            except:
                self.log_test("Create client booking", False, "Invalid JSON response")
                return None
        else:
            details = f"Status: {response.status_code if response else 'No response'}"
            if response:
                try:
                    error_detail = response.json().get('detail', 'Unknown error')
                    details += f", Error: {error_detail}"
                except:
                    pass
            self.log_test("Create client booking", False, details)
            return None

    def test_client_bookings_list(self):
        """Test client bookings list"""
        response = self.make_request('GET', 'bookings/my', use_client=True)
        
        success = response and response.status_code == 200
        details = f"Status: {response.status_code if response else 'No response'}"
        if success:
            try:
                bookings = response.json()
                if isinstance(bookings, list):
                    details += f", Found {len(bookings)} bookings"
                else:
                    success = False
                    details += ", Response is not a list"
            except:
                success = False
                details += ", Invalid JSON response"
        
        self.log_test("Client bookings list", success, details)
        return success

    def test_auth_me(self):
        """Test auth/me endpoint"""
        response = self.make_request('GET', 'auth/me', use_admin=True)
        
        if response and response.status_code == 200:
            try:
                user_data = response.json()
                if user_data.get('email') == 'admin@econnect-vtc.com':
                    self.log_test("Auth me endpoint", True)
                    return True
                else:
                    self.log_test("Auth me endpoint", False, f"Wrong email: {user_data.get('email')}")
                    return False
            except:
                self.log_test("Auth me endpoint", False, "Invalid JSON response")
                return False
        else:
            details = f"Status: {response.status_code if response else 'No response'}"
            self.log_test("Auth me endpoint", False, details)
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting VTC Backend API Tests...")
        print("=" * 50)
        
        # Test basic connectivity
        if not self.test_root_endpoint():
            print("❌ Basic connectivity failed, stopping tests")
            return False
        
        # Test authentication
        if not self.test_admin_login():
            print("❌ Admin login failed, stopping admin tests")
            return False
        
        # Test admin endpoints
        self.test_admin_stats()
        self.test_admin_bookings()
        self.test_admin_drivers()
        self.test_admin_clients()
        self.test_auth_me()
        
        # Test driver creation
        driver = self.test_create_driver()
        
        # Test client registration and booking
        if self.test_client_registration():
            booking = self.test_client_booking()
            self.test_client_bookings_list()
        
        # Print summary
        print("\n" + "=" * 50)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} passed")
        
        if self.failed_tests:
            print("\n❌ Failed Tests:")
            for test in self.failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        if self.passed_tests:
            print(f"\n✅ Passed Tests: {', '.join(self.passed_tests)}")
        
        return self.tests_passed == self.tests_run

def main():
    tester = VTCAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())