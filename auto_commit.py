# -*- coding: utf-8 -*-
import sys
import subprocess
from datetime import datetime

# Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8')

def run_command(command):
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        encoding='utf-8'    # <- THIS is the fix
    )
    if result.returncode == 0:
        print(f"OK: {command}")
    else:
        print(f"FAILED: {command}")
        print(result.stderr)
    return result

def daily_update():
    print("=" * 50)
    print("DAILY PRICE INTELLIGENCE UPDATE")
    print("=" * 50)

    print("\nRunning scraper...")
    run_command("python scraper/scraper.py")

    print("\nStaging changes...")
    run_command("git add .")

    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    commit_message = f"Daily update: Price data collected on {today}"

    print("\nCommitting...")
    run_command(f'git commit -m "{commit_message}"')

    print("\nPushing to GitHub...")
    run_command("git push origin main")

    print("\nDone! Streak is safe!")

if __name__ == "__main__":
    daily_update()