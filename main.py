"""
Capture network responses and save them to JSON file for reference or further processing.
"""

from importlib import import_module
from pathlib import Path
from os import path
import kthread
import argparse
import json
import time
from selenium import webdriver


def remove_dup(iterable):
    """
    Utility function to remove duplicates.
    This implementation maintains insertion order.

    Returns:
        list[any]: New list with duplicates removed
    """
    seen = set()
    seen_add = seen.add
    return [x for x in iterable if not (x in seen or seen_add(x))]


if __name__ == "__main__":
    # Command line arguments setup
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url",
        type=str,
        default="about:blank",
        help="Default URL to navigate to. If not specified, blank page will be shown.",
    )
    parser.add_argument(
        "--autonav",
        type=str,
        help="Auto navigation script in `autonav` folder. Each autonav script should contain a function named `func` and takes in a Selenium WebDriver as an argument",
    )
    parser.add_argument(
        "--filters",
        type=str,
        default="",
        help="Filters to apply when capturing network response URLs.",
    )

    # Retrieve command line arguments
    args = parser.parse_args()
    url = args.url
    autonav = args.autonav
    filters_str = args.filters

    # Process command line arguments
    input_filters = filters_str.split(",")
    filters = []
    autonav_func = None

    # For each filter specified, attempt import
    for specified_filter in input_filters:
        try:
            imp = import_module(f"filters.{specified_filter}")
            filters.append(imp.func)
        except ModuleNotFoundError:
            print(
                f'Ensure that your filter `{specified_filter}` has a corresponding python file in the `filters` folder. For personal filters, attach a "personal." prefix. e.g. --filters images,personal.myfilter'
            )
            exit()
        except AttributeError:
            print(
                f"Ensure that your python file for `{specified_filter}` exports a filter function named `func`."
            )
            exit()

    # Attempt importing autonav function
    try:
        autonav_imp = import_module(f"autonav.{autonav}")
        autonav_func = autonav_imp.func
    except ModuleNotFoundError:
        print(
            f"Ensure that your specified autonav `{autonav}` exists in the `autonav` folder."
        )
        exit()
    except AttributeError:
        print(
            f"Ensure that your python file for `{autonav}` autonav exports a function named `func`, which takes in a Selenium WebDriver as an argument."
        )
        exit()

    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    # Initialize the WebDriver
    driver = webdriver.Chrome(options=options)

    # Enable network tracking
    driver.execute_cdp_cmd("Network.enable", {})

    # Visit the website
    driver.get(url)

    # If autonav function specified, run the function in a separate thread
    if autonav is not None:
        print(f"Running autonav function `{autonav}`.")
        thread = kthread.KThread(target=autonav_func, args=(driver,))
        thread.start()

    # File to save URLs to
    FOLDER = "data"
    timestr = time.strftime("%Y%m%d-%H%M%S")
    file_name = f"{timestr}.json"
    file_path = path.join(FOLDER, file_name)

    # Save to file every 3 seconds to backup, and also upon closing.
    urls = []

    # Ensure parent folders are created
    Path(FOLDER).mkdir(parents=True, exist_ok=True)

    # Main loop: Save network responses to disk every second
    while True:
        # Fetch the performance logs
        logs = driver.get_log("performance")

        # Extract URLs of all image resources
        new_urls = []
        for log in logs:
            log_data = json.loads(log["message"])["message"]

            # For each log, run it through specified filter functions, if any
            if all(filter_func(log_data) for filter_func in filters):
                params = log_data["params"]
                response = params["response"]
                urls.append(response.get("url", ""))

        # Ensure duplicates removed
        urls = remove_dup(urls)

        with open(file_path, "w", encoding="utf8") as f:
            json.dump(urls, f, indent=4)
            print(f"Total URLs recorded: {len(urls)}")

        time.sleep(1)
