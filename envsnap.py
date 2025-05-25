# envsnap.py – MVP for capturing and restoring environment snapshots

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime

SNAPSHOT_DIR = os.path.expanduser("~/.envsnap")
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

def snapshot_file(name):
    return os.path.join(SNAPSHOT_DIR, f"{name}.json")

def get_env_vars():
    keys = ["PATH", "DEBUG", "API_KEY", "SECRET_KEY"]  # Extend as needed
    return {key: os.environ.get(key, "") for key in keys}

def get_python_version():
    return sys.version.split("\n")[0]

def get_venv():
    return os.environ.get("VIRTUAL_ENV", "none")

def get_installed_packages():
    try:
        result = subprocess.check_output([sys.executable, "-m", "pip", "freeze"])
        return result.decode().splitlines()
    except subprocess.CalledProcessError:
        return []

def get_git_branch():
    try:
        result = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        return result.decode().strip()
    except subprocess.CalledProcessError:
        return "none"

def save_snapshot(name):
    data = {
        "timestamp": datetime.now().isoformat(),
        "python_version": get_python_version(),
        "virtualenv": get_venv(),
        "packages": get_installed_packages(),
        "git_branch": get_git_branch(),
        "env_vars": get_env_vars(),
    }
    with open(snapshot_file(name), 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Snapshot '{name}' saved.")

def list_snapshots():
    for file in os.listdir(SNAPSHOT_DIR):
        if file.endswith(".json"):
            path = os.path.join(SNAPSHOT_DIR, file)
            with open(path) as f:
                data = json.load(f)
                print(f"📸 {file[:-5]} – {data['timestamp']}")

def restore_env_vars(name):
    path = snapshot_file(name)
    if not os.path.exists(path):
        print("❌ Snapshot not found.")
        return
    with open(path) as f:
        data = json.load(f)
    for k, v in data.get("env_vars", {}).items():
        print(f"export {k}={v}")  # You can pipe this into `source <(python envsnap.py ...)`

def view_snapshot(name):
    path = snapshot_file(name)
    if not os.path.exists(path):
        print("❌ Snapshot not found.")
    else:
        with open(path) as f:
            data = json.load(f)
        print(f"\n📦 Snapshot: {name}")
        print(f"🕒 Timestamp: {data.get('timestamp')}")
        print(f"🐍 Python: {data.get('python_version')}")
        print(f"📁 Virtualenv: {data.get('virtualenv')}")
        print(f"🌿 Git Branch: {data.get('git_branch')}")
        print(f"🔑 Env Vars:")
        for k, v in data.get('env_vars', {}).items():
            print(f"   {k} = {v}")
        print(f"📦 Packages: {len(data.get('packages', []))} installed")
        for pkg in data.get('packages', [])[:10]:
            print(f"   - {pkg}")
        if len(data.get('packages', [])) > 10:
            print("   ... (truncated)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EnvSnap – Save and restore dev environments")
    subparsers = parser.add_subparsers(dest="command")

    save_cmd = subparsers.add_parser("save")
    save_cmd.add_argument("name", help="Snapshot name")

    list_cmd = subparsers.add_parser("list")

    restore_cmd = subparsers.add_parser("restore")
    restore_cmd.add_argument("name", help="Snapshot name")
    restore_cmd.add_argument("--env-vars", action="store_true", help="Restore environment variables")

    view_cmd = subparsers.add_parser("view")
    view_cmd.add_argument("name", help="Snapshot name to view")

    args = parser.parse_args()

    if args.command == "save":
        save_snapshot(args.name)
    elif args.command == "list":
        list_snapshots()
    elif args.command == "restore":
        if args.env_vars:
            restore_env_vars(args.name)
        else:
            print("⚠️ Add --env-vars to restore environment variables")
    elif args.command == "view":
        view_snapshot(args.name)
    else:
        parser.print_help()

