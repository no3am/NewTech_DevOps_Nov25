#!/usr/bin/env python3
"""
ETCD Writer Script

This script allows you to manually change the value of /config/background_color
in etcd. This simulates how Kubernetes API server writes changes to etcd.

Usage:
    python writer.py <color>
    
Examples:
    python writer.py red
    python writer.py blue
    python writer.py green
    python writer.py "#FF5733"
"""

import os
import sys
import etcd3

# Configuration
ETCD_HOST = os.getenv('ETCD_HOST', 'localhost')
ETCD_PORT = int(os.getenv('ETCD_PORT', '2379'))
WATCH_KEY = '/config/background_color'

def main():
    # Check if color argument is provided
    if len(sys.argv) < 2:
        print("Usage: python writer.py <color>")
        print("\nExamples:")
        print("  python writer.py red")
        print("  python writer.py blue")
        print("  python writer.py green")
        print("  python writer.py '#FF5733'")
        sys.exit(1)
    
    new_value = sys.argv[1]
    
    print(f"Connecting to etcd at {ETCD_HOST}:{ETCD_PORT}...")
    
    try:
        # Connect to etcd
        client = etcd3.client(host=ETCD_HOST, port=ETCD_PORT)
        
        # Get current value (if exists)
        value, metadata = client.get(WATCH_KEY)
        if value:
            old_value = value.decode('utf-8')
            print(f"Current value: {old_value}")
        else:
            print("Key does not exist yet. Creating new key...")
        
        # Write the new value
        # In Kubernetes: This is what happens when you run 'kubectl apply'
        # The API server writes the resource to etcd
        print(f"\nWriting new value: {new_value}")
        client.put(WATCH_KEY, new_value)
        
        # Verify the write
        value, metadata = client.get(WATCH_KEY)
        if value and value.decode('utf-8') == new_value:
            print(f"✓ Successfully updated {WATCH_KEY} to: {new_value}")
            print("\n💡 The Watcher service should have detected this change instantly!")
            print("   Check the watcher container logs to see the reaction.")
        else:
            print("✗ Failed to verify the write")
            sys.exit(1)
    
    except Exception as e:
        print(f"✗ Error: {e}")
        print(f"\nMake sure:")
        print(f"  1. etcd is running (docker-compose up)")
        print(f"  2. ETCD_HOST and ETCD_PORT are correct")
        print(f"  3. You can connect to etcd from this machine")
        sys.exit(1)

if __name__ == '__main__':
    main()
