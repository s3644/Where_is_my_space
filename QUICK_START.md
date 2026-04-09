# Quick Start Guide

## Repository Structure

```
Where_is_my_space/
├── .github/
│   └── workflows/
│       └── disk-analysis.yml    # GitHub Actions workflow
├── .gitattributes               # Git attributes
├── .gitignore                   # Git ignore patterns
├── README.md                    # Full documentation
├── REPO_SETUP.md                # Repository setup instructions
├── setup.sh                     # Git initialization script
├── where_is_my_space.py         # Main analysis tool
├── WHERE_IS_MY_SPACE_SUMMARY.md # Example analysis report
└── WHERE_IS_MY_SPACE_REPORT.md  # Generated analysis report
```

## Quick Commands

### Run Analysis
```bash
cd /home/jukrapope/Where_is_my_space
python3 where_is_my_space.py
```

### Generate Report (Universal)
```bash
# Works on any Linux system
python3 where_is_my_space.py --output report.md

# Exclude specific mount points based on your system
python3 where_is_my_space.py --exclude-mount /mnt/nas --output report.md
```

### Initialize Git Repository
```bash
./setup.sh
```

### Upload to GitHub
```bash
# After running setup.sh:
git remote add origin https://github.com/YOUR_USERNAME/where-is-my-space.git
git branch -M main
git push -u origin main
```

## What This Tool Does

Analyzes disk space usage and explains discrepancies between:
- `df -h` (kernel view of disk usage)
- `du -sh` (actual file content size)

Commonly reveals where "missing" space goes:
- Filesystem reserved blocks (5% default)
- Inode tables and metadata
- Directory structure overhead
- Journal space

## Example Output

```
DF Information:
  Filesystem: /dev/nvme0n1p2
  Size: 3.6T
  Used: 2.3T (65%)

Discrepancy Analysis:
  df reports: 2.3T
  du reports: 1.7T
  Missing: 0.6T

  Breakdown:
    Reserved blocks: 186GB
    Inode tables: 58GB
    Directory overhead: 300GB
```

## Files Explained

- **where_is_my_space.py** - Main analysis tool
- **README.md** - Complete documentation
- **WHERE_IS_MY_SPACE_SUMMARY.md** - Example analysis report
- **WHERE_IS_MY_SPACE_REPORT.md** - Generated report
- **REPO_SETUP.md** - Repository setup instructions
- **setup.sh** - Git initialization helper

## Next Steps

1. Review the documentation in README.md
2. Run the tool to analyze your system
3. Upload to GitHub using the setup script
4. Share with your team!

For detailed instructions, see REPO_SETUP.md

---

**Author: Jukrapope Jitpimolmard**