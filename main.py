import os
import subprocess
import signal
import sys
import time
import atexit

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def check_running_servers():
    if os.name == 'nt':
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], capture_output=True, text=True)
        return 'python.exe' in result.stdout
    else:
        try:
            result = subprocess.run(['pgrep', '-f', 'python.*(oserver|ouss)'], capture_output=True, text=True)
            return bool(result.stdout.strip())
        except:
            return False

def kill_python_servers():
    if os.name == 'nt':
        os.system('taskkill /F /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *server*" > nul 2>&1')
    else:
        try:
            os.system("pkill -9 -f 'python.*oserver.py' 2>/dev/null")
            os.system("pkill -9 -f 'python.*oserver-test1.py' 2>/dev/null")
            os.system("pkill -9 -f 'python.*ouss.py' 2>/dev/null")
            os.system("pkill -9 -f 'python.*oucc2.py' 2>/dev/null")
        except:
            pass
    time.sleep(0.5)

def cleanup():
    kill_python_servers()

def run_selected_file(file_path):
    try:
        if check_running_servers():
            response = input("\nA server is already running. Do you want to kill it? (y/n): ").lower()
            if response == 'y':
                kill_python_servers()
                print("Previous server killed.")
            else:
                print("Keeping existing server running.")
               # return
        
        process = subprocess.Popen(['python', file_path])
        
        print("\nPress Ctrl+C to exit")
        
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\nClosing server...", end='', flush=True)
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
            kill_python_servers()
            print(" done")
            return
                
    except Exception as e:
        print(f"Error running {file_path}: {e}")
        kill_python_servers()

def main():
    atexit.register(cleanup)
    
    while True:
        clear_screen()
        print("Screen Sharing Application")
        print("=========================")
        print("1. TCP Implementation")
        print("2. UDP Implementation")
        print("3. Exit")
        
        try:
            choice = input("\nEnter your choice (1-3): ")
            
            if choice == "1":
                clear_screen()
                print("TCP Implementation")
                print("=================")
                print("1. First Implementation (using PIL)")
                print("2. Second Implementation (using MSS)")
                print("3. Back to main menu")
                
                tcp_choice = input("\nEnter your choice (1-3): ")
                
                if tcp_choice == "1":
                    run_selected_file("tcp/oserver.py")
                elif tcp_choice == "2":
                    run_selected_file("tcp/oserver-test1.py")
                elif tcp_choice == "3":
                    continue
                    
            elif choice == "2":
                clear_screen()
                print("UDP Implementation")
                print("=================")
                print("1. Server (ouss.py)")
                print("2. Client (oucc.py)")
                print("3. Back to main menu")
                
                udp_choice = input("\nEnter your choice (1-3): ")
                
                if udp_choice == "1":
                    run_selected_file("udp/ouss.py")
                elif udp_choice == "2":
                    run_selected_file("udp/oucc2.py")
                elif udp_choice == "3":
                    continue
                    
            elif choice == "3":
                print("\nExiting application...")
                kill_python_servers()
                os._exit(0)
            
        except KeyboardInterrupt:
            print("\nExiting application...")
            kill_python_servers()
            os._exit(0)

if __name__ == "__main__":
    main()
