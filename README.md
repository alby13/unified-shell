# 🔄 Unified Shell (Polyglot Terminal)
Execute Windows DOS, PowerShell, and Linxu (bash) commands in one place. Designed for Windows environment.

> **Stop fighting your muscle memory.** Use the commands you know, on the operating system you have.

![Platform](https://img.shields.io/badge/platform-Win%20%7C%20Linux%20%7C%20Mac-lightgrey)

## 💡 The Concept

Developers and SysAdmins rarely stick to one operating system. We switch between Windows servers, Linux distributions, and local environments constantly. 

The problem? **Context switching.** - You type `ls` in Command Prompt and get an error.
- You type `dir` in Bash and look like a novice.
- You try to `grep` logs in PowerShell and realize you need `Select-String`.

**[Program Name]** is a lightweight compatibility layer that detects the command you *intended* to use and translates it to the command the current operating system *understands*.

---

## 🚀 How It Works

[Program Name] sits between your input and the system shell. It parses your command, identifies the syntax (DOS, Bash, or PowerShell), and executes the native equivalent in real-time.

### The Workflow:
1. **Input:** You type a command (e.g., `rm -rf ./build` on Windows).
2. **Detection:** [Program Name] identifies this as a Linux/Bash syntax.
3. **Translation:** It maps the arguments to the Windows equivalent (`Remove-Item -Recurse -Force ./build`).
4. **Execution:** The action is performed natively.

---

## 📦 Python File

```
Run unified-shell.py
```


## ⚡ Usage Examples
You don't need to learn new syntax. Just run Unified Shell (or set it as your default shell entry point).

## ⚙️ Configuration
You can map custom aliases or override default translations in the config.json file:

JSON

{
  "mappings": {
    "ll": "ls -la",
    "reboot": "shutdown -r now"
  },
  "safetyMode": true
}

## 🤝 Contributing
We can't cover every edge case in every CLI alone. If you find a command that doesn't translate correctly:

Fork the repo.

Add the missing mapping to src/translations.map.
