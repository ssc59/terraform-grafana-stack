# worker.py
from pathlib import Path
import subprocess
import json

import db


def process_employee(employee_number):
    employee = db.get_user(employee_number)

    if employee is None:
        raise ValueError(f"Employee {employee_number} does not exist")

    TERRAFORM_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "terraform-team02"
    )

    print(f"Running Terraform from: {TERRAFORM_DIR}")
    
    subprocess.run(
        [
            "terraform",
            "apply",
            "-auto-approve",
        ],
        cwd="../terraform-team02",
        check=True,
    )

    
    ansible_vars = {
            "team_group": "TEAM02",
            "team_gid": 8022,
            "racf_users": [
                {
                    "userid": employee["user_id"],
                    "name": employee["name"],
                    "default_group": "TEAM02",
                    "password": employee["user_id"],
                    "account": employee["account"],
                    "procedure": employee["procedure"],
                    "uid": employee["zos_uid"],
                }
            ],
        }

    ANSIBLE_DIR = (
    Path(__file__).resolve().parent.parent
    / "zos-ansible"
    )

    #Run: sync_user_libraries.yml
    try:
        subprocess.run(
            [
                "ansible-playbook",
                "-i",
                "inventory/hosts.yml",
                "playbooks/sync_user_libraries.yml",
                "--extra-vars",
                json.dumps(ansible_vars),
            ],
            cwd=ANSIBLE_DIR,
            check=True,
        )
    except:
        print("sync_user_libraries.yml failed")

    #Run: create_users.yml
    try:
        subprocess.run(
            [
                "ansible-playbook",
                "-i",
                "inventory/hosts.yml",
                "playbooks/create_users.yml",
                "--extra-vars",
                json.dumps(ansible_vars),
            ],
            cwd=ANSIBLE_DIR,
            check=True,
        )
    except:
        print("create_users.yml failed")