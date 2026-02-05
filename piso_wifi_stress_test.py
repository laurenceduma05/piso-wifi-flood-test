#!/usr/bin/env python3
"""
Piso WiFi Stress Test Tool - Multi-User Edition
Simulates thousands of concurrent users connecting to a Piso WiFi portal
Supports multiple users running tests simultaneously
"""

import requests
import threading
import time
import socket
import json
from datetime import datetime
import random
import sys
import os
from multiprocessing import Process, Manager, Lock
from queue import Queue
import argparse

class PisoWiFiStressTest:
    def __init__(self, portal_ip: str, num_users: int = 1000, 
                 user_id: int = 0, total_users: int = 1, 
                 coordinator_ip: str = None, coordinator_port: int = 9999):
        """
        Initialize Piso WiFi stress tester with multi-user support
        
        Args:
            portal_ip: IP address of Piso WiFi portal
            num_users: Number of concurrent users to simulate per instance
            user_id: Unique ID for this test instance (0-based)
            total_users: Total number of concurrent test instances
            coordinator_ip: IP for coordination server (optional)
            coordinator_port: Port for coordination server
        """
        self.portal_ip = portal_ip
        self.portal_url = f"http://{portal_ip}"
        self.num_users = num_users
        self.user_id = user_id
        self.total_users = total_users
        
        # Coordination
        self.coordinator_ip = coordinator_ip
        self.coordinator_port = coordinator_port
        self.is_coordinator = False
        self.shared_stats = None
        
        # Statistics
        self.successful_logins = 0
        self.failed_logins = 0
        self.total_attempts = 0
        self.lock = threading.Lock()
        
        # Results storage
        self.results = []
        
        # User range for this instance
        self.user_start = user_id * num_users
        self.user_end = (user_id + 1) * num_users
        
        print(f"[Instance {user_id}] User range: {self.user_start} to {self.user_end-1}")
    
    def generate_user_credentials(self, user_id: int):
        """Generate credentials for a user"""
        return {
            "username": f"user{user_id:08d}",
            "password": f"pass{user_id:08d}",
            "voucher": f"PISO{random.randint(100000, 999999)}",
            "mac": f"00:1A:2B:{random.randint(0,255):02X}:{random.randint(0,255):02X}:{random.randint(0,255):02X}"
        }
    
    def attempt_login(self, global_user_id: int):
        """Simulate a single user login attempt"""
        credentials = self.generate_user_credentials(global_user_id)
        
        try:
            # Common Piso WiFi login endpoints
            login_urls = [
                f"{self.portal_url}/login",
                f"{self.portal_url}/auth",
                f"{self.portal_url}/voucher",
                f"{self.portal_url}/authenticate.php",
                f"{self.portal_url}/login.php"
            ]
            
            session = requests.Session()
            login_success = False
            
            # Try each potential endpoint
            for url in login_urls:
                try:
                    # Prepare POST data (common variations)
                    post_data_variations = [
                        {
                            "username": credentials["username"],
                            "password": credentials["password"]
                        },
                        {
                            "voucher": credentials["voucher"]
                        },
                        {
                            "code": credentials["voucher"]
                        },
                        {
                            "user": credentials["username"],
                            "pass": credentials["password"],
                            "voucher": credentials["voucher"]
                        }
                    ]
                    
                    for post_data in post_data_variations:
                        response = session.post(
                            url,
                            data=post_data,
                            timeout=3,
                            verify=False,
                            allow_redirects=True,
                            headers={
                                'User-Agent': f'PisoTester/{global_user_id}'
                            }
                        )
                        
                        # Check if login was successful
                        if response.status_code == 200 or response.status_code == 302:
                            if "success" in response.text.lower() or "welcome" in response.text.lower():
                                login_success = True
                                break
                    
                    if login_success:
                        break
                        
                except requests.exceptions.RequestException:
                    continue
            
            # Update statistics
            with self.lock:
                self.total_attempts += 1
                if login_success:
                    self.successful_logins += 1
                    status = "SUCCESS"
                else:
                    self.failed_logins += 1
                    status = "FAILED"
                
                # Update shared stats if available
                if self.shared_stats:
                    with self.shared_stats['lock']:
                        self.shared_stats['total_attempts'] += 1
                        if login_success:
                            self.shared_stats['successful_logins'] += 1
                        else:
                            self.shared_stats['failed_logins'] += 1
                
                # Print progress every 50 users
                if self.total_attempts % 50 == 0:
                    local_progress = f"[Instance {self.user_id}] Progress: {self.total_attempts}/{self.num_users}"
                    
                    if self.shared_stats:
                        total_all = self.shared_stats['total_attempts']
                        success_all = self.shared_stats['successful_logins']
                        global_progress = f" | Global: {total_all}/{self.num_users * self.total_users}"
                        print(f"{local_progress}{global_progress} | Success: {success_all}")
                    else:
                        print(f"{local_progress} | Success: {self.successful_logins}")
                
                self.results.append({
                    "user_id": global_user_id,
                    "instance_id": self.user_id,
                    "status": status,
                    "username": credentials["username"],
                    "voucher": credentials["voucher"]
                })
            
            return login_success
            
        except Exception as e:
            with self.lock:
                self.total_attempts += 1
                self.failed_logins += 1
                if self.shared_stats:
                    with self.shared_stats['lock']:
                        self.shared_stats['total_attempts'] += 1
                        self.shared_stats['failed_logins'] += 1
                
                self.results.append({
                    "user_id": global_user_id,
                    "instance_id": self.user_id,
                    "status": "ERROR",
                    "error": str(e)
                })
            return False
    
    def run_stress_test(self, threads_per_batch: int = 50):
        """
        Run the stress test with thousands of concurrent users
        
        Args:
            threads_per_batch: Number of concurrent threads per batch
        """
        print(f"\n[Instance {self.user_id}] " + "="*60)
        print(f"[Instance {self.user_id}]         PISO WiFi STRESS TEST - Instance {self.user_id}")
        print(f"[Instance {self.user_id}] " + "="*60)
        print(f"[Instance {self.user_id}] Target Portal: {self.portal_url}")
        print(f"[Instance {self.user_id}] Number of Users (this instance): {self.num_users:,}")
        print(f"[Instance {self.user_id}] Concurrent Threads: {threads_per_batch}")
        if self.total_users > 1:
            print(f"[Instance {self.user_id}] Total Concurrent Instances: {self.total_users}")
            print(f"[Instance {self.user_id}] Total Users (all instances): {self.num_users * self.total_users:,}")
        print(f"[Instance {self.user_id}] Starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[Instance {self.user_id}] " + "-"*60)
        
        start_time = time.time()
        
        # Create threads
        threads = []
        
        # Launch all users with controlled concurrency
        user_queue = Queue()
        for user_id in range(self.user_start, self.user_end):
            user_queue.put(user_id)
        
        # Worker function for threads
        def worker():
            while not user_queue.empty():
                try:
                    user_id = user_queue.get_nowait()
                    self.attempt_login(user_id)
                    user_queue.task_done()
                except:
                    break
        
        # Create and start worker threads
        for i in range(threads_per_batch):
            thread = threading.Thread(target=worker)
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Wait for all users to be processed
        print(f"[Instance {self.user_id}] [STATUS] Running stress test...")
        user_queue.join()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=5)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print instance report
        self.print_instance_report(duration)
    
    def print_instance_report(self, duration: float):
        """Print report for this instance"""
        print(f"\n[Instance {self.user_id}] " + "="*60)
        print(f"[Instance {self.user_id}]               INSTANCE REPORT")
        print(f"[Instance {self.user_id}] " + "="*60)
        
        print(f"[Instance {self.user_id}] 📊 SUMMARY:")
        print(f"[Instance {self.user_id}]    Portal URL: {self.portal_url}")
        print(f"[Instance {self.user_id}]    Users Attempted: {self.total_attempts:,}")
        print(f"[Instance {self.user_id}]    Successful Logins: {self.successful_logins:,}")
        print(f"[Instance {self.user_id}]    Failed Logins: {self.failed_logins:,}")
        if self.total_attempts > 0:
            success_rate = (self.successful_logins/self.total_attempts*100)
            print(f"[Instance {self.user_id}]    Success Rate: {success_rate:.2f}%")
        
        print(f"[Instance {self.user_id}] ⏱️  PERFORMANCE:")
        print(f"[Instance {self.user_id}]    Duration: {duration:.2f} seconds")
        if self.total_attempts > 0:
            print(f"[Instance {self.user_id}]    Rate: {self.total_attempts/duration:.2f} attempts/second")
            print(f"[Instance {self.user_id}]    Time per User: {(duration/self.total_attempts)*1000:.2f} ms")
        
        # Save individual results
        self.save_individual_results(duration)
    
    def save_individual_results(self, duration: float):
        """Save individual instance results to a file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"piso_wifi_test_instance_{self.user_id}_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write("="*60 + "\n")
            f.write(f"PISO WiFi STRESS TEST - INSTANCE {self.user_id}\n")
            f.write("="*60 + "\n\n")
            f.write(f"Portal: {self.portal_url}\n")
            f.write(f"Instance ID: {self.user_id}\n")
            f.write(f"Users Attempted: {self.total_attempts}\n")
            f.write(f"Successful: {self.successful_logins}\n")
            f.write(f"Failed: {self.failed_logins}\n")
            if self.total_attempts > 0:
                f.write(f"Success Rate: {(self.successful_logins/self.total_attempts*100):.2f}%\n")
            f.write(f"Duration: {duration:.2f} seconds\n\n")
            f.write("-"*60 + "\n")
            f.write("DETAILED RESULTS:\n")
            f.write("-"*60 + "\n\n")
            
            for result in self.results[:100]:  # Save first 100 results
                f.write(f"User {result['user_id']:08d}: {result['status']}")
                if 'username' in result:
                    f.write(f" | Username: {result['username']}")
                if 'voucher' in result:
                    f.write(f" | Voucher: {result['voucher']}")
                f.write("\n")
        
        print(f"[Instance {self.user_id}] ✓ Results saved to: {filename}")
    
    def get_stats(self):
        """Get statistics from this instance"""
        return {
            'instance_id': self.user_id,
            'successful_logins': self.successful_logins,
            'failed_logins': self.failed_logins,
            'total_attempts': self.total_attempts,
            'user_start': self.user_start,
            'user_end': self.user_end
        }


class MultiUserCoordinator:
    """Coordinates multiple stress test instances"""
    
    def __init__(self, portal_ip: str, total_users: int, users_per_instance: int = 500):
        """
        Initialize multi-user coordinator
        
        Args:
            portal_ip: Target portal IP
            total_users: Total number of concurrent test instances
            users_per_instance: Users per instance
        """
        self.portal_ip = portal_ip
        self.total_users = total_users
        self.users_per_instance = users_per_instance
        self.instances = []
        self.shared_stats = Manager().dict()
        self.shared_stats['total_attempts'] = 0
        self.shared_stats['successful_logins'] = 0
        self.shared_stats['failed_logins'] = 0
        self.shared_stats['lock'] = Manager().Lock()
        
    def start_all_instances(self):
        """Start all stress test instances"""
        print("\n" + "="*80)
        print("           MULTI-USER STRESS TEST COORDINATION")
        print("="*80)
        print(f"Target Portal: {self.portal_ip}")
        print(f"Number of Instances: {self.total_users}")
        print(f"Users per Instance: {self.users_per_instance}")
        print(f"Total Concurrent Users: {self.total_users * self.users_per_instance:,}")
        print(f"Starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")
        
        processes = []
        
        # Create and start processes
        for i in range(self.total_users):
            tester = PisoWiFiStressTest(
                portal_ip=self.portal_ip,
                num_users=self.users_per_instance,
                user_id=i,
                total_users=self.total_users
            )
            tester.shared_stats = self.shared_stats
            self.instances.append(tester)
            
            process = Process(target=tester.run_stress_test, args=(50,))
            process.start()
            processes.append(process)
            
            print(f"[Coordinator] Started instance {i} (PID: {process.pid})")
            time.sleep(0.5)  # Stagger process starts
        
        # Wait for all processes to complete
        print(f"\n[Coordinator] Waiting for all {self.total_users} instances to complete...")
        for process in processes:
            process.join()
        
        # Print combined report
        self.print_combined_report()
    
    def print_combined_report(self):
        """Print combined report from all instances"""
        print("\n" + "="*80)
        print("                  COMBINED TEST REPORT")
        print("="*80)
        
        total_attempts = self.shared_stats['total_attempts']
        successful_logins = self.shared_stats['successful_logins']
        failed_logins = self.shared_stats['failed_logins']
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total Instances: {self.total_users}")
        print(f"   Total Users Attempted: {total_attempts:,}")
        print(f"   Successful Logins: {successful_logins:,}")
        print(f"   Failed Logins: {failed_logins:,}")
        if total_attempts > 0:
            print(f"   Success Rate: {(successful_logins/total_attempts*100):.2f}%")
        
        print(f"\n⚡ LOAD GENERATED:")
        print(f"   Total Concurrent Users: {self.total_users * self.users_per_instance:,}")
        
        # Save combined results
        self.save_combined_results()
    
    def save_combined_results(self):
        """Save combined results to a file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"piso_wifi_test_combined_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write("="*80 + "\n")
            f.write("PISO WiFi MULTI-USER STRESS TEST - COMBINED RESULTS\n")
            f.write("="*80 + "\n\n")
            f.write(f"Portal: http://{self.portal_ip}\n")
            f.write(f"Total Instances: {self.total_users}\n")
            f.write(f"Total Users: {self.shared_stats['total_attempts']}\n")
            f.write(f"Successful: {self.shared_stats['successful_logins']}\n")
            f.write(f"Failed: {self.shared_stats['failed_logins']}\n")
            if self.shared_stats['total_attempts'] > 0:
                f.write(f"Success Rate: {(self.shared_stats['successful_logins']/self.shared_stats['total_attempts']*100):.2f}%\n")
        
        print(f"\n[Coordinator] ✓ Combined results saved to: {filename}")


