# Panfinder

## Description
Panfinder is a tool designed to find admin panels and directories in web applications.

## Features
- Supports multiple wordlists for path discovery.
- Color-coded output based on HTTP status codes.
- Multi-threaded scanning for faster results.



Installation

Clone the repository:

git clone https://github.com/0x0Mr/panfinder.git

## Usage
To use Panfinder, specify the target URL and a wordlist of paths to scan.

```bash
python3 panfinder.py -u http://example.com -w panels/admin.txt
