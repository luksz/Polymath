#!/usr/bin/env python3
"""Seed development data. Run after bootstrap."""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Polymath development data")
    parser.add_argument("--env", default="development", choices=["development", "test"])
    args = parser.parse_args()

    print(f"Seeding {args.env} data...")
    print()

    # Phase 0: placeholder — real seeding added per service in Phase 1+
    print("Would seed:")
    print("  auth.users        — 1 owner user")
    print("  llm.prompts       — 3 example prompts")
    print("  content.posts     — 2 draft blog posts")
    print("  habits.habits     — 3 example habits")
    print()
    print("(Seeding not yet implemented — services don't exist yet.)")
    print("Add real seed logic in scripts/seed/ per service as each phase ships.")


if __name__ == "__main__":
    main()
