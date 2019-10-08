"""
Main entrypoint for ocupgrader.
"""

import argparse
import logging
from sh import ErrorReturnCode
import sys

from ocdeployer.utils import oc, load_cfg_file
import yaml

from .schema import validate_schema

log = logging.getLogger("ocupgrader")
logging.basicConfig(level=logging.INFO)


def set_oc_project(args):
    try:
        oc("project", args.project, _reraise=True)
    except ErrorReturnCode:
        log.error("You should log in to your cluster before upgrading and make sure you can access specified project:")
        log.error("  $ oc login https://api.myopenshift --token=*************")
        log.error("  $ oc project %s", args.project)
        sys.exit(2)


def get_project_spec(args):
    try:
        return load_cfg_file(args.file)
    except ValueError as e:
        log.error(e)
        sys.exit(3)


def list_tasks(args, project_spec):
    log.info("Available tasks:")
    for task_name in project_spec["tasks"]:
        log.info("  %s (%s)", task_name, project_spec["tasks"][task_name]["description"])


def run_task(args, project_spec):
    task_name = args.task
    if task_name in project_spec["tasks"]:
        log.info("Executing task: %s", task_name)
        for command in project_spec["tasks"][task_name]["commands"]:
            oc(command)
    else:
        log.error("Task doesn't exist in project spec: '%s'", task_name)
        sys.exit(5)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project", action="store", help="target OpenShift project")
    parser.add_argument("-f", "--file", action="store", default=".ocupgrader.yml",
                        help="project file with upgrade tasks specification (default: '%(default)s')")
    subparsers = parser.add_subparsers(dest="subcommand")
    subparsers.add_parser("list-tasks", help="list available tasks")
    run_parser = subparsers.add_parser("run", help="run given task")
    run_parser.add_argument("task", help="task name")
    args = parser.parse_args()
    
    set_oc_project(args)
    project_spec = get_project_spec(args)
    if not validate_schema(project_spec):
        log.error("Error validating project spec.")
        sys.exit(4)

    if args.subcommand == "run":
        run_task(args, project_spec)
    elif args.subcommand == "list-tasks":
        list_tasks(args, project_spec)
    else:
        log.error("No subcommand specified. Nothing to do.")
        sys.exit(1)

if __name__ == "__main__":
    main()
