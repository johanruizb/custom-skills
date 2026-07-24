#!/usr/bin/env python3
"""
Detect mechanical code duplication across a codebase.

Finds near-duplicate code blocks (normalized) across files, helping identify
copy-paste duplication that a human should review.

Usage:
    python detect-duplicates.py <root_dir> [--min-lines N] [--exclude PATTERN ...]

Options:
    --min-lines N      Minimum block size to consider (default: 5)
    --exclude PATTERN   Glob pattern to exclude (can be repeated)
                       Default excludes: node_modules, .git, __pycache__, .venv,
                       venv, dist, build, migrations, vendor, *.min.js, *.map

Output:
    Prints groups of near-duplicate blocks with file:line references.
    Exits 0 always (findings are informational).
"""

import argparse
import hashlib
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

# File extensions to analyze
EXTENSIONS = {
    '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.kt', '.go', '.rs',
    '.rb', '.php', '.cs', '.c', '.cpp', '.h', '.hpp', '.swift', '.m',
    '.vue', '.svelte', '.html', '.css', '.scss', '.less',
}

# Default exclusion patterns
DEFAULT_EXCLUDES = {
    'node_modules', '.git', '__pycache__', '.venv', 'venv', 'dist',
    'build', 'migrations', 'vendor', '.next', 'coverage', 'target',
    '.tox', '.eggs', '*.egg-info', '__pypackages__',
}

# File name patterns to exclude
FILE_EXCLUDES = {
    '*.min.js', '*.min.css', '*.map', '*.lock', 'package-lock.json',
    'yarn.lock', 'poetry.lock', 'Cargo.lock', 'go.sum',
}


def should_exclude(path: Path, exclude_patterns: set) -> bool:
    """Check if a path should be excluded."""
    parts = path.parts
    
    # Check directory components
    for part in parts:
        for pattern in exclude_patterns:
            if '*' in pattern:
                import fnmatch
                if fnmatch.fnmatch(part, pattern):
                    return True
            elif part == pattern or part.startswith(pattern):
                return True
    
    # Check file name patterns
    import fnmatch
    for pattern in FILE_EXCLUDES:
        if fnmatch.fnmatch(path.name, pattern):
            return True
    
    return False


def normalize_block(text: str) -> str:
    """Normalize a code block for comparison: strip whitespace, lowercase keywords."""
    # Remove comments (Python, JS, etc.)
    text = re.sub(r'#.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'//.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    
    # Remove blank lines
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    
    # Normalize whitespace within lines
    lines = [re.sub(r'\s+', ' ', l) for l in lines]
    
    # Normalize variable names to placeholders (heuristic)
    # This helps find blocks that are structurally identical but use different names
    normalized = []
    for line in lines:
        # Replace string literals with <str>
        line = re.sub(r'["\'].*?["\']', '<str>', line)
        # Replace numbers with <num>
        line = re.sub(r'\b\d+\.?\d*\b', '<num>', line)
        normalized.append(line)
    
    return '\n'.join(normalized)


def extract_blocks(lines: list, min_lines: int) -> list:
    """Extract contiguous blocks of minimum size from a list of lines."""
    blocks = []
    # Use a sliding window approach
    for start in range(len(lines)):
        end = start + min_lines
        if end > len(lines):
            break
        block_text = '\n'.join(lines[start:end])
        blocks.append((start + 1, block_text))  # 1-indexed line number
    return blocks


def find_duplicates(root: Path, min_lines: int, exclude_patterns: set) -> list:
    """Find duplicate blocks across all source files."""
    # Collect all source files
    source_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not should_exclude(
            Path(dirpath) / d, exclude_patterns)]
        
        for fname in filenames:
            fpath = Path(dirpath) / fname
            if fpath.suffix in EXTENSIONS and not should_exclude(fpath, exclude_patterns):
                source_files.append(fpath)
    
    if not source_files:
        print("No source files found matching the criteria.")
        return []
    
    print(f"Scanning {len(source_files)} source files for blocks >= {min_lines} lines...")
    
    # Build a map: normalized_hash -> [(file, start_line, raw_text)]
    block_map = defaultdict(list)
    
    for fpath in source_files:
        try:
            content = fpath.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        
        lines = content.splitlines()
        blocks = extract_blocks(lines, min_lines)
        
        for start_line, block_text in blocks:
            normalized = normalize_block(block_text)
            if len(normalized.strip()) < 20:  # Skip trivially short blocks
                continue
            block_hash = hashlib.md5(normalized.encode()).hexdigest()
            block_map[block_hash].append({
                'file': str(fpath.relative_to(root)),
                'line': start_line,
                'text': block_text,
            })
    
    # Find groups with > 1 occurrence (duplicates)
    duplicates = []
    for block_hash, occurrences in block_map.items():
        if len(occurrences) > 1:
            # Check if occurrences are in different files (cross-file duplication)
            files = set(occ['file'] for occ in occurrences)
            if len(files) > 1 or len(occurrences) > 2:
                duplicates.append({
                    'hash': block_hash,
                    'occurrences': occurrences,
                    'count': len(occurrences),
                    'files': files,
                })
    
    # Sort by number of occurrences (most duplicated first)
    duplicates.sort(key=lambda d: d['count'], reverse=True)
    
    return duplicates


