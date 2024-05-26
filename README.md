# NetScraper

Customizable internet resource scraper. Opens a selenium browser and records network response URLs as the user browses (or through the use of an automation script).

## Setup

```
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Customization

Key command line arguments for main.py:

- `--url`: URL to start selenium in
- `--autonav`: Automation script in `autonav` folder. Scripts in this folder should not be committed to this repository.
- `--filters`: Comma separated string to apply filters to URL capturing. Script in `filters` folder are general filters (e.g. filtering out images), where as scripts in `personal/filters` folder is meant for personal use, specific to user's own needs

## TODO

- Serialization of cookies used when accessing resources