import os
import sys
import requests
import time
from loguru import logger

from flowdeploy.keys import get_key

FLOWDEPLOY_BASE_URL = os.environ.get("FLOWDEPLOY_API_URL", "https://api.toolche.st")


def nextflow(pipeline, outdir, pipeline_version, inputs=None, cli_args="", export_location=None, profiles=None,
             run_location=None, is_async=False, **kwargs):
    if export_location is not None and export_location.startswith('fd://'):
        raise ValueError("Export location is for locations outside FlowDeploy. "
                         "Use 'outdir' to place results where you want in the shared file system.")
    if not outdir.startswith('fd://'):
        raise ValueError("Path in outdir must be within the shared file system.")

    # Create the request payload
    payload = {
        "pipeline": pipeline,
        "inputs": inputs,
        "cli_args": cli_args,
        "pipeline_version": pipeline_version,
        "outdir": outdir,
        "export_location": export_location,
        "profiles": profiles,  # might want to add a separate "parallelize" arg and join with profiles
        "run_location": run_location,
    }
    api_key = get_key(kwargs.get('cli', False))
    headers = {
        "Authorization": f"Key {api_key}",
        "Content-Type": "application/json",
    }
    # Step 1: Create a new FlowDeploy instance
    response = requests.post(f"{FLOWDEPLOY_BASE_URL}/flowdeploy/nf", json=payload, headers=headers)

    if response.status_code != 200:
        error_json = response.json()
        error = error_json['error'] or 'Unknown'
        logger.error(f"Failed to create FlowDeploy instance. Error: {error}")
        return

    task_id = response.json()["id"]
    logger.info(f"FlowDeploy instance created. Task ID: {task_id}")
    logger.info(f"You can view the running job at https://app.flowdeploy.com/dashboard/{task_id}?runType=1")

    if is_async:
        logger.info("Async Toolchest initiation is complete!")
        return

    counter = 0
    state = ''
    while state not in ["COMPLETE", "CANCELED", "EXECUTOR_ERROR", "SYSTEM_ERROR"]:
        if counter % 10 == 0:  # Check state every 10 seconds
            response = requests.get(f"{FLOWDEPLOY_BASE_URL}/tes/v1/tasks/{task_id}", headers=headers)
            task_info = response.json()
            state = task_info.get("state")

        status_message = f"State: {state} ({'*' * (counter % 10 + 1)}) "

        sys.stdout.write(
            f"\r{status_message}".ljust(120),
        )
        sys.stdout.flush()

        counter += 1
        time.sleep(1)

    sys.stdout.write(
        f"\rState: {state}".ljust(120) + '\n',
    )
    sys.stdout.flush()
    logger.info("FlowDeploy process finished.")
