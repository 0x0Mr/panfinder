import requests
import sys
import time
import argparse
import os
import threading
from datetime import datetime

# Function to print colored text
def print_color(text, color):
    if color == "green":
        print("\033[92m" + text + "\033[0m")
    elif color == "red":
        print("\033[91m" + text + "\033[0m")
    elif color == "blue":
        print("\033[94m" + text + "\033[0m")
    elif color == "purple":
        print("\033[95m" + text + "\033[0m")
    else:
        print(text)

# Function to check for admin panels
def find_admin_panel(base_url, wordlist, status_codes, threads, verbose, output_file):
    # Ensure base_url ends with a slash
    if not base_url.endswith('/'):
        base_url += '/'

    panel_dict = {}
    lock = threading.Lock()

    checked_panels = 0
    total_panels = sum(1 for line in open(wordlist))

    def check_panel(path):
        nonlocal checked_panels
        try:
            url = base_url + path.strip()
            response = requests.get(url, timeout=5)
            if response.status_code in status_codes:
                color = "green" if response.status_code == 200 else \
                        "blue" if response.status_code in [301, 307] else \
                        "red" if response.status_code in [400, 404] else \
                        "purple" if response.status_code == 403 else \
                        "yellow"
                with lock:
                    checked_panels += 1
                    progress = "[**] Checking panel {}/{} [{}] [{}]".format(
                        checked_panels, total_panels,
                        "#" * (checked_panels // (total_panels // 100)),
                        checked_panels, total_panels
                    )
                    sys.stdout.write("\r" + progress)
                    sys.stdout.flush()
                    if checked_panels not in panel_dict:
                        panel_dict[checked_panels] = []
                    panel_dict[checked_panels].append((url, response.headers, response.status_code, color))
        except requests.RequestException as e:
            if verbose:
                with lock:
                    print_color("\r[-] Error accessing " + url + ": " + str(e), "red")

    if threads is None:
        threads = 10
    for line in open(wordlist, 'r'):
        t = threading.Thread(target=check_panel, args=(line,))
        t.start()
        if threading.active_count() > threads:
            t.join()

    # Wait for all threads to finish
    while threading.active_count() > 1:
        time.sleep(1)

    # Print results
    for status_code, panels in panel_dict.items():
        for url, headers, status, color in panels:
            print_color("\n[+] Found panel: " + url + " with status code " + str(status) + " (" + ", ".join([f"{k}: {v}" for k, v in headers.items()]) + ")", color)
            if output_file:
                with open(output_file, 'a') as f:
                    f.write("[+] Found panel: " + url + " with status code " + str(status) + " (" + ", ".join([f"{k}: {v}" for k, v in headers.items()]) + ")\n")

    if not panel_dict:
        print_color("[-] No panels found.", "red")
    if output_file:
        with open(output_file, 'a') as f:
            f.write("[-] No panels found.\n")

    print_color("\n[+] Scan completed.", "green")

# Function to display ASCII art
def display_ascii_art():
    print("""
    *****************************************
    ***        PWN TOOLS v1.0              ***
    *****************************************
    """)

# Function to display banner
def display_banner():
    print("""
             ******************************************
             *          PWN Admin Panel Finder        *
             ******************************************
             * Author: [0x0MAr]                          *
             * Date: [3/7/2024]                             *
             * insta:@_7pwn                          *
             ******************************************
             """.format(datetime.now().strftime("%m/%d/%Y")))

# Parse command line arguments
parser = argparse.ArgumentParser(description='Find admin panels on a target web application.')
parser.add_argument('-u', '--url', required=True, help='URL to target')
parser.add_argument('-w', '--wordlist', required=True, help='Wordlist to use for paths')
parser.add_argument('-s', '--status-codes', nargs='+', default=list(range(200, 501)), help='List of HTTP status codes to consider as valid (default: 200-500)')
parser.add_argument('-t', '--threads', type=int, default=None, help='Number of threads to use (default: 10)')
parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
parser.add_argument('-o', '--output', help='Save output to a file')
args = parser.parse_args()

# Display banner
display_banner()

# Display ASCII art
display_ascii_art()

# Find admin panels
with open(args.wordlist, 'r') as f:
    total_panels = sum(1 for line in f)
    f.seek(0)
    find_admin_panel(args.url, args.wordlist, set(args.status_codes), args.threads, args.verbose, args.output)
