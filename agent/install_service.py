"""
Helper to register the agent as a system service.

Linux:   python -m agent.install_service --systemd
         (writes /etc/systemd/system/soc-agent.service and prints enable/start)
Windows: python -m agent.install_service --windows
         (prints NSSM commands; NSSM is required: https://nssm.cc)
"""

import argparse
import os
import sys
from pathlib import Path

SYSTEMD_UNIT = """[Unit]
Description=SOC Endpoint Detection Agent
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart={python} -m agent
WorkingDirectory={workdir}
Restart=on-failure
RestartSec=5
Environment=PYTHONUNBUFFERED=1
# Environment=AGENT_CONFIG=/etc/soc-agent/agent_config.yaml

[Install]
WantedBy=multi-user.target
"""

WINDOWS_NSSM = """\
:: Run from an elevated command prompt with NSSM (https://nssm.cc) in PATH.
nssm install soc-agent {python} -m agent
nssm set soc-agent AppDirectory "{workdir}"
nssm set soc-agent AppStdout "{workdir}\\logs\\service.out.log"
nssm set soc-agent AppStderr "{workdir}\\logs\\service.err.log"
nssm set soc-agent Start SERVICE_AUTO_START
nssm start soc-agent
"""


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Register the SOC agent as a system service")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--systemd", action="store_true", help="Linux: write a systemd unit")
    group.add_argument("--windows", action="store_true", help="Windows: print NSSM commands")
    args = parser.parse_args(argv)

    python = sys.executable
    workdir = str(Path(__file__).resolve().parent.parent)

    if args.systemd:
        if os.name != "posix":
            print("systemd is only supported on Linux.", file=sys.stderr)
            return 1
        unit = SYSTEMD_UNIT.format(python=python, workdir=workdir)
        target = Path("/etc/systemd/system/soc-agent.service")
        try:
            target.write_text(unit)
        except PermissionError:
            print("Permission denied writing", target)
            print("Run as root, or install manually with:\n")
            print(unit)
            return 1
        print("Wrote", target)
        print("Enable & start with:")
        print("  sudo systemctl daemon-reload")
        print("  sudo systemctl enable --now soc-agent")
        return 0

    if args.windows:
        print(WINDOWS_NSSM.format(python=python, workdir=workdir))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())