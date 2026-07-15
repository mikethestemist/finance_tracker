import subprocess
import sys
import os

def run_script(script_name, is_streamlit=False):
    print(f"🌿 Executing: {script_name}...")
    try:
        if is_streamlit:
            # Run Streamlit without blocking, or let it take over the process
            subprocess.run([sys.executable, "-m", "streamlit", "run", script_name])
        else:
            # Run standard backend Python scripts sequentially
            result = subprocess.run([sys.executable, script_name], check=True, text=True)
            if result.returncode == 0:
                print(f"✅ {script_name} completed successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during execution of {script_name}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Assuming your scripts are named step1_fetch.py, step2_process.py, etc.
    # Replace these filenames with your actual filenames!
    
    run_script("01_Email_Fetcher.py")     # First process
    run_script("02_Trans_Filter.py")   # Second process
    
    # Finally, boot up your dashboard
    run_script("03_Dashboard.py", is_streamlit=True)