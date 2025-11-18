import subprocess
import os
import sys
import re

# Configuration colors for the prompt
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    GRAY = '\033[90m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class UnifiedShell:
    def __init__(self):
        self.mode = "cmd"  # Default mode
        self.running = True
        self.history = []  # internal history storage
        os.system('') # Enable ANSI colors

    def get_prompt(self):
        cwd = os.getcwd()
        if self.mode == "cmd":
            mode_str = f"{Colors.BLUE}[CMD]{Colors.ENDC}"
        elif self.mode == "ps":
            mode_str = f"{Colors.YELLOW}[PS]{Colors.ENDC}"
        elif self.mode == "wsl":
            mode_str = f"{Colors.GREEN}[WSL]{Colors.ENDC}"
        else:
            mode_str = f"[{self.mode}]"
        
        return f"\n{mode_str} {cwd} > "

    def smart_translate(self, cmd_str, current_mode):
        """
        Intercepts commands to provide Unified behavior:
        1. Networking (traceroute, ifconfig)
        2. Polyfills (uptime, uname)
        3. Auto-Sensing PowerShell
        4. Linux -> DOS translation (ls, cp, mv, rm, cat, etc.)
        """
        parts = cmd_str.strip().split()
        if not parts:
            return cmd_str, False

        base = parts[0].lower()
        
        # --- 1. Networking Commands ---
        if base == 'ifconfig':
            if '-a' in cmd_str or '/all' in cmd_str: return 'ipconfig /all', True
            return 'ipconfig', True

        if base == 'ip':
            if len(parts) > 1:
                subcmd = parts[1].lower()
                if subcmd in ['a', 'addr', 'address']: return 'ipconfig', True
                if subcmd in ['r', 'route']: return 'route print', True
                if subcmd in ['n', 'neigh', 'neighbor']: return 'arp -a', True
            return 'ipconfig', True

        # --- 2. Polyfills & Direct Mappings ---
        if base in ['uptime', 'get-uptime']:
            polyfill = (
                'powershell -NoProfile -Command "'
                '$os = Get-CimInstance Win32_OperatingSystem; '
                '$uptime = (Get-Date) - $os.LastBootUpTime; '
                'Write-Host \\"Uptime: $($uptime.Days) days, $($uptime.Hours) hours, $($uptime.Minutes) minutes\\""'
            )
            return polyfill, True

        if base == 'uname':
            return "ver", True
            
        if base == 'sudo' and len(parts) > 1:
            print(f"{Colors.GRAY}(Ignoring 'sudo' on Windows...){Colors.ENDC}")
            return " ".join(parts[1:]), True

        # --- 3. Heuristic: Auto-Sense PowerShell ---
        if current_mode == "cmd":
            if re.match(r'^[a-zA-Z]+-[a-zA-Z]+', parts[0]):
                print(f"{Colors.GRAY}(Routing '{parts[0]}' to PowerShell...){Colors.ENDC}")
                return f'powershell -NoProfile -Command "{cmd_str}"', True

        # --- 4. Translation: Linux to DOS (Only in CMD mode) ---
        if current_mode == "cmd":
            aliases = {
                'ls':         ('dir', True),
                'll':         ('dir', True), 
                'clear':      ('cls', False),
                'pwd':        ('cd', False),
                'cp':         ('copy', False),
                'mv':         ('move', False),
                'rm':         ('del', False),
                'cat':        ('type', False),
                'grep':       ('findstr', False),
                'man':        ('help', False),
                'whoami':     ('echo %USERNAME%', False),
                'touch':      ('type nul >>', False),
                'which':      ('where', False),
                'traceroute': ('tracert', False),
                'dig':        ('nslookup', False),
                'kill':       ('taskkill /F /PID', False),
                'ps':         ('tasklist', False)
            }

            if base in aliases:
                target_cmd, complex_flags = aliases[base]
                if complex_flags:
                    new_parts = [target_cmd]
                    for arg in parts[1:]:
                        if arg.startswith('-'):
                            flag_map = ""
                            if 'a' in arg: flag_map += " /a"
                            if 'R' in arg or 'r' in arg: flag_map += " /s"
                            if flag_map: new_parts.append(flag_map.strip())
                        else:
                            new_parts.append(arg)
                    return " ".join(new_parts), True
                else:
                    parts[0] = target_cmd
                    return " ".join(parts), True

        return cmd_str, False

    def run_cmd(self, command):
        try:
            subprocess.run(command, shell=True)
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.ENDC}")

    def run_powershell(self, command):
        try:
            cmd_list = ["powershell", "-NoProfile", "-Command", command]
            subprocess.run(cmd_list, shell=False)
        except FileNotFoundError:
            print(f"{Colors.RED}Error: PowerShell not found.{Colors.ENDC}")

    def run_wsl(self, command):
        try:
            cmd_list = ["wsl", "bash", "-c", command]
            subprocess.run(cmd_list, shell=False)
        except FileNotFoundError:
            print(f"{Colors.RED}Error: WSL not found.{Colors.ENDC}")

    def change_directory(self, path):
        try:
            if path == "~":
                path = os.path.expanduser("~")
            os.chdir(path)
        except FileNotFoundError:
            print(f"{Colors.RED}Path '{path}' not found.{Colors.ENDC}")

    def show_history(self):
        print(f"{Colors.BOLD}--- Session History ---{Colors.ENDC}")
        for i, cmd in enumerate(self.history):
            print(f"{i+1}: {cmd}")

    def parse_and_execute(self, user_input):
        user_input = user_input.strip()
        if not user_input: return

        # Record history (internal)
        self.history.append(user_input)

        parts = user_input.split(" ", 1)
        base_cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        # --- Internal Commands ---
        if base_cmd in ["exit", "quit"]:
            self.running = False
            return
        if base_cmd == "cd":
            if args: self.change_directory(args)
            else: print(os.getcwd())
            return
        if base_cmd == "history":
            self.show_history()
            return
        if base_cmd == "mode":
            if args.lower() in ["cmd", "dos"]: self.mode = "cmd"
            elif args.lower() in ["ps", "powershell"]: self.mode = "ps"
            elif args.lower() in ["wsl", "linux"]: self.mode = "wsl"
            else: print(f"Current mode: {self.mode}")
            return

        # --- Execution Logic ---
        target_mode = self.mode
        clean_cmd = user_input

        # 1. Prefix Overrides
        if ':' in base_cmd:
             prefix, rest = user_input.split(':', 1)
             prefix = prefix.lower()
             if prefix in ['c', 'cmd']: target_mode = 'cmd'; clean_cmd = rest.strip()
             elif prefix in ['p', 'ps']: target_mode = 'ps'; clean_cmd = rest.strip()
             elif prefix in ['w', 'l', 'wsl']: target_mode = 'wsl'; clean_cmd = rest.strip()

        # 2. Smart Translation
        if target_mode in ['cmd', 'ps']:
            translated_cmd, was_translated = self.smart_translate(clean_cmd, target_mode)
            
            if was_translated:
                # Handle recursion (sudo -> ip -> ifconfig)
                if any(clean_cmd.lower().startswith(x) for x in ["sudo ", "ip "]):
                     translated_cmd, _ = self.smart_translate(translated_cmd, target_mode)

                if "powershell" in translated_cmd.lower() and target_mode == "cmd":
                    self.run_cmd(translated_cmd) 
                    return
                else:
                    clean_cmd = translated_cmd

        # 3. Execution
        if target_mode == "cmd":
            self.run_cmd(clean_cmd)
        elif target_mode == "ps":
            self.run_powershell(clean_cmd)
        elif target_mode == "wsl":
            self.run_wsl(clean_cmd)

    def start(self):
        print(f"{Colors.BOLD}Unified Shell v8.0{Colors.ENDC}")
        print("Try: 'history', 'uptime', 'ifconfig', 'traceroute', 'ls'")
        
        while self.running:
            try:
                user_input = input(self.get_prompt())
                self.parse_and_execute(user_input)
            except KeyboardInterrupt:
                print("\nType 'exit' to quit.")

if __name__ == "__main__":
    shell = UnifiedShell()
    shell.start()
