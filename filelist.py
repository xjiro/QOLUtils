#!/usr/bin/env python3
"""
File List Utility - Cross-platform tool for comparing directory file lists
"""

import os
import json
import sys
import hashlib
import base64
import random
from pathlib import Path
from typing import Dict, Tuple
import zlib

def clear_screen():
    """Clear the terminal screen (Windows/Linux compatible)"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title: str):
    """Print a formatted header"""
    clear_screen()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
    print()


def format_size(size_bytes: int) -> str:
    """Format bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def scan_directory(directory: str) -> Dict[str, int]:
    """
    Recursively scan a directory and return a dict of relative paths to file sizes
    
    Args:
        directory: Path to the directory to scan
    
    Returns:
        Dictionary mapping relative file paths to their sizes in bytes
    """
    directory_path = Path(directory).resolve()
    if not directory_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    if not directory_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")
    
    file_list = {}
    
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = Path(root) / file
            try:
                # Get relative path from the scanned directory
                rel_path = file_path.relative_to(directory_path)
                # Use forward slashes for consistency across platforms
                rel_path_str = str(rel_path).replace('\\', '/')
                file_size = file_path.stat().st_size
                file_list[rel_path_str] = file_size
            except (OSError, PermissionError) as e:
                print(f"Warning: Could not access {file_path}: {e}")
    
    return file_list


