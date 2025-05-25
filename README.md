# 🧠 EnvSnap – Terminal-Based Environment Snapshot Tool

**EnvSnap** is a simple Python CLI tool for capturing, viewing, and restoring your local development environment — including Python version, virtual environment, installed packages, Git branch, and selected environment variables.

It’s like a time machine for your dev setup.


## 🔧 Features

- 📸 Save a snapshot of:
  - Python version
  - Virtual environment
  - Installed packages (`pip freeze`)
  - Current Git branch
  - Key environment variables (`PATH`, `DEBUG`, `API_KEY`, `SECRET_KEY`)
- 🔍 View a snapshot before restoring it
- 🧾 List all saved snapshots
- ✅ Restore environment variables from a snapshot
  

## 🚀 Usage

## Save a snapshot

```bash
envsnap save my-project-setup
```

## View a snapshot

```bash
envsnap view my-project-setup
```

## Restore environment variables

```bash
source <(envsnap restore my-project-setup --env-vars)
```

## List all saved snapshots

```bash
envsnap list
```

# 📂 Snapshot Storage

Snapshots are saved as `.json` files in:

```bash
~/.envsnap/
```

Each file contains environment metadata under the name you give it.

# 🤖 What It Captures

* Python version (e.g., `3.11.2`)
* Virtual environment path
* Output of `pip freeze`
* Current Git branch
* Key environment variables

# 🔐 Security Note

Environment variables may include sensitive values like API keys or tokens. Use caution when sharing snapshot files.

# 🛣 Roadmap Ideas

* Auto-restore pip packages
* Snapshot comparison (`diff`)
* Docker/container info capture
* Export to `.env` or Markdown

# 📄 License

Licensed under the Apache License, Version 2.0.
