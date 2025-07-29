#!/usr/bin/env python3
"""
MathsFun - Interactive Math Practice Application

This is the entry point for the MathsFun application.
The actual implementation is in src/presentation/cli/main.py
"""

import argparse


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="MathsFun - Interactive Math Practice Application"
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Use local Docker Supabase environment instead of production",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    from src.presentation.cli.main import main
    main(use_local=args.local)