#!/usr/bin/env python3
"""
Piso WiFi Stress Test Tool - Custom Portal Edition
Specifically designed for portal: http://10.0.0.1/client?page=dashboard
"""

import requests
import threading
import time
import json
import random
from datetime import datetime
import argparse
from queue import Queue
from multiprocessing import Process, Manager, Lock
import urllib.parse

class PisoWiFiCustomTester:
    def __init__(self, portal_ip: str, num_users: int = 1000, 
                 user_id: int = 0, total_users: int = 1):
        """
        Initialize Piso WiFi tester for specific portal structure
        
        Args:
            portal_ip: IP address of Piso WiFi portal
            num_users: Number of concurrent users to simulate
            user_id: Unique ID for this test instance
            total_users: Total number of concurrent test instances
        """
        self.portal_ip = portal_ip
        self.base_url = f"http://{portal_ip}"
        self.num_users = num_users
        self.user_id = user_id
        self.total_users = total_users
        
        # Portal specific endpoints
        self.endpoints = {
            'dashboard': '/client?page=dashboard',
            'login': '/client?page=login',
            'voucher': '/client?page=voucher',
            'coin': '/client?page=coin',
            'status': '/client?page=status',
            'logout': '/client?page=logout',
        }
        
        # Statistics
        self.stats = {
            'total_attempts': 0,
            'coin_insertions': 0,
            'voucher_logins': 0,
            'direct_logins': 0,
            'successful_logins': 0,
            'failed_logins': 0,
            'page_access_success': 0,
            'page_access_failed': 0
        }
        self.lock = threading.Lock()
        
        # Results storage
        self.results = []
        
        # User range for this instance
        self.user_start = user_id * num_users
        self.user_end = (user_id + 1) * num_users
        
        print(f"[Instance {user_id}] User range: {self.user_start} to {self.user_end-1}")
        
        # Test portal connectivity
        self.test_portal_connection()
    
    def test_portal_connection(self):
        """Test connection to the portal"""
        print(f"[Instance {self.user_id}] Testing portal connection...")
        
        for page_name, endpoint in self.endpoints.items():
            url = f"{self.base_url}{endpoint}"
            try:
                response = requests.get(url, timeout=5, verify=False)
                if response.status_code == 200:
                    print(f"  ✓ {page_name}: {url} (Status: {response.status_code})")
                    
                    # Check for INSERT COIN message
                    if 'insert coin' in response.text.lower():
                        print(f"     Found 'INSERT COIN' on {page_name} page")
                    
                    # Check for login forms
                    if '<form' in response.text.lower():
                        print(f"     Found form on {page_name} page")
                        
                else:
                    print(f"  ✗ {page_name}: {url} (Status: {response.status_code})")
                    
            except Exception as e:
                print(f"  ✗ {page_name}: {url} (Error: {str(e)[:50]})")
    
    def generate_user_info(self, user_id: int):
        """Generate user information"""
        return {
            "user_id": user_id,
            "username": f"user{user_id:08d}",
            "password": f"pass{user_id:08d}",
            "voucher": f"VOUCH{random.randint(10000, 99999)}",
            "mac": f"02:{random.randint(0,255):02X}:{random.randint(0,255):02X}:"
                   f"{random.randint(0,255):02X}:{random.randint(0,255):02X}:{random.randint(0,255):02X}",
            "coin_amount": random.choice([1, 5, 10, 20]),
            "device": random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
                "Mozilla/5.0 (Android 11; Mobile; rv:91.0) Gecko/91.0 Firefox/91.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            ]),
            "session_id": f"sess{random.randint(100000, 999999)}"
        }
    
    def access_dashboard(self, user_info):
        """Access the dashboard page"""
        url = f"{self.base_url}{self.endpoints['dashboard']}"
        headers = {
            'User-Agent': user_info['device'],
            'X-Forwarded-For': user_info['mac'].replace(':', '.'),
            'Referer': self.base_url
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=5, verify=False)
            return response.status_code, response.text
        except Exception as e:
            return 0, str(e)
    
    def simulate_coin_insertion(self, user_info):
        """Simulate coin insertion on the coin page"""
        url = f"{self.base_url}{self.endpoints['coin']}"
        
        # Common coin insertion parameters
        coin_data = {
            'mac': user_info['mac'],
            'amount': str(user_info['coin_amount']),
            'time': str(int(time.time())),
            'action': 'insert_coin',
            'device': 'coin_slot_1',
            'session': user_info['session_id']
        }
        
        headers = {
            'User-Agent': user_info['device'],
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': f"{self.base_url}{self.endpoints['dashboard']}"
        }
        
        try:
            response = requests.post(
                url,
                data=coin_data,
                headers=headers,
                timeout=5,
                verify=False
            )
            
            if response.status_code == 200:
                # Check for success indicators
                response_text = response.text.lower()
                if any(keyword in response_text for keyword in 
                       ['success', 'accepted', 'inserted', 'credited', 'thank you']):
                    return True, "Coin inserted successfully"
                elif 'json' in response.headers.get('content-type', ''):
                    # Try to parse as JSON
                    try:
                        json_data = response.json()
                        if json_data.get('status') == 'success':
                            return True, "Coin inserted (JSON success)"
                    except:
                        pass
            return False, f"Failed with status {response.status_code}"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def attempt_voucher_login(self, user_info):
        """Attempt voucher login"""
        url = f"{self.base_url}{self.endpoints['voucher']}"
        
        voucher_data = {
            'voucher_code': user_info['voucher'],
            'mac': user_info['mac'],
            'submit': '1',
            'action': 'redeem_voucher'
        }
        
        headers = {
            'User-Agent': user_info['device'],
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': f"{self.base_url}{self.endpoints['dashboard']}"
        }
        
        try:
            response = requests.post(
                url,
                data=voucher_data,
                headers=headers,
                timeout=5,
                verify=False
            )
            
            if response.status_code == 200:
                response_text = response.text.lower()
                if any(keyword in response_text for keyword in 
                       ['success', 'redeemed', 'accepted', 'connected', 'welcome']):
                    return True, "Voucher accepted"
                elif 'invalid' in response_text or 'failed' in response_text:
                    return False, "Voucher invalid"
            
            return False, f"Status {response.status_code}"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def attempt_direct_login(self, user_info):
        """Attempt direct login with username/password"""
        url = f"{self.base_url}{self.endpoints['login']}"
        
        login_data = {
            'username': user_info['username'],
            'password': user_info['password'],
            'mac': user_info['mac'],
            'submit': 'Login',
            'action': 'login'
        }
        
        headers = {
            'User-Agent': user_info['device'],
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': f"{self.base_url}{self.endpoints['dashboard']}"
        }
        
        try:
            response = requests.post(
                url,
                data=login_data,
                headers=headers,
                timeout=5,
                verify=False
            )
            
            if response.status_code == 200:
                response_text = response.text.lower()
                if any(keyword in response_text for keyword in 
                       ['success', 'welcome', 'logged in', 'connected']):
                    return True, "Login successful"
                elif '302' in response_text or 'location:' in response.headers:
                    return True, "Login successful (redirect)"
            
            return False, f"Status {response.status_code}"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def check_connection_status(self, user_info):
        """Check if user is connected"""
        url = f"{self.base_url}{self.endpoints['status']}"
        
        headers = {
            'User-Agent': user_info['device'],
            'X-Client-MAC': user_info['mac']
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=5, verify=False)
            
            if response.status_code == 200:
                response_text = response.text.lower()
                if any(keyword in response_text for keyword in 
                       ['connected', 'online', 'active', 'authenticated']):
                    return True, "User is connected"
                elif any(keyword in response_text for keyword in 
                         ['disconnected', 'offline', 'expired', 'unauthorized']):
                    return False, "User is not connected"
            
            return False, f"Status {response.status_code}"
            
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def test_user_flow(self, global_user_id: int):
        """Test complete user flow on the portal"""
        user_info = self.generate_user_info(global_user_id)
        session = requests.Session()
        
        result = {
            'user_id': global_user_id,
            'instance_id': self.user_id,
            'mac': user_info['mac'],
            'steps': [],
            'status': 'INITIALIZED',
            'coin_inserted': False,
            'voucher_used': False,
            'login_success': False,
            'connected': False
        }
        
        try:
            print(f"[User {global_user_id:08d}] Starting test...")
            
            # Step 1: Access dashboard
            step1_status, step1_content = self.access_dashboard(user_info)
            result['steps'].append(('dashboard_access', step1_status))
            
            if step1_status != 200:
                result['status'] = 'DASHBOARD_FAILED'
                return result
            
            with self.lock:
                self.stats['page_access_success'] += 1
            
            # Step 2: Check for INSERT COIN message
            if 'insert coin' in step1_content.lower():
                print(f"[User {global_user_id:08d}] INSERT COIN detected, simulating coin insertion...")
                
                # Step 3: Simulate coin insertion
                coin_success, coin_message = self.simulate_coin_insertion(user_info)
                result['steps'].append(('coin_insertion', coin_success, coin_message))
                
                if coin_success:
                    with self.lock:
                        self.stats['coin_insertions'] += 1
                    result['coin_inserted'] = True
                    print(f"[User {global_user_id:08d}] Coin inserted successfully")
                    
                    # Wait for coin processing
                    time.sleep(random.uniform(0.1, 0.5))
                    
                    # Step 4: Try voucher login after coin
                    voucher_success, voucher_message = self.attempt_voucher_login(user_info)
                    result['steps'].append(('voucher_login', voucher_success, voucher_message))
                    
                    if voucher_success:
                        with self.lock:
                            self.stats['voucher_logins'] += 1
                        result['voucher_used'] = True
                        print(f"[User {global_user_id:08d}] Voucher login successful")
                    else:
                        # Try direct login if voucher fails
                        login_success, login_message = self.attempt_direct_login(user_info)
                        result['steps'].append(('direct_login', login_success, login_message))
                        
                        if login_success:
                            with self.lock:
                                self.stats['direct_logins'] += 1
                            print(f"[User {global_user_id:08d}] Direct login successful")
                
                else:
                    print(f"[User {global_user_id:08d}] Coin insertion failed: {coin_message}")
                    result['status'] = 'COIN_INSERTION_FAILED'
            
            else:
                # No INSERT COIN, try voucher directly
                print(f"[User {global_user_id:08d}] No INSERT COIN, trying voucher login...")
                
                voucher_success, voucher_message = self.attempt_voucher_login(user_info)
                result['steps'].append(('voucher_login', voucher_success, voucher_message))
                
                if voucher_success:
                    with self.lock:
                        self.stats['voucher_logins'] += 1
                    result['voucher_used'] = True
                    print(f"[User {global_user_id:08d}] Voucher login successful")
                else:
                    # Try direct login
                    login_success, login_message = self.attempt_direct_login(user_info)
                    result['steps'].append(('direct_login', login_success, login_message))
                    
                    if login_success:
                        with self.lock:
                            self.stats['direct_logins'] += 1
                        print(f"[User {global_user_id:08d}] Direct login successful")
            
            # Step 5: Check connection status
            time.sleep(0.5)  # Wait a bit for connection to establish
            connected, connection_message = self.check_connection_status(user_info)
            result['steps'].append(('connection_check', connected, connection_message))
            
            if connected:
                with self.lock:
                    self.stats['successful_logins'] += 1
                result['connected'] = True
                result['login_success'] = True
                result['status'] = 'CONNECTED_SUCCESSFULLY'
                print(f"[User {global_user_id:08d}] ✓ Successfully connected!")
            else:
                with self.lock:
                    self.stats['failed_logins'] += 1
                result['status'] = 'NOT_CONNECTED'
                print(f"[User {global_user_id:08d}] ✗ Failed to connect")
            
        except Exception as e:
            result['status'] = f'ERROR: {str(e)}'
            result['steps'].append(('error', str(e)))
            print(f"[User {global_user_id:08d}] Error: {e}")
        
        # Update statistics
        with self.lock:
            self.stats['total_attempts'] += 1
            
            # Print progress
            if self.stats['total_attempts'] % 10 == 0:
                print(f"[Instance {self.user_id}] Progress: {self.stats['total_attempts']}/{self.num_users} | "
                      f"Connected: {self.stats['successful_logins']} | "
                      f"Coins: {self.stats['coin_insertions']}")
        
        # Store result
        self.results.append(result)
        return result
    
    def run_stress_test(self, threads_per_batch: int = 25):
        """Run the stress test"""
        print(f"\n[Instance {self.user_id}] " + "="*70)
        print(f"[Instance {self.user_id}]     PISO WIFI CUSTOM PORTAL STRESS TEST")
        print(f"[Instance {self.user_id}] " + "="*70)
        print(f"[Instance {self.user_id}] Portal: {self.base_url}{self.endpoints['dashboard']}")
        print(f"[Instance {self.user_id}] Users: {self.num_users:,}")
        print(f"[Instance {self.user_id}] Threads: {threads_per_batch}")
        print(f"[Instance {self.user_id}] Starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[Instance {self.user_id}] " + "-"*70)
        
        start_time = time.time()
        
        # Create work queue
        user_queue = Queue()
        for user_id in range(self.user_start, self.user_end):
            user_queue.put(user_id)
        
        # Worker function
        def worker():
            while not user_queue.empty():
                try:
                    user_id = user_queue.get_nowait()
                    self.test_user_flow(user_id)
                    user_queue.task_done()
                except:
                    break
        
        # Create and start worker threads
        threads = []
        for i in range(threads_per_batch):
            thread = threading.Thread(target=worker)
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        print(f"[Instance {self.user_id}] [STATUS] Running stress test...")
        user_queue.join()
        
        # Wait for threads
        for thread in threads:
            thread.join(timeout=5)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print report
        self.print_detailed_report(duration)
    
    def print_detailed_report(self, duration: float):
        """Print detailed test report"""
        print(f"\n[Instance {self.user_id}] " + "="*70)
        print(f"[Instance {self.user_id}]              TEST COMPLETION REPORT")
        print(f"[Instance {self.user_id}] " + "="*70)
        
        # Statistics
        print(f"\n[Instance {self.user_id}] 📊 TEST STATISTICS:")
        print(f"[Instance {self.user_id}]    Total Users Tested: {self.stats['total_attempts']:,}")
        print(f"[Instance {self.user_id}]    Dashboard Access: {self.stats['page_access_success']:,}")
        print(f"[Instance {self.user_id}]    Coin Insertions: {self.stats['coin_insertions']:,}")
        print(f"[Instance {self.user_id}]    Voucher Logins: {self.stats['voucher_logins']:,}")
        print(f"[Instance {self.user_id}]    Direct Logins: {self.stats['direct_logins']:,}")
        print(f"[Instance {self.user_id}]    Successful Connections: {self.stats['successful_logins']:,}")
        print(f"[Instance {self.user_id}]    Failed Connections: {self.stats['failed_logins']:,}")
        
        if self.stats['total_attempts'] > 0:
            success_rate = (self.stats['successful_logins'] / self.stats['total_attempts']) * 100
            coin_rate = (self.stats['coin_insertions'] / self.stats['total_attempts']) * 100
            print(f"[Instance {self.user_id}]    Connection Success Rate: {success_rate:.2f}%")
            print(f"[Instance {self.user_id}]    Coin Insertion Rate: {coin_rate:.2f}%")
        
        # Performance
        print(f"\n[Instance {self.user_id}] ⚡ PERFORMANCE:")
        print(f"[Instance {self.user_id}]    Total Duration: {duration:.2f} seconds")
        if self.stats['total_attempts'] > 0:
            users_per_second = self.stats['total_attempts'] / duration
            avg_time_per_user = duration / self.stats['total_attempts']
            print(f"[Instance {self.user_id}]    Users per Second: {users_per_second:.2f}")
            print(f"[Instance {self.user_id}]    Avg Time per User: {avg_time_per_user:.2f} seconds")
        
        # Revenue calculation
        total_coins_value = self.stats['coin_insertions'] * 5  # Assuming ₱5 average
        print(f"\n[Instance {self.user_id}] 💰 SIMULATED REVENUE:")
        print(f"[Instance {self.user_id}]    Total Coins Inserted: {self.stats['coin_insertions']:,}")
        print(f"[Instance {self.user_id}]    Estimated Revenue: ₱{total_coins_value:,}")
        
        # Result breakdown
        print(f"\n[Instance {self.user_id}] 📈 RESULT BREAKDOWN:")
        status_counts = {}
        for result in self.results:
            status = result['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in sorted(status_counts.items()):
            percentage = (count / self.stats['total_attempts']) * 100 if self.stats['total_attempts'] > 0 else 0
            print(f"[Instance {self.user_id}]    {status}: {count} ({percentage:.1f}%)")
        
        # Save results
        self.save_results(duration)
    
    def save_results(self, duration: float):
        """Save results to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"piso_custom_{self.user_id}_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write("="*80 + "\n")
            f.write(f"PISO WIFI CUSTOM PORTAL TEST - Instance {self.user_id}\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Portal URL: {self.base_url}{self.endpoints['dashboard']}\n")
            f.write(f"Duration: {duration:.2f} seconds\n\n")
            
            f.write("🔧 PORTAL ENDPOINTS USED:\n")
            f.write("-"*40 + "\n")
            for name, endpoint in self.endpoints.items():
                f.write(f"{name}: {self.base_url}{endpoint}\n")
            
            f.write("\n📊 TEST STATISTICS:\n")
            f.write("-"*40 + "\n")
            for key, value in self.stats.items():
                f.write(f"{key}: {value}\n")
            
            f.write("\n📝 SAMPLE RESULTS (First 30):\n")
            f.write("-"*40 + "\n")
            for result in self.results[:30]:
                f.write(f"User {result['user_id']:08d}: {result['status']}\n")
                f.write(f"  MAC: {result['mac']}\n")
                if result['coin_inserted']:
                    f.write(f"  Coin Inserted: Yes\n")
                if result['voucher_used']:
                    f.write(f"  Voucher Used: Yes\n")
                f.write(f"  Steps: {len(result['steps'])}\n\n")
        
        print(f"[Instance {self.user_id}] ✓ Results saved to: {filename}")


class MultiUserCoordinator:
    """Coordinate multiple test instances"""
    
    def __init__(self, portal_ip: str, total_instances: int, users_per_instance: int = 200):
        self.portal_ip = portal_ip
        self.total_instances = total_instances
        self.users_per_instance = users_per_instance
        
    def run(self):
        """Run coordinated test"""
        print("\n" + "="*80)
        print("         MULTI-USER CUSTOM PORTAL STRESS TEST")
        print("="*80)
        
        print(f"\n📋 TEST CONFIGURATION:")
        print(f"   Portal: http://{self.portal_ip}/client?page=dashboard")
        print(f"   Instances: {self.total_instances}")
        print(f"   Users per Instance: {self.users_per_instance}")
        print(f"   Total Users: {self.total_instances * self.users_per_instance:,}")
        
        print(f"\n⏰ Starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        processes = []
        
        for i in range(self.total_instances):
            tester = PisoWiFiCustomTester(
                portal_ip=self.portal_ip,
                num_users=self.users_per_instance,
                user_id=i,
                total_users=self.total_instances
            )
            
            process = Process(target=tester.run_stress_test)
            process.start()
            processes.append(process)
            
            print(f"[Coordinator] Started instance {i} (PID: {process.pid})")
            time.sleep(0.3)
        
        # Wait for all processes
        print(f"\n[Coordinator] All {self.total_instances} instances running...")
        for process in processes:
            process.join()
        
        print(f"\n[Coordinator] All tests completed!")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Piso WiFi Custom Portal Stress Test",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single instance test
  python3 piso_custom.py --portal 10.0.0.1 --users 100
  
  # Multi-user test
  python3 piso_custom.py --portal 10.0.0.1 --multi --instances 3 --per-instance 80
  
  # High-load test
  python3 piso_custom.py --portal 10.0.0.1 --users 500 --threads 50
        """
    )
    
    parser.add_argument("--portal", "-p", required=True, help="Piso WiFi portal IP (e.g., 10.0.0.1)")
    parser.add_argument("--users", "-u", type=int, default=100, help="Users per instance")
    parser.add_argument("--threads", "-t", type=int, default=25, help="Threads per batch")
    
    # Multi-user mode
    parser.add_argument("--multi", "-m", action="store_true", help="Multi-user mode")
    parser.add_argument("--instances", "-n", type=int, default=3, help="Number of instances")
    parser.add_argument("--per-instance", "-pi", type=int, default=80, help="Users per instance")
    
    args = parser.parse_args()
    
    print("="*80)
    print("      PISO WIFI CUSTOM PORTAL STRESS TESTER")
    print("="*80)
    print(f"\n🔧 Specifically designed for: http://{args.portal}/client?page=dashboard")
    print("\n⚠️  This tool simulates user interactions with your Piso WiFi portal")
    print("   Only use on networks you own or have permission to test!\n")
    
    if args.multi:
        print("📋 MULTI-USER MODE SELECTED")
        print(f"   Total instances: {args.instances}")
        print(f"   Total users: {args.instances * args.per_instance:,}")
        
        confirm = input("\nStart multi-user stress test? (yes/no): ").lower()
        if confirm == 'yes':
            coordinator = MultiUserCoordinator(
                portal_ip=args.portal,
                total_instances=args.instances,
                users_per_instance=args.per_instance
            )
            coordinator.run()
        else:
            print("❌ Test cancelled")
    else:
        print("📋 SINGLE INSTANCE MODE")
        print(f"   Users: {args.users:,}")
        print(f"   Threads: {args.threads}")
        
        confirm = input("\nStart stress test? (yes/no): ").lower()
        if confirm == 'yes':
            tester = PisoWiFiCustomTester(
                portal_ip=args.portal,
                num_users=args.users,
                user_id=0
            )
            tester.run_stress_test(threads_per_batch=args.threads)
        else:
            print("❌ Test cancelled")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()