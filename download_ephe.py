#!/usr/bin/env python3
"""Download minimal Swiss Ephemeris files"""
import os
import urllib.request
import sys

def main():
    eph_dir = os.path.join(os.getcwd(), 'eph')
    os.makedirs(eph_dir, exist_ok=True)
    
    # Minimal files needed for planets 1900-2100
    files = [
        'se1_100.se1',  # 1900-1999
        'se1_200.se1',  # 2000-2099
    ]
    
    base_url = 'https://www.astro.com/swisseph/ephe/se1'
    
    print("📥 Downloading ephemeris files...")
    for fname in files:
        url = f"{base_url}/{fname}"
        filepath = os.path.join(eph_dir, fname)
        if not os.path.exists(filepath):
            print(f"  Downloading {fname}...")
            try:
                urllib.request.urlretrieve(url, filepath)
                print(f"  ✓ {fname}")
            except Exception as e:
                print(f"  ✗ Failed: {e}")
        else:
            print(f"  ✓ {fname} (already exists)")
    
    print(f"✅ Ephemeris files ready in {eph_dir}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
