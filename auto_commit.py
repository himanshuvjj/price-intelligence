import sys
sys.stdout.reconfigure(encoding='utf-8')

import subprocess
from datetime import datetime

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ {command}")
    else:
        print(f"❌ Failed: {command}")
        print(result.stderr)
    return result

def daily_update():
    print("=" * 50)
    print("🔄 DAILY PRICE INTELLIGENCE UPDATE")
    print("=" * 50)

    print("\n📡 Running scraper...")
    run_command("python scraper/scraper.py")

    print("\n📦 Staging changes...")
    run_command("git add .")

    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    commit_message = f"📊 Daily update: Price data collected on {today}"

    print(f"\n💬 Committing...")
    run_command(f'git commit -m "{commit_message}"')

    print("\n🚀 Pushing to GitHub...")
    run_command("git push origin main")

    print("\n✅ Daily update complete! Streak is safe 🔥")

if __name__ == "__main__":
    daily_update()