def run_single_user_mode(args):
    """Run in single user mode"""
    tester = PisoWiFiStressTest(
        portal_ip=args.portal,  # FIXED: Changed from args.portal_ip
        num_users=args.users,
        user_id=args.instance_id
    )
    tester.run_stress_test(threads_per_batch=args.threads)


def run_multi_user_mode(args):
    """Run in multi-user coordinator mode"""
    coordinator = MultiUserCoordinator(
        portal_ip=args.portal,  # FIXED: Changed from args.portal_ip
        total_users=args.instances,
        users_per_instance=args.per_instance
    )
    coordinator.start_all_instances()


def main():
    """Main function with command line arguments"""
    parser = argparse.ArgumentParser(
        description="Piso WiFi Stress Test Tool - Multi-User Edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single instance with 1000 users
  python3 piso_stress.py --portal 192.168.1.1 --users 1000
  
  # Multi-user mode with 5 instances, 500 users each
  python3 piso_stress.py --portal 192.168.1.1 --multi --instances 5 --per-instance 500
  
  # Join existing test as instance 3
  python3 piso_stress.py --portal 192.168.1.1 --instance-id 3 --users 200
        """
    )
    
    # Required arguments
    parser.add_argument("--portal", "-p", required=True, help="Piso WiFi portal IP address")
    
    # Mode selection
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--multi", "-m", action="store_true", help="Multi-user coordinator mode")
    group.add_argument("--instance-id", "-i", type=int, default=0, help="Instance ID for single mode")
    
    # Single mode arguments
    parser.add_argument("--users", "-u", type=int, default=1000, help="Number of users per instance")
    parser.add_argument("--threads", "-t", type=int, default=50, help="Threads per batch")
    
    # Multi mode arguments
    parser.add_argument("--instances", "-n", type=int, default=5, help="Number of instances (multi mode)")
    parser.add_argument("--per-instance", "-pi", type=int, default=500, help="Users per instance (multi mode)")
    
    args = parser.parse_args()
    
    print("="*80)
    print("         PISO WiFi STRESS TESTING TOOL - MULTI-USER EDITION")
    print("="*80)
    
    print(f"\n⚠️  WARNING: This tool will generate significant network traffic.")
    print("   Only use on networks you own or have permission to test.\n")
    
    if args.multi:
        print(f"📋 MULTI-USER MODE CONFIGURATION:")
        print(f"   Portal IP: {args.portal}")
        print(f"   Number of Instances: {args.instances}")
        print(f"   Users per Instance: {args.per_instance}")
        print(f"   Total Concurrent Users: {args.instances * args.per_instance:,}")
        
        confirm = input("\nStart multi-user stress test? (yes/no): ").lower()
        if confirm == 'yes':
            run_multi_user_mode(args)
        else:
            print("\n❌ Test cancelled")
    else:
        print(f"📋 SINGLE INSTANCE MODE CONFIGURATION:")
        print(f"   Portal IP: {args.portal}")
        print(f"   Instance ID: {args.instance_id}")
        print(f"   Number of Users: {args.users:,}")
        print(f"   Concurrent Threads: {args.threads}")
        
        confirm = input("\nStart stress test? (yes/no): ").lower()
        if confirm == 'yes':
            run_single_user_mode(args)
        else:
            print("\n❌ Test cancelled")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()