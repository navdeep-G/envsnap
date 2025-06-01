# __main__.py – Entry point for envsnap CLI tool with automatic setup and autocompletion

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime
from difflib import get_close_matches, unified_diff

SNAPSHOT_DIR = os.path.expanduser("~/.envsnap")
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

BASH_COMPLETION_SCRIPT = os.path.expanduser("~/.envsnap_completion.bash")

COMMANDS_REQUIRING_SNAPSHOT = ["view", "restore"]


def write_bash_completion_script():
    script_content = f"""#!/bin/bash
_envsnap_complete() {{
    local curr_arg prev_arg
    curr_arg="${{COMP_WORDS[COMP_CWORD]}}"
    prev_arg="${{COMP_WORDS[COMP_CWORD-1]}}"

    if [[ "$prev_arg" == "view" || "$prev_arg" == "restore" || "$prev_arg" == "diff" || "$prev_arg" == "report" ]]; then
        local snapshots=$(cd {SNAPSHOT_DIR} 2>/dev/null && ls *.json | sed 's/\\.json$//')
        COMPREPLY=($(compgen -W "$snapshots" -- "$curr_arg"))
    fi
}}

complete -o default -F _envsnap_complete envsnap
"""
    with open(BASH_COMPLETION_SCRIPT, "w") as f:
        f.write(script_content)
    os.chmod(BASH_COMPLETION_SCRIPT, 0o755)

    def append_source_line(shell_file):
        shell_path = os.path.expanduser(shell_file)
        bash_line = f"source {BASH_COMPLETION_SCRIPT}"
        if os.path.exists(shell_path):
            with open(shell_path, "r+") as f:
                content = f.read()
                if bash_line not in content:
                    f.write(f"\n# EnvSnap Autocompletion\n{bash_line}\n")
        else:
            with open(shell_path, "w") as f:
                f.write(f"# EnvSnap Autocompletion\n{bash_line}\n")

    append_source_line("~/.bashrc")
    append_source_line("~/.bash_profile")

    print("✅ Bash autocompletion installed.")
    print("👉 Restart your terminal or run: source ~/.bash_profile")


def snapshot_file(name):
    return os.path.join(SNAPSHOT_DIR, f"{name}.json")


def get_available_snapshots():
    return [f[:-5] for f in os.listdir(SNAPSHOT_DIR) if f.endswith(".json")]


def resolve_snapshot_name(name):
    matches = get_close_matches(name, get_available_snapshots(), n=1, cutoff=0.3)
    return matches[0] if matches else name


def load_snapshot(name):
    path = snapshot_file(name)
    if not os.path.exists(path):
        print(f"❌ Snapshot '{name}' not found.")
        sys.exit(1)
    with open(path) as f:
        return json.load(f)


def get_env_vars():
    return dict(os.environ)


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
    resolved_name = resolve_snapshot_name(name)
    path = snapshot_file(resolved_name)
    if not os.path.exists(path):
        print("❌ Snapshot not found.")
        return
    with open(path) as f:
        data = json.load(f)
    for k, v in data.get("env_vars", {}).items():
        print(f"export {k}={v}")


def view_snapshot(name):
    resolved_name = resolve_snapshot_name(name)
    path = snapshot_file(resolved_name)
    if not os.path.exists(path):
        print("❌ Snapshot not found.")
    else:
        with open(path) as f:
            data = json.load(f)
        print(f"\n📦 Snapshot: {resolved_name}")
        print(f"🕒 Timestamp: {data.get('timestamp')}")
        print(f"🐍 Python: {data.get('python_version')}")
        print(f"📁 Virtualenv: {data.get('virtualenv')}")
        print(f"🌿 Git Branch: {data.get('git_branch')}")
        print("🔑 Env Vars:")
        for k, v in data.get('env_vars', {}).items():
            print(f"   {k} = {v}")
        print(f"📦 Packages: {len(data.get('packages', []))} installed")
        for pkg in data.get('packages', [])[:10]:
            print(f"   - {pkg}")
        if len(data.get('packages', [])) > 10:
            print("   ... (truncated)")


def compare_snapshots(name1, name2):
    snap1 = load_snapshot(resolve_snapshot_name(name1))
    snap2 = load_snapshot(resolve_snapshot_name(name2))

    def flatten_snapshot(data):
        flattened = {}
        for key, value in data.items():
            if key == "packages":
                flattened.update({f"package:{pkg}": "installed" for pkg in value})
            elif isinstance(value, dict):
                flattened.update({f"{key}:{k}": v for k, v in value.items()})
            else:
                flattened[key] = value
        return flattened

    flat1 = flatten_snapshot(snap1)
    flat2 = flatten_snapshot(snap2)

    all_keys = sorted(set(flat1.keys()) | set(flat2.keys()))

    print(f"\n🔍 Comparing snapshots '{name1}' vs '{name2}':\n")
    differences_found = False
    for key in all_keys:
        val1 = flat1.get(key, "<missing>")
        val2 = flat2.get(key, "<missing>")
        if val1 != val2:
            differences_found = True
            print(f"🔸 {key}\n   - {name1}: {val1}\n   - {name2}: {val2}\n")

    if not differences_found:
        print("✅ No differences found.")


def report_snapshot(name):
    data = load_snapshot(resolve_snapshot_name(name))
    print(f"\n📋 Summary Report for '{name}'")
    print("----------------------------")
    print(f"📅 Timestamp       : {data.get('timestamp')}")
    print(f"🐍 Python Version  : {data.get('python_version')}")
    print(f"🌿 Git Branch      : {data.get('git_branch')}")
    print(f"📁 Virtualenv Path : {data.get('virtualenv')}")
    print(f"🔑 Env Vars Count  : {len(data.get('env_vars', {}))}")
    print(f"📦 Package Count   : {len(data.get('packages', []))}")
    print("📦 Top Packages    :")
    for pkg in data.get('packages', [])[:10]:
        print(f"   - {pkg}")
    if len(data.get('packages', [])) > 10:
        print("   ... (truncated)")


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--setup-completion":
        write_bash_completion_script()
        return

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

    diff_cmd = subparsers.add_parser("diff")
    diff_cmd.add_argument("snap1", help="First snapshot name")
    diff_cmd.add_argument("snap2", help="Second snapshot name")

    report_cmd = subparsers.add_parser("report")
    report_cmd.add_argument("name", help="Snapshot name to summarize")

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
    elif args.command == "diff":
        compare_snapshots(args.snap1, args.snap2)
    elif args.command == "report":
        report_snapshot(args.name)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

