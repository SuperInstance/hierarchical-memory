#!/usr/bin/env python3
"""
Test runner script for hierarchical-memory package.

Provides convenient commands to run tests with various options including:
- Run all tests
- Run specific test files
- Run with coverage reporting
- Run specific test markers
- Generate coverage reports
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path


def run_command(cmd, verbose=False):
    """Run a command and return the result."""
    if verbose:
        print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


def run_all_tests(verbose=False, coverage=True, extra_args=None):
    """Run all tests."""
    cmd = ["python", "-m", "pytest", "tests/"]

    if coverage:
        cmd.extend([
            "--cov=hierarchical_memory",
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing:skip-covered",
            "--cov-report=xml:coverage.xml"
        ])

    if extra_args:
        cmd.extend(extra_args)

    return run_command(cmd, verbose)


def run_specific_test(test_file, verbose=False, coverage=True, extra_args=None):
    """Run a specific test file."""
    cmd = ["python", "-m", "pytest", f"tests/{test_file}"]

    if coverage:
        cmd.extend([
            "--cov=hierarchical_memory",
            "--cov-report=term-missing:skip-covered"
        ])

    if extra_args:
        cmd.extend(extra_args)

    return run_command(cmd, verbose)


def run_marked_tests(marker, verbose=False, coverage=True, extra_args=None):
    """Run tests with specific marker."""
    cmd = ["python", "-m", "pytest", "-m", marker]

    if coverage:
        cmd.extend([
            "--cov=hierarchical_memory",
            "--cov-report=term-missing:skip-covered"
        ])

    if extra_args:
        cmd.extend(extra_args)

    return run_command(cmd, verbose)


def run_with_coverage_report(verbose=False):
    """Run tests and generate detailed coverage report."""
    print("Running tests with full coverage report...")
    cmd = [
        "python", "-m", "pytest",
        "--cov=hierarchical_memory",
        "--cov-report=html:htmlcov",
        "--cov-report=term",
        "--cov-report=xml:coverage.xml",
        "--cov-config=pytest.ini"
    ]
    returncode = run_command(cmd, verbose)

    if returncode == 0:
        print("\n" + "="*60)
        print("Coverage report generated:")
        print("  HTML: htmlcov/index.html")
        print("  XML:  coverage.xml")
        print("="*60)

    return returncode


def list_tests():
    """List all available tests."""
    print("\nAvailable test files:")
    print("-" * 40)
    for test_file in Path("tests").glob("test_*.py"):
        print(f"  - {test_file.name}")

    print("\nAvailable markers:")
    print("-" * 40)
    markers = [
        ("unit", "Unit tests (fast, isolated)"),
        ("integration", "Integration tests (slower, cross-component)"),
        ("slow", "Slow tests (should be run separately)"),
        ("working", "Working memory tests"),
        ("episodic", "Episodic memory tests"),
        ("semantic", "Semantic memory tests"),
        ("procedural", "Procedural memory tests"),
        ("consolidation", "Consolidation tests"),
        ("retrieval", "Retrieval tests"),
        ("sharing", "Memory sharing tests"),
    ]
    for marker, description in markers:
        print(f"  - {marker}: {description}")


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(
        description="Test runner for hierarchical-memory package",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests
  python run_tests.py

  # Run all tests with verbose output
  python run_tests.py -v

  # Run specific test file
  python run_tests.py -f test_working_memory.py

  # Run tests with specific marker
  python run_tests.py -m working

  # Generate coverage report only
  python run_tests.py --coverage

  # List available tests and markers
  python run_tests.py --list
        """
    )

    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Verbose output")

    parser.add_argument("--no-cov", action="store_true",
                       help="Disable coverage reporting")

    parser.add_argument("-f", "--file", type=str,
                       help="Run specific test file")

    parser.add_argument("-m", "--marker", type=str,
                       help="Run tests with specific marker")

    parser.add_argument("--coverage", action="store_true",
                       help="Generate coverage report only")

    parser.add_argument("--list", action="store_true",
                       help="List available tests and markers")

    parser.add_argument("extra", nargs="*",
                       help="Extra arguments to pass to pytest")

    args = parser.parse_args()

    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)

    # Handle list command
    if args.list:
        list_tests()
        return 0

    # Handle coverage report
    if args.coverage:
        return run_with_coverage_report(args.verbose)

    # Determine what to run
    coverage = not args.no_cov

    if args.file:
        # Run specific test file
        return run_specific_test(args.file, args.verbose, coverage, args.extra)

    elif args.marker:
        # Run marked tests
        return run_marked_tests(args.marker, args.verbose, coverage, args.extra)

    else:
        # Run all tests
        return run_all_tests(args.verbose, coverage, args.extra)


if __name__ == "__main__":
    sys.exit(main())