def main():
    parser = argparse.ArgumentParser(
        description='Detect mechanical code duplication across a codebase.'
    )
    parser.add_argument('root_dir', help='Root directory to scan')
    parser.add_argument('--min-lines', type=int, default=5,
                        help='Minimum block size to consider (default: 5)')
    parser.add_argument('--exclude', action='append', default=[],
                        help='Glob pattern to exclude (can be repeated)')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON instead of text')
    args = parser.parse_args()
    
    root = Path(args.root_dir).resolve()
    if not root.exists():
        print(f"Error: {root} does not exist", file=sys.stderr)
        sys.exit(1)
    
    exclude_patterns = set(DEFAULT_EXCLUDES)
    if args.exclude:
        exclude_patterns.update(args.exclude)
    
    duplicates = find_duplicates(root, args.min_lines, exclude_patterns)
    
    if not duplicates:
        print("No duplicate blocks found (with the given parameters).")
        return
    
    # Deduplicate overlapping blocks (a block at line 5 and line 6 are likely the same duplication)
    # Group by file pairs
    seen_groups = set()
    unique_dupes = []
    for dup in duplicates:
        # Create a signature of the file:line pairs
        sig = tuple(sorted((occ['file'], occ['line']) for occ in dup['occurrences']))
        # Check if this is a subset of an already-seen group
        is_subset = False
        for seen in seen_groups:
            if set(sig).issubset(set(seen)):
                is_subset = True
                break
        if not is_subset:
            unique_dupes.append(dup)
            seen_groups.add(sig)
    
    if args.json:
        import json
        output = []
        for dup in unique_dupes[:50]:  # Cap at 50 groups
            output.append({
                'count': dup['count'],
                'files': list(dup['files']),
                'occurrences': [{'file': occ['file'], 'line': occ['line']} 
                                 for occ in dup['occurrences']],
                'preview': dup['occurrences'][0]['text'][:200],
            })
        print(json.dumps(output, indent=2))
    else:
        print(f"\nFound {len(unique_dupes)} duplicate block groups (showing top 30):\n")
        for i, dup in enumerate(unique_dupes[:30], 1):
            print(f"--- Group {i} ({dup['count']} occurrences in {len(dup['files'])} files) ---")
            for occ in dup['occurrences']:
                print(f"  {occ['file']}:{occ['line']}")
            # Show preview of first occurrence
            preview = dup['occurrences'][0]['text'][:200]
            print(f"  Preview:\n    {preview[:200]}\n")
        
        if len(unique_dupes) > 30:
            print(f"... and {len(unique_dupes) - 30} more groups (use --json for full output)")


if __name__ == '__main__':
    main()