# 📦 Helper CLI

A simple command-line tool to show system info (IP, CPU arch, etc.) and the commands used to get them.

---

### 🚀 Install

With [uv](https://docs.astral.sh/uv/) (recommended):

```bash
uv tool install helper-cli
```

Or run without installing:

```bash
uvx --from helper-cli helper ip
```

With pip:

```bash
pip install helper-cli
```

---

### 🧠 Usage

```bash
helper [command]
```

#### Available commands:

| Command | Description                       | Example              |
| ------- | --------------------------------- | -------------------- |
| `ip`    | Show internal IP                  | `helper ip`          |
| `pubip` | Show public IP                    | `helper pubip`       |
| `arch`  | Show CPU architecture (arm / amd) | `helper arch`        |
| `si`    | Show system information           | `helper si`          |
| `nix`   | Show NixOS information            | `helper nix`         |
| `d`     | Show Docker information           | `helper d`           |
| `sp`    | Show speed test results           | `helper sp`          |
| `v`     | Show virtual environment info     | `helper v`           |
| `f`     | Show file information             | `helper f`           |
| `env`   | Show environment variables        | `helper env`         |
| `run`   | Run command snippets              | `helper run`         |
| `kill`  | Kill processes by name or port    | `helper kill <name>` |
| `disk`  | Show disk usage, mount, and list info | `helper disk usage`  |
| `journalctl` | Show useful journalctl options and examples | `helper journalctl` |
| `tools` | List other tools by the same author | `helper tools`       |
| `odoo`  | Download click-odoo scripts to current dir | `helper odoo`   |
| `all`   | Show all info                     | `helper all`         |

Use `-v` for verbose output (e.g., `helper ip -v`).

Each command also prints the shell command it runs to get the result.

### 📚 Library Usage

You can import and use helper functions programmatically:

```python
import helper

# Get disk usage information
usage = helper.disk.get_usage()
print(usage)

# Get system information as dict
info = helper.system_info.get_info()
print(f"System: {info['system']['system']}")
print(f"CPU: {info['cpu']['cpu']}")

# Get internal IP
ip = helper.internal_ip.get_internal_ip()
print(f"Internal IP: {ip}")

# Get public IP
pub_ip = helper.public_ip.get_public_ip()
print(f"Public IP: {pub_ip}")

# Get architecture
arch = helper.arch.get_arch()
print(f"Architecture: {arch}")

# Get all info
all_info = helper.all_info.get_info()
print(all_info)
```

### 🔄 Upgrade

With uv:

```bash
uv tool upgrade helper-cli
```

With pip:

```bash
pip install --upgrade helper-cli
```

---

### 🧑‍💻 Contribute

Pull requests are welcome!

Set up a development environment with uv:

```bash
uv venv
uv pip install -e ".[dev]"
```

Or with pip:

```bash
pip install -e ".[dev]"
```

Before submitting a PR, ensure your code passes lint checks and tests:
```bash
make lint
make test
```

With uv you can also run them directly:

```bash
uv run --extra dev ruff check .
uv run --extra dev pytest
```

#### Testing

Run the test suite:
```bash
make test
```

Or run pytest directly:
```bash
pytest
```

Tests are located in the `tests/` directory. For detailed testing guidelines and conventions, see `src_docs/testing.md`.

Repo: [https://github.com/nguyenhuy158/helper](https://github.com/nguyenhuy158/helper)