def dump_directory_to_json():
    """Menu option 1: Dump directory files to JSON"""
    print_header("Dump Directory to JSON")
    
    directory = input("Enter directory path to scan: ").strip()
    if not directory:
        print("Error: No directory provided")
        input("\nPress Enter to continue...")
        return
    
    try:
        print(f"\nScanning directory: {directory}")
        file_list = scan_directory(directory)
        
        # Generate default filename with hash and random component
        dir_hash = hashlib.sha256(str(Path(directory).resolve()).encode()).digest()
        hash_b32 = base64.b32encode(dir_hash)[:8].decode('ascii')
        random_int = random.randint(10000000, 99999999)
        default_filename = f"filelist_{hash_b32}_{random_int}.json"
        
        output_file = input(f"Enter output JSON filename (default: {default_filename}): ").strip()
        if not output_file:
            output_file = default_filename
        
        # Ensure .json extension
        if not output_file.endswith('.json'):
            output_file += '.json'
        
        # Create formatted JSON with metadata
        output_data = {
            "source_directory": str(Path(directory).resolve()),
            "total_files": len(file_list),
            "total_size": sum(file_list.values()),
            "files": file_list
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        total_size = sum(file_list.values())
        print(f"\n✓ Successfully scanned {len(file_list)} files")
        print(f"✓ Total size: {format_size(total_size)}")
        print(f"✓ Saved to: {output_file}")
        
    except Exception as e:
        print(f"\nError: {e}")
    
    input("\nPress Enter to continue...")


def load_json_filelist(json_path: str) -> Tuple[Dict[str, int], Dict]:
    """
    Load a JSON file list
    
    Returns:
        Tuple of (files dict, metadata dict)
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, dict) and 'files' in data:
        # New format with metadata
        files = data['files']
        metadata = {k: v for k, v in data.items() if k != 'files'}
    else:
        # Old format - just a dict of files
        files = data
        metadata = {}
    
    return files, metadata


def compare_file_lists():
    """Menu option 2: Compare two JSON file lists"""
    print_header("Compare Two File Lists")
    
    file_a = input("Enter path to first JSON file (A): ").strip()
    if not file_a:
        print("Error: No file provided")
        input("\nPress Enter to continue...")
        return
    
    file_b = input("Enter path to second JSON file (B): ").strip()
    if not file_b:
        print("Error: No file provided")
        input("\nPress Enter to continue...")
        return
    
    try:
        # Load both file lists
        files_a, meta_a = load_json_filelist(file_a)
        files_b, meta_b = load_json_filelist(file_b)
        
        # Convert to sets for comparison
        set_a = set(files_a.keys())
        set_b = set(files_b.keys())
        
        # Find differences
        only_in_a = set_a - set_b
        only_in_b = set_b - set_a
        in_both = set_a & set_b
        
        # Calculate sizes
        size_only_a = sum(files_a[f] for f in only_in_a)
        size_only_b = sum(files_b[f] for f in only_in_b)
        size_both_a = sum(files_a[f] for f in in_both)
        size_both_b = sum(files_b[f] for f in in_both)
        
        # Display results
        print("\n" + "=" * 70)
        print("COMPARISON RESULTS")
        print("=" * 70)
        
        print(f"\nList A: {file_a}")
        if 'source_directory' in meta_a:
            print(f"  Source: {meta_a['source_directory']}")
        print(f"  Total files: {len(files_a)}")
        print(f"  Total size: {format_size(sum(files_a.values()))}")
        
        print(f"\nList B: {file_b}")
        if 'source_directory' in meta_b:
            print(f"  Source: {meta_b['source_directory']}")
        print(f"  Total files: {len(files_b)}")
        print(f"  Total size: {format_size(sum(files_b.values()))}")
        
        print("\n" + "-" * 70)
        print("SUMMARY")
        print("-" * 70)
        print(f"Files in both lists:     {len(in_both):6d}  ({format_size(size_both_a)})")
        print(f"Files only in A:         {len(only_in_a):6d}  ({format_size(size_only_a)})")
        print(f"Files only in B:         {len(only_in_b):6d}  ({format_size(size_only_b)})")
        
        comparison_data = {
            "file_a": file_a,
            "file_b": file_b,
            "summary": {
                "total_in_a": len(files_a),
                "total_in_b": len(files_b),
                "in_both": len(in_both),
                "only_in_a": len(only_in_a),
                "only_in_b": len(only_in_b),
                "size_only_a": size_only_a,
                "size_only_b": size_only_b
            },
            "files_only_in_a": {f: files_a[f] for f in sorted(only_in_a)},
            "files_only_in_b": {f: files_b[f] for f in sorted(only_in_b)},
            "files_in_both": {f: {"size_a": files_a[f], "size_b": files_b[f]} for f in sorted(in_both)}
        }
        
        generate_zip_script(list(comparison_data["files_only_in_a"].keys()) + list(comparison_data["files_only_in_b"].keys()))
            
        
    except FileNotFoundError as e:
        print(f"\nError: File not found - {e}")
    except json.JSONDecodeError as e:
        print(f"\nError: Invalid JSON file - {e}")
    except Exception as e:
        print(f"\nError: {e}")
    
    input("\nPress Enter to continue...")


def generate_zip_script(files):
    files = json.dumps(files)
    compressed = zlib.compress(files.encode('utf-8'))
    zip_b64 = base64.b64encode(compressed).decode('utf-8')

    with open("zip_different_files.py", 'w', encoding='utf-8') as f:
        f.write("#!/usr/bin/env python3\n")
        f.write('"""\n')
        f.write("Script to compress difference files into a zip archive\n")
        f.write('"""\n\n')
        f.write("import zipfile, json, zlib, base64\n\n")
        f.write(f"zip_b64 = '''{zip_b64}'''\n\n")
        f.write("zip_data = base64.b64decode(zip_b64)\n")
        f.write("files = zlib.decompress(zip_data).decode('utf-8')\n")
        f.write("files = json.loads(files)\n\n")
        f.write("compressed_successful = 0\n")
        f.write("with zipfile.ZipFile('diff_files.zip', 'w') as zipf:\n")
        f.write("    for file in files:\n")
        f.write("        try:\n")
        f.write("            zipf.write(file)\n")
        f.write("            compressed_successful += 1\n")
        f.write("        except FileNotFoundError:\n")
        f.write("            pass\n")
        f.write("print(f'Compressed {compressed_successful} files into diff_files.zip')\n")

    print("\n✓ Generated zip_diff_files.py script to create diff_files.zip with the mutually exclusive files")

def show_menu():
    """Display the main menu and return user choice"""
    print_header("File List Utility")
    
    print("Available Operations:")
    print()
    print("  1. Dump directory to JSON")
    print("  2. Compare two JSON file lists")
    print("  3. Quit")
    print()
    
    choice = input("Enter your choice (1-3): ").strip()
    return choice


def main():
    while True:
        choice = show_menu()
        
        if choice == '1':
            dump_directory_to_json()
        elif choice == '2':
            compare_file_lists()
        elif choice == '3':
            print_header("Goodbye!")
            print("Thank you for using File List Utility.\n")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please enter a number from 1 to 3.")
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
