import json
import time
from pathlib import Path

from selenium.common.exceptions import JavascriptException

from .config import load_config
from .pbi import PowerBIClient
from .scraping import copy_html, load_url


def run(project_dir=None, clean=True):
    """Run the load test"""

    if not project_dir:
        project_dir = Path().cwd()

    pbi_client = PowerBIClient()
    token_path = pbi_client.dump_token(path=project_dir)

    config = load_config()

    workspace_name = config["workspace"]
    print(workspace_name)
    report_name = config["report"]
    print(report_name)
    page_name = config.get("page", "")
    print(page_name)

    # Get Workspace
    workspace_id = pbi_client.get_workspace_id(workspace_name)

    if not workspace_id:
        raise Exception

    print(f"Workspace ID: {workspace_id}")

    # Get Report
    report = pbi_client.get_report(workspace_id, report_name)
    report_url = report["embedUrl"]
    report_id = report["id"]

    print(f"Report ID: {report_id}")

    # Get Page
    page = pbi_client.get_page(workspace_id, report_id, page_name)
    page_id = page["name"]

    print(f"Page ID: {page_id}")

    # Fitlers
    slicers = config.get("slicers", [])
    filters = config.get("filters", [])

    report_path = project_dir / "parameters.json"

    report_dict = {
        "reportUrl": report_url,
        "reportId": report_id,
        "pageName": page_id,
        "sessionRestart": 100,
        "slicers": slicers,
        "filters": filters,
    }

    report_parameter_str = json.dumps(report_dict)

    report_str = "reportParameters={0};".format(report_parameter_str)

    with open(report_path, "w", encoding="utf8") as report_file:
        report_file.write(report_str)

    project_filepath = copy_html(project_dir).absolute()

    fileurl = f"file:///{project_filepath}"

    driver = load_url(fileurl)

    duration = None

    while not duration:
        try:
            duration = driver.execute_script("return duration")

        except JavascriptException:
            time.sleep(1)

    print(f"Duration: {duration}s")

    input("Press Enter to continue...")

    driver.quit()

    if clean:
        print("Start cleaning...")
        Path(report_path).unlink()
        Path(token_path).unlink()
        Path(project_filepath).unlink()
