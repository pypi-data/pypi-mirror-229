import json
import logging
import os
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple, Dict
from tqdm import tqdm

from . import utils


logger = logging.getLogger(__name__)


class ExportType:
	MARKDOWN = "markdown"
	HTML = "html"
	PDF = "pdf"


class ViewExportType:
	CURRENT_VIEW = "currentView"
	ALL = "all"


class NotionExporter:
	"""
	Uses the Notion API to export pages asynchronously. Downloads the exported zip file
	and unpacks it to the specified directory.

	## Arguments
	- `token_v2` The token_v2 cookie from your logged-in Notion session.
	- `file_token` The file_token cookie from your logged-in Notion session.
	- `pages` A {'name' : 'id'} format dict. **Names can be anything you want**.
	- `export_directory` The directory to export the pages to. Defaults to the current directory.
	- `flatten_export_file_tree` Whether to flatten the export file tree. Defaults to True.
	- `export_type` The type of export to perform. Defaults to `ExportType.MARKDOWN`.
	- `current_view_export_type` The type of export to perform. Defaults to `ViewExportType.CURRENT_VIEW`.
	- `include_files` Whether to include the static files in the export. Defaults to True.
	- `recursive` Whether to recursively export subpages. Defaults to True.
	- `rewrite` Whether to rewrite the export directory. Defaults to False. If True, does not create a new directory for each export.
	- `verbose` Whether to print verbose output. Defaults to False.
	"""

	def __init__(
		self,
		token_v2: str,
		file_token: str,
		pages: Dict[str, str],
		export_directory: str = None,
		flatten_export_file_tree: bool = True,
		export_type: ExportType = ExportType.MARKDOWN,
		current_view_export_type: ViewExportType = ViewExportType.CURRENT_VIEW,
		include_files: bool = True,
		recursive: bool = True,
		rewrite: bool = False,
		verbose: bool = False,
	):
		for v in pages.values():
			utils.to_uuid_format(v, error_msg=f"Invalid page ID. ")
		self.token_v2 = token_v2
		self.file_token = file_token
		self.include_files = include_files
		self.recursive = recursive
		self.pages = pages
		self.current_view_export_type = current_view_export_type
		self.flatten_export_file_tree = flatten_export_file_tree
		self.export_type = export_type
		self.download_headers = {
			"content-type": "application/json",
			"cookie": f"file_token={self.file_token};",
		}
		self.query_headers = {
			"content-type": "application/json",
			"cookie": f"token_v2={self.token_v2};",
		}
		self.export_directory = export_directory or os.getcwd()
		if not self.export_directory.startswith("/"):
			self.export_directory = f"{os.getcwd()}/{self.export_directory}"
		dir = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") if not rewrite else ""
		os.makedirs(f"{self.export_directory}/{dir}", exist_ok=True)
		self.export_directory = f"{self.export_directory}/{dir}"
		if verbose:
			logging.basicConfig(
				level=logging.DEBUG,
				format="%(asctime)s [%(levelname)s] [%(module)s.%(funcName)s]: %(message)s",
				datefmt="%Y-%m-%d %H:%M:%S",
			)

	def _get_format_options(
		self, export_type: ExportType, include_files: bool = False
	) -> dict:
		format_options = {}
		if export_type == ExportType.PDF:
			format_options["pdfFormat"] = "Letter"

		if not include_files:
			format_options["includeContents"] = "no_files"

		return format_options

	def _get_task_id(self, id: str) -> str:
		url = "https://www.notion.so/api/v3/enqueueTask"
		id = utils.to_uuid_format(id)
		export_options = {
			"exportType": self.export_type,
			"locale": "en",
			"timeZone": "Europe/London",
			"collectionViewExportType": self.current_view_export_type,
			"flattenExportFiletree": self.flatten_export_file_tree,
		}
		# Update the exportOptions with format-specific options
		export_options.update(
			self._get_format_options(
				export_type=self.export_type, include_files=self.include_files
			)
		)
		payload = json.dumps(
			{
				"task": {
					"eventName": "exportBlock",
					"request": {
						"block": {
							"id": id,
						},
						"recursive": self.recursive,
						"exportOptions": export_options,
					},
				}
			}
		)
		response = utils.session.post(url, headers=self.query_headers, data=payload)
		response.raise_for_status()
		return response.json()["taskId"]

	def _get_status(self, task_id: str) -> dict:
		url = "https://www.notion.so/api/v3/getTasks"

		payload = json.dumps({"taskIds": [task_id]})

		response = utils.session.post(url, headers=self.query_headers, data=payload)
		response.raise_for_status()
		return response.json()["results"][0]

	def _process_page(self, page: Tuple[str, str]) -> dict:
		name, id = page
		task_id = self._get_task_id(id)

		status, state, error, pages_exported = self._wait_for_export_completion(
			task_id=task_id
		)
		if state == "failure":
			logger.error(f"Export failed for {name} with error: {error}")
			return {"state": state, "name": name, "error": error}

		export_url = status.get("status", {}).get("exportURL")
		if export_url:
			utils.download_url(
				url=export_url,
				path=f"{self.export_directory}/{export_url.split('/')[-1]}",
				headers=self.download_headers,
			)
		else:
			logger.error(f"Failed to get exportURL for {name}")

		return {
			"state": state,
			"name": name,
			"exportURL": export_url,
			"pagesExported": pages_exported,
		}

	def _wait_for_export_completion(self, task_id) -> Tuple[dict, str, str, int]:
		"""Helper method to wait until the export is complete or failed."""
		while True:
			status = self._get_status(task_id)
			if not status:
				time.sleep(1)
				continue
			state = status.get("state")
			error = status.get("error")
			if state == "failure" or status.get("status", {}).get("exportURL"):
				return (
					status,
					state,
					error,
					status.get("status", {}).get("pagesExported"),
				)
			time.sleep(1)

	def export(self):
		logger.info(f"Exporting {len(self.pages)} pages...")
		with ThreadPoolExecutor() as executor:
			futures = []
			with tqdm(total=len(self.pages), dynamic_ncols=True) as pbar:
				for page in self.pages.items():
					futures.append(executor.submit(self._process_page, page))
				for future in futures:
					result = future.result()
					if result["state"] == "failure":
						continue
					name = result["name"]
					pagesExported = result["pagesExported"]

					pbar.set_postfix_str(
						f"Exporting {name}... {pagesExported} pages already exported"
					)
					pbar.update(1)

		utils.unzip_all(self.export_directory)
		# Rename the extracted pages to the page names provided from self.pages
		utils.rename_extracted_pages(
			path=self.export_directory, pages=self.pages, format=self.export_type
		)
