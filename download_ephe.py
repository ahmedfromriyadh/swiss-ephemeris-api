#!/usr/bin/env python3
"""Download Swiss Ephemeris data files"""
import os
import urllib.request
import sys

def download_file(url, filename):
    print(f"Downloading {filename}...")
    try:
        urllib.request.urlretrieve(url, filename)
        print(f"✓ Downloaded {filename}")
        return True
    except Exception as e:
        print(f"✗ Failed to download {filename}: {e}")
        return False

def main():
    # ✅ IMPORTANT: Use current working directory (writable on Render)
    eph_dir = os.path.join(os.getcwd(), 'eph')
    os.makedirs(eph_dir, exist_ok=True)
    
    # Files to download
    files_to_download = [
        'se1_100.se1',
        'se1_200.se1',
        'se1_300.se1',
    ]
    
    base_url = 'https://www.astro.com/ftp/swisseph/ephe'
    
    success = True
    for filename in files_to_download:
        url = f"{base_url}/{filename}"
        filepath = os.path.join(eph_dir, filename)
        if not download_file(url, filepath):
            success = False
    
    if success:
        print(f"✓ All ephemeris files downloaded to {eph_dir}!")
        return 0
    else:
        print("✗ Some files failed to download")
        return 1

if __name__ == '__main__':
    sys.exit(main())
