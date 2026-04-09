# Where Is My Space? - Disk Space Analysis Tool

A comprehensive Python tool to analyze disk space usage and identify where space is being consumed on Linux systems.

## Problem Solved

This tool helps answer the common question: **"Where is my disk space going?"** when `df -h` shows more used space than `du -sh` reports.

### Common Scenario
- `df -h` shows: 2.3TB used on a 3.6TB drive
- `du -sh` shows: ~1.6TB used
- **Missing:** ~0.7TB unaccounted for

## Features

- **Comprehensive Analysis:**
  - Compares `df` (kernel view) vs `du` (user view) measurements
  - Identifies filesystem overhead (reserved blocks, inode tables, journal)
  - Lists largest directories and files
  - Detects deleted files still held open by processes

- **Ext4 Filesystem Insights:**
  - Calculates reserved block space (typically 5% of filesystem)
  - Estimates inode table overhead
  - Reports journal size
  - Analyzes directory structure overhead

- **Flexible Output:**
  - Console report with detailed breakdown
  - Markdown report generation for sharing
  - Configurable exclusion of mount points

## Installation

### Prerequisites
- Python 3.6+
- Linux system with ext4 filesystem
- `sudo` privileges for detailed analysis

### Setup
```bash
# Clone or download the script
chmod +x where_is_my_space.py

# Make it executable
sudo chmod +x where_is_my_space.py
```

## Usage

### Basic Usage
```bash
# Analyze root filesystem (works on any Linux system)
./where_is_my_space.py

# Analyze specific path
./where_is_my_space.py --root /path/to/analyze
```

### Exclude Mount Points
```bash
# Exclude NAS mount and other network filesystems
./where_is_my_space.py --exclude-mount /mnt/nas --exclude-mount /media/external

# Exclude multiple mount points
./where_is_my_space.py --exclude-mount /mnt/nas --exclude-mount /mnt/external --exclude-mount /run/user/1000
```

### Universal Usage
```bash
# This script works on any Linux system
# Just specify which mount points to exclude based on your system

# Example for a system with NAS mount
./where_is_my_space.py --exclude-mount /mnt/nas

# Example for a system with external drives
./where_is_my_space.py --exclude-mount /media/external --exclude-mount /mnt/usb

# Example for a system with Docker mounts
./where_is_my_space.py --exclude-mount /var/lib/docker
```

### Generate Markdown Report
```bash
# Save report to file
./where_is_my_space.py --output disk_analysis.md

# Save with custom filename
./where_is_my_space.py -o my_report.md
```

### Verbose Output
```bash
# Show detailed information
./where_is_my_space.py --verbose
```

### Full Example
```bash
# Example for any Linux system
./where_is_my_space.py \
  --root / \
  --exclude-mount /mnt/nas \
  --exclude-mount /mnt/external \
  --output disk_space_report.md \
  --verbose
```

## Output Examples

### Console Report
```
================================================================================
DISK SPACE ANALYSIS REPORT
================================================================================
Timestamp: 2026-04-09T12:30:45.123456
Root Path: /

DF Information (from kernel):
  Filesystem: /dev/nvme0n1p2
  Type: ext4
  Size: 3.6T
  Used: 2.3T (65%)
  Available: 1.2T

Filesystem Overhead Estimates:
  Reserved Blocks: 180.00 GB
  Inode Table: 62.50 GB
  Journal: 0.25 GB

Space Discrepancy Analysis:
  df reports: 2300.00 GB
  du reports: 1700.00 GB
  Discrepancy: 600.00 GB

  Estimated Overhead Breakdown:
    Reserved blocks: 180.00 GB
    Inode table: 62.50 GB
    Journal: 0.25 GB
    Directory/Other overhead: 300.00 GB

Top 15 Largest Directories:
   ...

================================================================================
END OF REPORT
================================================================================
```

### Markdown Report
The tool can generate a formatted markdown report suitable for:
- GitHub repositories
- Documentation
- Sharing with team members
- Archiving for future reference

## Understanding the Results

### Why Does Discrepancy Exist?

The difference between `df` and `du` measurements is **normal** and expected. Here's where the "missing" space goes:

1. **Reserved Blocks (5% default)**
   - ~180GB on a 3.6TB drive
   - Reserved for root processes to prevent system failure
   - Managed by ext4, invisible to `du`

2. **Filesystem Metadata**
   - Inode tables: ~62GB (244M inodes × 256 bytes)
   - Block/Inode bitmaps
   - Group descriptors
   - Extent trees for file mapping

3. **Directory Overhead**
   - Directory entries for millions of files
   - HTree indexing for large directories
   - Extended attributes (xattrs)

4. **Journal Space**
   - Ext4 journal for crash consistency
   - Typically 128MB-1GB

### When to Worry

**Normal:**
- Discrepancy of 10-20% of total capacity
- Reserved blocks consuming expected space
- Filesystem metadata proportional to file count

**Concerning:**
- Discrepancy >30% of total capacity
- Rapid growth in filesystem overhead
- Deleted files still held open consuming significant space

## Troubleshooting

### High Reserved Space
If you want to reduce reserved blocks (use with caution):
```bash
# Reduce from 5% to 1%
sudo tune2fs -m 1 /dev/nvme0n1p2

# Check current reservation
sudo tune2fs -l /dev/nvme0n1p2 | grep "Reserved block count"
```

**Warning:** Reducing reserved space below 1% can cause system instability when disk is nearly full.

### Deleted Files Still Open
If `lsof +L1` shows deleted files:
```bash
# Identify the process
sudo lsof +L1 | grep deleted

# Restart the process to release space
sudo systemctl restart service-name
# or
kill -HUP PID
```

## Files Included

- `where_is_my_space.py` - Main analysis script
- `README.md` - This documentation
- `WHERE_IS_MY_SPACE_SUMMARY.md` - Example analysis report

## License

MIT License - Feel free to use, modify, and distribute.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Version

1.0.0 - Initial release

## Author

Jukrapope Jitpimolmard
April 2026

## License

MIT License - Feel free to use, modify, and distribute.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Version

1.0.0 - Initial release

## Acknowledgments

This tool was developed to solve the common problem of unaccounted disk space on Linux systems, particularly those using ext4 filesystems with large numbers of files.