"""CLI entry point for gdlex-inspector."""

from __future__ import annotations

import argparse
import json
import os
import sys

from . import __version__
from .backend import choose_backend
from .platform_info import get_platform_summary
from .report import _fmt_size, to_csv, to_html, to_json
from .risk import risk_label_for_display, risk_style_for_display
from .scan_profiles import get_default_profiles, get_profile, resolve_target_path
from .scanner import parse_size, scan_directory
from .system_profile import detect_system_profile


BANNER = "GD LEX Inspector v{version} — Diagnostic read-only disk inspection tool"
READONLY_NOTICE = "[READ-ONLY] No files were modified or deleted."


def _print_result(result, top_n: int) -> None:
    print()
    print(f"  Path:     {result.root_path}")
    print(f"  Total:    {_fmt_size(result.total_size)}")
    print(f"  Files:    {result.total_files}")
    print(f"  Dirs:     {result.total_dirs}")
    if result.issues:
        print(f"  Skipped:  {len(result.issues)} paths (permission denied or errors)")
    print()

    if result.top_files:
        print(f"  Top {len(result.top_files)} files by size:")
        for i, f in enumerate(result.top_files, 1):
            label = risk_label_for_display(f.risk_level, f.category, f.path, f.size)
            style = risk_style_for_display(f.risk_level, f.category, f.path, f.size)
            risk = f" [{label}]" if style not in ("none", "low") else ""
            print(f"    {i:>3}. {_fmt_size(f.size):>10}  {f.path}{risk}")
    print()

    if result.top_dirs:
        print(f"  Top {len(result.top_dirs)} directories by size:")
        for i, d in enumerate(result.top_dirs, 1):
            label = risk_label_for_display(d.risk_level, d.category, d.path, d.size)
            style = risk_style_for_display(d.risk_level, d.category, d.path, d.size)
            risk = f" [{label}]" if style not in ("none", "low") else ""
            print(f"    {i:>3}. {_fmt_size(d.size):>10}  {d.path}{risk}")
    print()

    if result.categories:
        print("  Categories:")
        for c in result.categories:
            print(f"    {c.category:<30} {_fmt_size(c.total_size):>10}  ({c.file_count} files)")
    print()

    if result.extensions:
        print("  Top 10 extensions:")
        for e in result.extensions[:10]:
            print(f"    {e.extension:<15} {_fmt_size(e.total_size):>10}  ({e.file_count} files)")
    print()

    print(f"  {READONLY_NOTICE}")


def cmd_gui(args: argparse.Namespace) -> int:
    from .gui import launch_gui
    return launch_gui(initial_path=getattr(args, "path", ""))


def cmd_version(args: argparse.Namespace) -> int:
    print(f"gdlex-inspector {__version__}")
    return 0


def cmd_system_info(args: argparse.Namespace) -> int:
    profile = detect_system_profile()
    if args.json:
        print(json.dumps(profile.to_dict(), indent=2, sort_keys=True))
        return 0

    print("GD LEX Inspector — System info")
    print()
    print(f"OS: {profile.os_family}")
    print(f"Platform: {profile.platform}")
    print(f"WSL: {'yes' if profile.is_wsl else 'no'}")
    print(f"Desktop: {profile.desktop_environment or 'unknown'}")
    print(f"Host: {profile.hostname or 'unknown'}")
    print()
    print("Mount rilevati:")
    if not profile.mounts:
        print("- none")
    for mount in profile.mounts:
        access = "ro" if mount.is_read_only else "rw"
        print(
            f"- {mount.mount_point:<28} {mount.fs_type:<12} "
            f"{mount.role:<14} {access}"
        )
    return 0


