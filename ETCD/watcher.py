#!/usr/bin/env python3
"""
ETCD Watcher Service

This service demonstrates the Watch mechanism used by Kubernetes Controllers.
When a key changes in etcd, this watcher is immediately notified without polling.

HOW KUBERNETES USES THIS:
- Kubernetes Controllers watch etcd for changes to resources (Pods, Deployments, etc.)
- When you create a Pod, Kubernetes writes it to etcd
- The Controller watching that resource type immediately detects the change
- The Controller then takes action (e.g., schedules the Pod to a node)
- This is event-driven, not polling-based - making it fast and efficient!
"""

import os
import sys
import time

try:
    import etcd3
except ImportError as e:
    print(f"ERROR: Failed to import etcd3: {e}", file=sys.stderr)
    print("Make sure etcd3 is installed: pip install etcd3", file=sys.stderr)
    sys.exit(1)

# Configuration from environment variables
ETCD_HOST = os.getenv('ETCD_HOST', 'localhost')
ETCD_PORT = int(os.getenv('ETCD_PORT', '2379'))
WATCH_KEY = '/config/background_color'

def main():
    print("=" * 60, flush=True)
    print("ETCD Watcher Service - Kubernetes Controller Simulation", flush=True)
    print("=" * 60, flush=True)
    print(f"Connecting to etcd at {ETCD_HOST}:{ETCD_PORT}...", flush=True)
    
    # Connect to etcd
    # In Kubernetes, Controllers connect to the etcd cluster through the API server
    try:
        client = etcd3.client(host=ETCD_HOST, port=ETCD_PORT)
        print(f"✓ Connected to etcd successfully!")
    except Exception as e:
        print(f"✗ Failed to connect to etcd: {e}")
        print(f"  Make sure etcd is running and accessible at {ETCD_HOST}:{ETCD_PORT}")
        sys.exit(1)
    
    print(f"\nWatching key: {WATCH_KEY}")
    print("Waiting for updates...")
    print("(This is how Kubernetes Controllers wait for resource changes)\n")
    print("-" * 60)
    
    # Get initial value if it exists
    try:
        value, metadata = client.get(WATCH_KEY)
        if value:
            print(f"Current value: {value.decode('utf-8') if isinstance(value, bytes) else value}")
        else:
            print("Key does not exist yet. Waiting for first write...")
    except Exception as e:
        print(f"⚠ Could not read initial value: {e}")
        print("   (This is okay - we'll still watch for new values)")
    
    print("-" * 60)
    print("\n🔍 WATCHING FOR CHANGES... (Press Ctrl+C to stop)\n")
    
    # Set up the watch
    # This is the magic! Instead of polling (checking repeatedly),
    # we subscribe to events. When the key changes, we get notified immediately.
    try:
        # Watch for changes to the key
        # In Kubernetes: Controllers watch for changes to specific resource types
        # Example: A Deployment Controller watches for Deployment objects
        # Using watch() for a single key
        events_iterator, cancel = client.watch(WATCH_KEY)
        
        for event in events_iterator:
            # Handle WatchResponse objects - python3-etcd3 returns events differently
            # The event might be a WatchResponse with events list, or individual events
            try:
                if hasattr(event, 'events'):
                    # It's a WatchResponse object with multiple events
                    events_list = event.events
                else:
                    # It's a single event
                    events_list = [event]
                
                for evt in events_list:
                    # Check if it's a PutEvent (create/update) or DeleteEvent
                    if hasattr(evt, 'value') and evt.value is not None:
                        # Key was created or updated
                        new_value = evt.value.decode('utf-8') if isinstance(evt.value, bytes) else evt.value
                        key_name = evt.key.decode('utf-8') if hasattr(evt, 'key') and evt.key and isinstance(evt.key, bytes) else (evt.key if hasattr(evt, 'key') and evt.key else WATCH_KEY)
                        
                        print("\n" + "=" * 60)
                        print("🚨 DETECTED CHANGE! New Color is:", new_value)
                        print("=" * 60)
                        print(f"Event Type: {type(evt).__name__}")
                        print(f"Key: {key_name}")
                        print(f"Value: {new_value}")
                        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
                        print("\n💡 This is exactly how Kubernetes Controllers react to changes!")
                        print("   - No polling needed")
                        print("   - Instant notification")
                        print("   - Event-driven architecture")
                        print("-" * 60)
                        print("\n🔍 Continuing to watch...\n")
                    elif hasattr(evt, 'value') and evt.value is None:
                        # Key was deleted
                        print("\n" + "=" * 60)
                        print("🚨 DETECTED DELETION! Key was removed")
                        print("=" * 60)
                        print("-" * 60)
                        print("\n🔍 Continuing to watch...\n")
            except Exception as e:
                print(f"Error processing event: {e}")
                print(f"Event type: {type(event)}")
                print(f"Event attributes: {dir(event)}")
                import traceback
                traceback.print_exc()
    
    except KeyboardInterrupt:
        print("\n\nWatcher stopped by user.")
        cancel()
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error watching key: {e}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
