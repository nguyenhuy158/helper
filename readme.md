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
| `all`   | Show all info                     | `helper all`         |

Use `-v` for verbose output (e.g., `helper ip -v`).

Each command also prints the shell command it runs to get the result.

### 🔄 Upgrade

```bash
pip install --upgrade helper
```

---

### 🧑‍💻 Contribute

Pull requests are welcome!
Repo: [https://github.com/nguyenhuy158/helper](https://github.com/nguyenhuy158/helper)
