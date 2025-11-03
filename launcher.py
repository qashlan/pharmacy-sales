"""
Launcher script for Pharmacy Sales Analytics Windows Executable.
This script starts the Streamlit server and opens the browser automatically.
"""

import sys
import os
import webbrowser
import time
import socket
from pathlib import Path
import subprocess
import threading

def find_free_port():
    """Find a free port to run Streamlit on."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def open_browser(url, delay=2):
    """Open browser after a delay to ensure server is ready."""
    time.sleep(delay)
    webbrowser.open(url)

def get_base_path():
    """Get the base path for bundled resources."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return Path(sys._MEIPASS)
    else:
        # Running as script
        return Path(__file__).parent

def main():
    """Main launcher function."""
    print("=" * 60)
    print("    Pharmacy Sales Analytics Dashboard")
    print("=" * 60)
    print()
    
    # Set base path for resources
    base_path = get_base_path()
    
    # Change to the base directory
    os.chdir(base_path)
    
    # Find a free port
    port = find_free_port()
    url = f"http://localhost:{port}"
    
    print(f"Starting server on {url}")
    print()
    print("The dashboard will open in your browser automatically.")
    print("To stop the server, close this window or press Ctrl+C")
    print()
    print("=" * 60)
    
    # Start browser in a separate thread
    browser_thread = threading.Thread(target=open_browser, args=(url, 3))
    browser_thread.daemon = True
    browser_thread.start()
    
    # Prepare streamlit command
    streamlit_script = base_path / "dashboard.py"
    
    # Run streamlit
    try:
        # Use subprocess to run streamlit
        cmd = [
            sys.executable,
            "-m", "streamlit", "run",
            str(streamlit_script),
            f"--server.port={port}",
            "--server.headless=true",
            "--browser.gatherUsageStats=false",
            "--server.enableCORS=false",
            "--server.enableXsrfProtection=false"
        ]
        
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        print("Thank you for using Pharmacy Sales Analytics!")
    except Exception as e:
        print(f"\nError starting server: {e}")
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)

if __name__ == "__main__":
    main()



