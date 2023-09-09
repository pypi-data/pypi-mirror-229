"""CLI handling utilities"""

import os
import argparse
from . import NotionExporter
from .utils import pages_from_str


def parse_args() -> argparse.Namespace:
    """Parses the CLI arguments.
    Only `page_id` is required. All other arguments are optional.
    """
    parser = argparse.ArgumentParser(
        description="Export Notion pages to your GitHub repository."
    )
    parser.add_argument(
        "page_id",
        help="The ID of the Notion page you want to export. Separate multiple pages with commas.",
    )
    parser.add_argument(
        "-d",
        "--export-dir",
        help="The directory to export the page to. Defaults to the current directory.",
    )
    parser.add_argument(
        "-k",
        "--keep-structure",
        help="Keep the page hierarchy when exporting. Defaults to False.",
        action="store_true",
    )
    parser.add_argument(
        "-t",
        "--export-type",
        help="The type of file to export. Defaults to HTML.",
        choices=["html", "markdown", "pdf", "word"],
        default="html",
    )
    parser.add_argument(
        "-c",
        "--current-view",
        help="The type of view to export. Defaults to the currentView.",
        choices=["currentView", "all"],
        default="currentView",
    )
    parser.add_argument(
        "-l",
        "--no-file",
        help="Do not export files attached to the page. Defaults to False.",
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--single-page",
        help="Do not export child pages. Defaults to False.",
        action="store_true",
    )
    parser.add_argument(
        "-w",
        "--rewrite",
        help="Do not create date-formated folders for each export. Defaults to False.",
        action="store_true",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Whether to print verbose output. Defaults to False.",
        action="store_true",
    )
    parser.add_argument(
        "--token-v2",
        help="The token_v2 cookie value from your Notion session.",
    )
    parser.add_argument(
        "--file-token",
        help="The file-token cookie value from your Notion session.",
    )
    args = parser.parse_args()
    return args


def run_from_cli():
    """Runs the exporter from the CLI arguments."""
    args = parse_args()
    token_v2 = args.token_v2 or os.getenv("NOTION_TOKEN_V2")
    file_token = args.file_token or os.getenv("NOTION_FILE_TOKEN")
    if not token_v2:
        raise ValueError("NOTION_TOKEN_V2 environment variable not set.")
    if not file_token:
        raise ValueError("NOTION_FILE_TOKEN environment variable not set.")
    exporter = NotionExporter(
        token_v2=token_v2,
        file_token=file_token,
        pages=pages_from_str(args.page_id),
        export_directory=args.export_dir,
        flatten_export_file_tree=args.keep_structure,
        export_type=args.export_type,
        current_view_export_type=args.current_view,
        include_files=not args.no_file,
        recursive=not args.single_page,
        rewrite=args.rewrite,
        verbose=args.verbose,
    )
    exporter.export()
