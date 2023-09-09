# NotionDL

Designed to simplify the process of exporting content from Notion. It provides an interface to configure, trigger, and download content exports from Notion. The class supports exporting content in various formats (Markdown, HTML, PDF) and also allows users to choose the scope of the export (current view vs. all content).

## Features

- Export content in **Markdown**, **HTML**, or **PDF** format.
- Configure the scope of your export: **current view** or **all content**.
- Option to include or exclude files in the export.
- Flatten the file tree structure upon export.
- Export multiple pages concurrently for faster processing.
- Monitor export progress with a progress bar.
- Automatically unpack zipped export files.

## Installation
```bash
pip install notiondl
```

## Usage
### CLI
```bash
python -m notiondl <PAGE_ID> -t <EXPORT_TYPE> --no-file -v
```
#### Avaialbe Options
| Argument | Description |
| --- | --- |
| `PAGE_ID` (required) | The ID of the Notion page you want to export. Separate multiple pages with commas. |
| `-d`, `--export-dir` | The directory to export the page to. Defaults to the current directory. |
| `-t`, `--export-type` | The type of file to export. Defaults to HTML. |
| `-l`, `--no-file` | Do not export files attached to the page. Defaults to False. |
| `-k`, `-keep-structure` | Keep the page hierarchy when exporting. Defaults to False. |
| `-s`, `--single-page` | Do not export child pages. Defaults to False. |
| `-w`, `--rewrite` | Do not create date-formated folders for each export. Defaults to False. |
| `-v`, `--verbose` | Whether to print verbose output. Defaults to False. |
| `-c`, `--current-view` | The type of view to export. Defaults to the currentView. |
You can set whether `NOTION_TOKEN_V2` and `NOTION_FILE_TOKEN` environment variables or providing these as CLI arguments
| `--token-v2` | The token_v2 cookie value from your Notion session. |
| `--file-token` | The file-token cookie value from your Notion session. |


### Python
```python
import notiondl

exporter = notiondl.NotionExporter(
    token_v2="<TOKEN>",
    file_token="<FILE_TOKEN>",
    pages={"index.html": "<PAGE_ID>"},
    export_directory="test",
    flatten_export_file_tree=True,
    export_type=notiondl.ExportType.HTML,
    current_view_export_type=notiondl.ViewExportType.CURRENT_VIEW,
    include_files=True,
    recursive=True,
    rewrite=True,
)
exporter.export()
```

## Requirements
In case of CLI, you have to set `NOTION_TOKEN_V2` and `NOTION_FILE_TOKEN` environment variables.
You will need to get the `token_v2` and `file_token` values from your Notion cookies. The `pages` dictionary should contain pairs of `page_name: page_id` for each page you want to export. `page_name` can be anything and would be used for the final downloaded file name.

### Needed Cookies

To export anything from Notion, one needs to authenticate oneself with some
Cookies (like a browser would). These cookies are called `token_v2` and
`file_token`. They are set on all requests of a logged in user when using the
Notion web-app.

#### How to retrieve the Cookies?

- Go to [notion.so](https://notion.so).
- Log in with your account.
- Open the developer tools of your browser, open Application > Storage > Cookies
  (Chrome); Storage tab (Firefox).
- Copy the value of the Cookies called `token_v2` and `file_token` and paste
  them somewhere safe.
- ⚠️ If you don't find `file_token`, you need to have at least had exported a file manually once.
- Those cookies have a **1 year validity**, so you don't need to do this often.

## License
[MIT](./LICENSE)

## Acknowledgement
https://github.com/Strvm/python-notion-exporter