def cmd_profiles(args: argparse.Namespace) -> int:
    profiles = get_default_profiles()
    if args.json:
        print(json.dumps([profile.to_dict() for profile in profiles], indent=2))
        return 0

    print("Profili di scansione disponibili:")
    for profile in profiles:
        depth = "completa" if profile.max_depth is None else str(profile.max_depth)
        print(f"- {profile.id:<20} {profile.label:<20} {profile.estimated_speed}")
        print(
            f"  target: {profile.target_path} | profondita: {depth} | "
            f"top: {profile.top}"
        )
        if profile.caution:
            print(f"  attenzione: {profile.caution}")
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    scan_profile = None
    if args.profile:
        scan_profile = get_profile(args.profile)
        if scan_profile is None:
            available = ", ".join(
                profile.id for profile in get_default_profiles()
            )
            print(
                f"Error: unknown scan profile {args.profile!r}. "
                f"Available profiles: {available}",
                file=sys.stderr,
            )
            return 2

    path = args.path or (scan_profile.target_path if scan_profile else None)
    if path is None:
        print("Error: a path or --profile is required.", file=sys.stderr)
        return 2
    path = resolve_target_path(path)
    if not os.path.exists(path):
        print(f"Error: path does not exist: {path!r}", file=sys.stderr)
        return 1
    if not os.path.isdir(path):
        print(f"Error: path is not a directory: {path!r}", file=sys.stderr)
        return 1

    min_size = scan_profile.min_size if scan_profile else 0
    if args.min_size is not None:
        try:
            min_size = parse_size(args.min_size)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    top = args.top if args.top is not None else (
        scan_profile.top if scan_profile else 10
    )
    max_depth = args.max_depth if args.max_depth is not None else (
        scan_profile.max_depth if scan_profile else None
    )
    follow_symlinks = (
        args.follow_symlinks
        if args.follow_symlinks is not None
        else (scan_profile.follow_symlinks if scan_profile else False)
    )
    exclude = (
        list(args.exclude)
        if args.exclude is not None
        else (list(scan_profile.excludes) if scan_profile else [])
    )
    backend = choose_backend(getattr(args, "backend", None))

    print(BANNER.format(version=__version__))
    if scan_profile:
        print(f"  Profile:  {scan_profile.id} ({scan_profile.label})")
    print(f"  Scanning: {os.path.abspath(path)}")
    print("  Please wait...", flush=True)

    result = scan_directory(
        root=path,
        top_n=top,
        min_size=min_size,
        max_depth=max_depth,
        follow_symlinks=follow_symlinks,
        exclude_patterns=exclude,
    )
    result.backend_used = backend
    result.platform_info = get_platform_summary()

    _print_result(result, top)

    if args.json:
        json_path = args.json
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(to_json(result))
        print(f"  JSON report saved: {json_path}")

    if args.html:
        html_path = args.html
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(to_html(result))
        print(f"  HTML report saved: {html_path}")

    if args.csv:
        csv_path = args.csv
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            f.write(to_csv(result))
        print(f"  CSV report saved: {csv_path}")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gdlex-inspector",
        description=(
            "GD LEX Inspector — Multiplatform disk inspection and prudential reporting.\n"
            "READ-ONLY: no files are modified or deleted."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("version", help="Print version and exit.")

    system_p = sub.add_parser(
        "system-info",
        help="Detect the operating system, environment, and mounted filesystems.",
    )
    system_p.add_argument(
        "--json", action="store_true",
        help="Print the system profile as JSON.",
    )

    profiles_p = sub.add_parser(
        "profiles",
        help="List scan profiles suited to the current system.",
    )
    profiles_p.add_argument(
        "--json", action="store_true",
        help="Print scan profiles as JSON.",
    )

    gui_p = sub.add_parser("gui", help="Launch the graphical interface (requires PySide6).")
    gui_p.add_argument(
        "--path", default="", metavar="DIR",
        help="Pre-fill the path field with this directory.",
    )

    scan_p = sub.add_parser("scan", help="Scan a directory and report disk usage.")
    scan_p.add_argument("path", nargs="?", help="Directory to scan.")
    scan_p.add_argument("--profile", metavar="ID",
                        help="Use defaults from a scan profile.")
    scan_p.add_argument("--top", type=int, default=None, metavar="N",
                        help="Number of top files/dirs to show (default: 10).")
    scan_p.add_argument("--min-size", metavar="SIZE",
                        help="Minimum file size to include in top list (e.g. 100M).")
    scan_p.add_argument("--max-depth", type=int, default=None, metavar="N",
                        help="Maximum directory depth to recurse into.")
    scan_p.add_argument("--json", metavar="PATH", default=None,
                        help="Export JSON report to this path.")
    scan_p.add_argument("--html", metavar="PATH", default=None,
                        help="Export HTML report to this path.")
    scan_p.add_argument("--csv", metavar="PATH", default=None,
                        help="Export CSV report to this path.")
    scan_p.add_argument("--exclude", metavar="PATTERN", action="append",
                        help="Exclude paths matching this glob pattern (repeatable).")
    scan_p.add_argument("--follow-symlinks", action="store_true", default=None,
                        help="Follow symbolic links (disabled by default).")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0
    if args.command == "version":
        return cmd_version(args)
    if args.command == "system-info":
        return cmd_system_info(args)
    if args.command == "profiles":
        return cmd_profiles(args)
    if args.command == "scan":
        return cmd_scan(args)
    if args.command == "gui":
        return cmd_gui(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
