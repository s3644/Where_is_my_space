# Where Is My Space? - GitHub Repository Setup

## Repository Contents

This repository contains tools and documentation for analyzing disk space usage on Linux systems.

### Files

1. **`where_is_my_space.py`** - Main Python script for disk space analysis
   - Comprehensive disk usage analysis
   - Compares `df` vs `du` measurements
   - Identifies filesystem overhead
   - Lists largest directories and files
   - Detects deleted files still held open

2. **`README.md`** - Complete documentation
   - Installation instructions
   - Usage examples
   - Troubleshooting guide
   - Understanding the results

3. **`WHERE_IS_MY_SPACE_SUMMARY.md`** - Example analysis report
   - Real-world case study
   - Detailed breakdown of space usage
   - Root cause analysis

4. **`WHERE_IS_MY_SPACE_REPORT.md`** - Generated analysis report
   - Output from running the tool
   - Can be regenerated anytime

5. **`.github/workflows/disk-analysis.yml`** - GitHub Actions workflow
   - Automated weekly analysis
   - Scheduled reporting

6. **`.gitignore`** - Git ignore patterns
   - Excludes Python cache files
   - Excludes generated reports
   - IDE and OS files

7. **`.gitattributes`** - Git attributes
   - Consistent line endings
   - Text file handling

## Quick Start

### Run Analysis
```bash
# Basic usage
python3 where_is_my_space.py

# Exclude mount points (e.g., NAS, external drives)
python3 where_is_my_space.py --exclude-mount /mnt/nas

# Generate markdown report
python3 where_is_my_space.py --output report.md
```

### Upload to GitHub

```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Initial commit
git commit -m "Initial commit: Where Is My Space? disk analysis tool"

# Create remote repository on GitHub
# (Go to GitHub, create new repo, then:)
git remote add origin https://github.com/YOUR_USERNAME/where-is-my-space.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Features

### What the Tool Does

1. **Space Discrepancy Analysis**
   - Compares `df -h` (kernel view) vs `du -sh` (user view)
   - Identifies "missing" space
   - Explains filesystem overhead

2. **Filesystem Insights**
   - Reserved blocks (typically 5% of filesystem)
   - Inode table overhead
   - Journal space
   - Directory structure overhead

3. **Large Files & Directories**
   - Lists top 15 largest directories
   - Lists top 10 largest files (>1GB)
   - Identifies space-consuming datasets

4. **Deleted Files**
   - Detects deleted files still held open
   - Shows which processes are holding them
   - Helps recover space from stale files

### Why This Matters

Common scenario:
- `df -h` shows: 2.3TB used on 3.6TB drive
- `du -sh` shows: ~1.6TB used
- **Missing:** ~0.7TB unaccounted for

This tool explains where that space goes and provides actionable insights.

## Use Cases

### For Developers
- Debug disk space issues
- Optimize storage usage
- Understand filesystem behavior

### For DevOps
- Monitor disk usage
- Automated reporting
- Capacity planning

### For Researchers
- Track large dataset storage
- Identify space-consuming experiments
- Optimize data management

## Contributing

Contributions are welcome! Here's how you can help:

1. **Report Issues** - Found a bug? Have a suggestion?
2. **Submit Features** - Want to add new analysis capabilities?
3. **Improve Documentation** - Make it clearer and more helpful

## License

MIT License - Free to use, modify, and distribute.

## Version History

### v1.0.0 (April 2026)
- Initial release
- Core analysis functionality
- Markdown report generation
- GitHub Actions integration

## Support

For issues or questions:
- Open an issue on GitHub
- Check the README for usage examples
- Review the example reports for real-world cases

## Author

Jukrapope Jitpimolmard
April 2026

## License

MIT License - Free to use, modify, and distribute.

## Contributing

Contributions are welcome! Here's how you can help:

1. **Report Issues** - Found a bug? Have a suggestion?
2. **Submit Features** - Want to add new analysis capabilities?
3. **Improve Documentation** - Make it clearer and more helpful

## Version History

### v1.0.0 (April 2026)
- Initial release
- Core analysis functionality
- Markdown report generation
- GitHub Actions integration

## Acknowledgments

Developed to solve the common problem of unaccounted disk space on Linux systems, particularly those using ext4 filesystems with large numbers of files.

---

**Happy analyzing!** 🚀