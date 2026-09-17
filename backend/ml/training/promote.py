"""Promotion CLI for promoting candidate runs to current."""
import argparse
from pathlib import Path
from backend.ml.artifacts import promote_run


def main():
    parser = argparse.ArgumentParser(description="Promote an ML candidate run to current")
    parser.add_argument("--run-id", type=str, required=True, help="Run ID to promote")
    parser.add_argument("--output-dir", type=str, default="artifacts/ml", help="Artifacts directory")
    args = parser.parse_args()

    link = promote_run(args.output_dir, args.run_id)
    print(f"Successfully promoted {args.run_id} -> {link}")


if __name__ == "__main__":
    main()
