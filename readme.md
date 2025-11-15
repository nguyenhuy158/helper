# 📦 Helper CLI

A simple command-line tool to show system info (IP, CPU arch, etc.) and the commands used to get them.

---

### 🚀 Install

```bash
pip install helper
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

```bash
pip install --upgrade helper
```

---

### 🧑‍💻 Contribute

Pull requests are welcome!

Before submitting a PR, ensure your code passes pylint checks and tests:
```bash
make lint
make test
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
