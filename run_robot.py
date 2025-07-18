#!/usr/bin/env python3
import multiprocessing
import subprocess
import sys
import time
import signal
import os

def run_server():
    """Run the server script"""
    print("[MAIN] Starting server...")
    try:
        subprocess.run([sys.executable, "serverV2Field.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[MAIN] Server process failed: {e}")
    except KeyboardInterrupt:
        print("[MAIN] Server interrupted")

def run_client():
    """Run the client script"""
    print("[MAIN] Starting client...")
    # Give server time to start
    time.sleep(2)
    try:
        subprocess.run([sys.executable, "clientLib.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[MAIN] Client process failed: {e}")
    except KeyboardInterrupt:
        print("[MAIN] Client interrupted")

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\n[MAIN] Received interrupt signal, shutting down...")
    sys.exit(0)

def main():
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("[MAIN] Starting robot system...")
    print("[MAIN] Press Ctrl+C to stop all processes")
    
    # Create processes
    server_process = multiprocessing.Process(target=run_server, name="Server")
    client_process = multiprocessing.Process(target=run_client, name="Client")
    
    try:
        # Start server first
        server_process.start()
        print(f"[MAIN] Server process started with PID: {server_process.pid}")
        
        # Start client
        client_process.start()
        print(f"[MAIN] Client process started with PID: {client_process.pid}")
        
        # Wait for both processes to complete
        server_process.join()
        client_process.join()
        
    except KeyboardInterrupt:
        print("\n[MAIN] Interrupt received, terminating processes...")
        
        # Terminate processes gracefully
        if server_process.is_alive():
            print("[MAIN] Terminating server process...")
            server_process.terminate()
            server_process.join(timeout=5)
            if server_process.is_alive():
                print("[MAIN] Force killing server process...")
                server_process.kill()
        
        if client_process.is_alive():
            print("[MAIN] Terminating client process...")
            client_process.terminate()
            client_process.join(timeout=5)
            if client_process.is_alive():
                print("[MAIN] Force killing client process...")
                client_process.kill()
    
    print("[MAIN] All processes terminated")

if __name__ == "__main__":
    # Set multiprocessing start method for better compatibility
    multiprocessing.set_start_method('spawn', force=True)
    main()