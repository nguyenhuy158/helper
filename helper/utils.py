import subprocess

def run_cmd(cmd):
    """Run a shell command and print the output."""
    print(f"$ {cmd}")
    try:
        result = subprocess.check_output(cmd, shell=True, text=True).strip()
        print(result)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None
