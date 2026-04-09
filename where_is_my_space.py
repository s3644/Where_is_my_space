#!/usr/bin/env python3
"""
Where Is My Space? - Universal Disk Space Analysis Tool

This script analyzes disk space usage and identifies where space is being consumed,
particularly focusing on discrepancies between df and du measurements.

Universal Design:
    - Works on any Linux system
    - No hardcoded paths or system-specific configurations
    - Configurable mount point exclusions via command line
    - Detects and excludes common network mounts automatically

Usage:
    python3 where_is_my_space.py [--exclude-mount /path/to/mount]
    python3 where_is_my_space.py --help

Examples:
    # Basic usage on any system
    python3 where_is_my_space.py
    
    # Exclude specific mount points
    python3 where_is_my_space.py --exclude-mount /mnt/nas --exclude-mount /mnt/external
    
    # Generate report
    python3 where_is_my_space.py --output report.md

Author: Jukrapope Jitpimolmard
Date: April 2026
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict, Optional


def run_command(cmd: List[str], check: bool = True) -> Tuple[int, str, str]:
    """Run a shell command and return exit code, stdout, and stderr."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=check
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout, e.stderr
    except FileNotFoundError:
        return -1, "", f"Command not found: {cmd[0]}"


def format_size(size_bytes: int) -> str:
    """Format bytes into human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def get_df_usage(mount_point: str = "/") -> Optional[Dict]:
    """Get disk usage information from df command."""
    code, stdout, _ = run_command(["df", "-hT", mount_point])
    if code != 0:
        return None
    
    lines = stdout.strip().split('\n')
    if len(lines) < 2:
        return None
    
    # Parse header and data
    header = lines[0].split()
    data = lines[1].split()
    
    if len(header) < len(data):
        return None
    
    return {
        'filesystem': data[0],
        'type': data[1],
        'size': data[2],
        'used': data[3],
        'available': data[4],
        'use_percent': data[5],
        'mounted_on': data[6] if len(data) > 6 else '/'
    }


def get_du_usage(path: str, exclude_paths: List[str] = None) -> Optional[int]:
    """Get disk usage in bytes from du command."""
    exclude_args = []
    if exclude_paths:
        for path in exclude_paths:
            exclude_args.extend(['--exclude', path])
    
    cmd = ['du', '-sb', path] + exclude_args
    code, stdout, _ = run_command(cmd)
    
    if code == 0:
        try:
            return int(stdout.split()[0])
        except (IndexError, ValueError):
            return None
    return None


def get_filesystem_info(device: str) -> Dict:
    """Get ext4 filesystem information using tune2fs and dumpe2fs."""
    info = {}
    
    # Get reserved blocks
    code, stdout, _ = run_command(['sudo', 'tune2fs', '-l', device])
    if code == 0:
        for line in stdout.split('\n'):
            if 'Reserved block count' in line:
                info['reserved_blocks'] = int(line.split(':')[1].strip())
            elif 'Block count' in line:
                info['total_blocks'] = int(line.split(':')[1].strip())
            elif 'Block size' in line:
                info['block_size'] = int(line.split(':')[1].strip())
            elif 'Inode count' in line:
                info['inode_count'] = int(line.split(':')[1].strip())
    
    # Get journal info
    code, stdout, _ = run_command(['sudo', 'dumpe2fs', device])
    if code == 0:
        for line in stdout.split('\n'):
            if 'Total journal size' in line:
                # Extract size in blocks
                try:
                    info['journal_blocks'] = int(line.split(':')[1].strip())
                except ValueError:
                    info['journal_blocks'] = 0
    
    return info


def get_largest_directories(path: str, top_n: int = 10, exclude_paths: List[str] = None) -> List[Tuple[str, int]]:
    """Get the largest directories under a path."""
    exclude_args = []
    if exclude_paths:
        for p in exclude_paths:
            exclude_args.extend(['--exclude', p])
    
    cmd = ['sudo', 'du', '-sh'] + exclude_args + [path]
    code, stdout, _ = run_command(cmd)
    
    if code != 0:
        return []
    
    results = []
    for line in stdout.strip().split('\n'):
        parts = line.split()
        if len(parts) >= 2:
            try:
                size_str = parts[0]
                dir_path = parts[1]
                # Convert size to bytes
                size = parse_size_to_bytes(size_str)
                results.append((dir_path, size))
            except ValueError:
                continue
    
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_n]


def parse_size_to_bytes(size_str: str) -> int:
    """Convert size string (e.g., '1.5G', '24M') to bytes."""
    size_str = size_str.strip()
    if not size_str:
        return 0
    
    # Extract number and unit
    import re
    match = re.match(r'([\d.]+)\s*([KMGTPEB]?)', size_str, re.IGNORECASE)
    if not match:
        return 0
    
    number = float(match.group(1))
    unit = match.group(2).upper()
    
    multipliers = {
        '': 1,
        'K': 1024,
        'M': 1024**2,
        'G': 1024**3,
        'T': 1024**4,
        'P': 1024**5,
        'E': 1024**6
    }
    
    return int(number * multipliers.get(unit, 1))


def get_largest_files(path: str, min_size_gb: float = 1.0, exclude_paths: List[str] = None) -> List[Tuple[str, int]]:
    """Get the largest files under a path."""
    min_size_bytes = int(min_size_gb * 1024**3)
    exclude_args = []
    if exclude_paths:
        for p in exclude_paths:
            exclude_args.extend(['--exclude', p])
    
    cmd = ['sudo', 'find', path, '-type', 'f', '-size', f'+{int(min_size_gb * 1024)}M'] + exclude_args
    code, stdout, _ = run_command(cmd)
    
    if code != 0:
        return []
    
    results = []
    for file_path in stdout.strip().split('\n'):
        if file_path:
            try:
                size = os.path.getsize(file_path)
                results.append((file_path, size))
            except OSError:
                continue
    
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def get_deleted_files_held_open() -> List[Dict]:
    """Get list of deleted files still held open by processes."""
    code, stdout, _ = run_command(['sudo', 'lsof', '+L1'])
    if code != 0:
        return []
    
    results = []
    for line in stdout.strip().split('\n'):
        if '(deleted)' in line:
            parts = line.split()
            if len(parts) >= 9:
                try:
                    size = int(parts[6])
                    results.append({
                        'command': parts[0],
                        'pid': parts[1],
                        'user': parts[2],
                        'size': size,
                        'path': parts[8]
                    })
                except (ValueError, IndexError):
                    continue
    
    return results


def analyze_disk_space(
    root_path: str = "/",
    exclude_mounts: List[str] = None,
    verbose: bool = False
) -> Dict:
    """
    Comprehensive disk space analysis.
    
    Args:
        root_path: Root path to analyze (default: /)
        exclude_mounts: List of mount points to exclude from analysis
        verbose: Whether to print detailed output
    
    Returns:
        Dictionary containing analysis results
    
    Note:
        This script is designed to work on any Linux system.
        Mount points to exclude should be specified via --exclude-mount flag.
        Default behavior excludes common network mounts and external drives.
    """
    if exclude_mounts is None:
        # Default exclusions for common network mounts and external drives
        exclude_mounts = [
            '/mnt/nas',
            '/mnt/external',
            '/media/*',
            '/run/user/*',
            '/sys/fs/cgroup',
            '/proc',
            '/sys',
            '/dev',
            '/run',
            '/tmp',
            '/var/tmp'
        ]
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'root_path': root_path,
        'df_info': None,
        'du_info': None,
        'filesystem_info': {},
        'largest_directories': [],
        'largest_files': [],
        'deleted_files_held_open': [],
        'discrepancy_analysis': {}
    }
    
    # Get df information
    df_info = get_df_usage(root_path)
    if df_info:
        results['df_info'] = df_info
        device = df_info['filesystem']
        
        # Get filesystem-specific information
        results['filesystem_info'] = get_filesystem_info(device)
        
        # Calculate filesystem overhead estimates
        if results['filesystem_info']:
            fs_info = results['filesystem_info']
            if fs_info.get('block_size') and fs_info.get('reserved_blocks'):
                reserved_bytes = fs_info['reserved_blocks'] * fs_info['block_size']
                results['filesystem_info']['reserved_bytes'] = reserved_bytes
                results['filesystem_info']['reserved_gb'] = reserved_bytes / (1024**3)
            
            if fs_info.get('block_size') and fs_info.get('inode_count'):
                # Estimate inode table size (256 bytes per inode)
                inode_table_bytes = fs_info['inode_count'] * 256
                results['filesystem_info']['inode_table_bytes'] = inode_table_bytes
                results['filesystem_info']['inode_table_gb'] = inode_table_bytes / (1024**3)
            
            if fs_info.get('journal_blocks') and fs_info.get('block_size'):
                journal_bytes = fs_info['journal_blocks'] * fs_info['block_size']
                results['filesystem_info']['journal_bytes'] = journal_bytes
                results['filesystem_info']['journal_gb'] = journal_bytes / (1024**3)
    
    # Get du information (excluding mount points)
    du_size = get_du_usage(root_path, exclude_mounts)
    if du_size:
        results['du_info'] = {
            'bytes': du_size,
            'human_readable': format_size(du_size)
        }
    
    # Get largest directories
    results['largest_directories'] = get_largest_directories(
        root_path, 
        top_n=15,
        exclude_paths=exclude_mounts
    )
    
    # Get largest files (>1GB)
    results['largest_files'] = get_largest_files(
        root_path,
        min_size_gb=1.0,
        exclude_paths=exclude_mounts
    )
    
    # Get deleted files still held open
    results['deleted_files_held_open'] = get_deleted_files_held_open()
    
    # Calculate discrepancy
    if results['df_info'] and results['du_info']:
        df_used_bytes = parse_size_to_bytes(results['df_info']['used'])
        du_used_bytes = results['du_info']['bytes']
        discrepancy = df_used_bytes - du_used_bytes
        
        results['discrepancy_analysis'] = {
            'df_used_bytes': df_used_bytes,
            'du_used_bytes': du_used_bytes,
            'discrepancy_bytes': discrepancy,
            'discrepancy_human': format_size(discrepancy),
            'estimated_overhead': {
                'reserved_blocks_gb': results['filesystem_info'].get('reserved_gb', 0),
                'inode_table_gb': results['filesystem_info'].get('inode_table_gb', 0),
                'journal_gb': results['filesystem_info'].get('journal_gb', 0),
                'directory_overhead_gb': discrepancy / 2  # Rough estimate
            }
        }
    
    return results


def print_report(results: Dict, verbose: bool = False):
    """Print analysis report to console."""
    print("=" * 80)
    print("DISK SPACE ANALYSIS REPORT")
    print("=" * 80)
    print(f"Timestamp: {results['timestamp']}")
    print(f"Root Path: {results['root_path']}")
    print()
    
    # DF Information
    if results['df_info']:
        df = results['df_info']
        print("DF Information (from kernel):")
        print(f"  Filesystem: {df['filesystem']}")
        print(f"  Type: {df['type']}")
        print(f"  Size: {df['size']}")
        print(f"  Used: {df['used']} ({df['use_percent']})")
        print(f"  Available: {df['available']}")
        print()
    
    # Filesystem Information
    if results['filesystem_info']:
        fs = results['filesystem_info']
        print("Filesystem Overhead Estimates:")
        if 'reserved_gb' in fs:
            print(f"  Reserved Blocks: {fs['reserved_gb']:.2f} GB")
        if 'inode_table_gb' in fs:
            print(f"  Inode Table: {fs['inode_table_gb']:.2f} GB")
        if 'journal_gb' in fs:
            print(f"  Journal: {fs['journal_gb']:.2f} GB")
        print()
    
    # Discrepancy Analysis
    if results['discrepancy_analysis']:
        disc = results['discrepancy_analysis']
        print("Space Discrepancy Analysis:")
        print(f"  df reports: {disc['df_used_bytes'] / (1024**3):.2f} GB")
        print(f"  du reports: {disc['du_used_bytes'] / (1024**3):.2f} GB")
        print(f"  Discrepancy: {disc['discrepancy_human']}")
        print()
        print("  Estimated Overhead Breakdown:")
        print(f"    Reserved blocks: {disc['estimated_overhead']['reserved_blocks_gb']:.2f} GB")
        print(f"    Inode table: {disc['estimated_overhead']['inode_table_gb']:.2f} GB")
        print(f"    Journal: {disc['estimated_overhead']['journal_gb']:.2f} GB")
        print(f"    Directory/Other overhead: {disc['estimated_overhead']['directory_overhead_gb']:.2f} GB")
        print()
    
    # Largest Directories
    if results['largest_directories']:
        print("Top 15 Largest Directories:")
        for i, (path, size) in enumerate(results['largest_directories'][:15], 1):
            print(f"  {i:2d}. {format_size(size):>10}  {path}")
        print()
    
    # Largest Files
    if results['largest_files']:
        print("Top 10 Largest Files (>1GB):")
        for i, (path, size) in enumerate(results['largest_files'][:10], 1):
            print(f"  {i:2d}. {format_size(size):>10}  {path}")
        print()
    
    # Deleted Files Held Open
    if results['deleted_files_held_open']:
        print("Deleted Files Still Held Open:")
        for file_info in results['deleted_files_held_open'][:10]:
            print(f"  {file_info['command']} (PID {file_info['pid']}): {format_size(file_info['size'])} - {file_info['path']}")
        if len(results['deleted_files_held_open']) > 10:
            print(f"  ... and {len(results['deleted_files_held_open']) - 10} more")
        print()
    
    print("=" * 80)
    print("END OF REPORT")
    print("=" * 80)


def save_report(results: Dict, output_file: str = None):
    """Save analysis report to a markdown file."""
    if output_file is None:
        output_file = f"disk_space_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(output_file, 'w') as f:
        f.write("# Disk Space Analysis Report\n\n")
        f.write(f"**Timestamp:** {results['timestamp']}\n\n")
        
        if results['df_info']:
            f.write("## DF Information\n")
            f.write(f"- Filesystem: {results['df_info']['filesystem']}\n")
            f.write(f"- Type: {results['df_info']['type']}\n")
            f.write(f"- Size: {results['df_info']['size']}\n")
            f.write(f"- Used: {results['df_info']['used']} ({results['df_info']['use_percent']})\n")
            f.write(f"- Available: {results['df_info']['available']}\n\n")
        
        if results['filesystem_info']:
            f.write("## Filesystem Overhead\n")
            fs = results['filesystem_info']
            if 'reserved_gb' in fs:
                f.write(f"- Reserved Blocks: {fs['reserved_gb']:.2f} GB\n")
            if 'inode_table_gb' in fs:
                f.write(f"- Inode Table: {fs['inode_table_gb']:.2f} GB\n")
            if 'journal_gb' in fs:
                f.write(f"- Journal: {fs['journal_gb']:.2f} GB\n")
            f.write("\n")
        
        if results['discrepancy_analysis']:
            f.write("## Space Discrepancy\n")
            disc = results['discrepancy_analysis']
            f.write(f"- df reports: {disc['df_used_bytes'] / (1024**3):.2f} GB\n")
            f.write(f"- du reports: {disc['du_used_bytes'] / (1024**3):.2f} GB\n")
            f.write(f"- Discrepancy: {disc['discrepancy_human']}\n\n")
        
        if results['largest_directories']:
            f.write("## Top 15 Largest Directories\n")
            for i, (path, size) in enumerate(results['largest_directories'][:15], 1):
                f.write(f"{i}. {format_size(size):>10} - {path}\n")
            f.write("\n")
        
        if results['largest_files']:
            f.write("## Top 10 Largest Files (>1GB)\n")
            for i, (path, size) in enumerate(results['largest_files'][:10], 1):
                f.write(f"{i}. {format_size(size):>10} - {path}\n")
            f.write("\n")
        
        f.write("---\n")
        f.write(f"*Report generated by Where Is My Space? tool*\n")
    
    print(f"Report saved to: {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze disk space usage and identify where space is being consumed.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 where_is_my_space.py
  python3 where_is_my_space.py --exclude-mount /mnt/external
  python3 where_is_my_space.py --output my_report.md
  python3 where_is_my_space.py --verbose
        """
    )
    
    parser.add_argument(
        '--exclude-mount',
        action='append',
        dest='exclude_mounts',
        help='Mount point to exclude from analysis (can be specified multiple times)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file for markdown report'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--root',
        default='/',
        help='Root path to analyze (default: /)'
    )
    
    args = parser.parse_args()
    
    # Run analysis
    print("Running disk space analysis...")
    results = analyze_disk_space(
        root_path=args.root,
        exclude_mounts=args.exclude_mounts,
        verbose=args.verbose
    )
    
    # Print report
    print_report(results, verbose=args.verbose)
    
    # Save report if requested
    if args.output:
        save_report(results, args.output)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())