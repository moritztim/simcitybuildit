#!/usr/bin/env python
import csv
import os
import argparse
from collections import defaultdict


def generate_markdown_tables(csv_file, root_path):
	"""
	Create a README.md in each directory from the CSV, containing a flat markdown table.
	The first column becomes a link to the .sha256 file.
	"""
	with open(csv_file, "r", encoding="utf8") as f:
		reader = csv.DictReader(f)
		headers = reader.fieldnames
		headers[0] = headers[0].lstrip("\ufeff")  # Remove BOM if present

		rows_by_dir = defaultdict(list)

		for row in reader:
			file_path = row[headers[0]]
			dir_path = os.path.dirname(file_path)
			row[headers[0]] = (
					f"[{file_path}](./{file_path})"
			)
			rows_by_dir[dir_path].append(row)

		for dir_path, rows in rows_by_dir.items():
			print(f"Indexing {dir_path or 'root'}")
			output_path = os.path.join(root_path, dir_path, "README.md")
			os.makedirs(os.path.dirname(output_path), exist_ok=True)
			with open(output_path, "w", encoding="utf8") as out:
					out.write(f"# Index of {dir_path or 'SimCity.app'}\n\n")
					out.write(f"| {' | '.join(headers)} |\n")
					out.write(f"| {' | '.join(['---'] * len(headers))} |\n")
					for row in rows:
						out.write(f"| {' | '.join([row[header] for header in headers])} |\n")
					out.write("\n\n")
					out.write(f"This file was **generated** from [{os.path.basename(csv_file)}]({os.path.relpath(csv_file, os.path.dirname(output_path))}). Please do not edit it directly.\n")


def main():
	parser = argparse.ArgumentParser(
		description="Generate README.md files from a CSV file"
	)
	parser.add_argument("csv_file", help="Path to the CSV file")
	parser.add_argument("root_path", help="Root directory to use for linking paths")

	args = parser.parse_args()

	generate_markdown_tables(args.csv_file, args.root_path)


if __name__ == "__main__":
	main()
