# worker.py
from pathlib import Path
from threading import Thread
from datetime import datetime
import subprocess
import json
import traceback

import db


'''
Runs process_employee with threading, to allow for several workers at a time.
'''
def run_employee_worker(employee_number):
    log_dir = Path("/tmp/employee-worker-logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_path = log_dir / f"employee-{employee_number}.log"

    thread = Thread(
        target=process_employee,
        args=(employee_number, log_path),
        daemon=False,
        name=f"employee-{employee_number}",
    )

    thread.start()
    return thread


'''
Creates user AWS instances and user accounts in all systems.
'''
def process_employee(employee_number, log_path):

    # Create Logs Per User
    with open(log_path, "w", encoding="utf-8") as log:
        try:
            log.write(
                f"Started employee worker at {datetime.now()}\n"
                f"Employee number: {employee_number}\n\n"
            )
            log.flush()
    
            employee = db.get_user(employee_number)
            if employee is None:
                raise ValueError(f"Employee {employee_number} does not exist")

            TERRAFORM_DIR = (
                Path(__file__).resolve().parent.parent
                / "terraform-end-user"
            )
          
            all_employees = db.get_all_users()

            team_users = [
                user["user_id"]
                for user in all_employees
            ]

            log.write(f"Running Terraform from: {TERRAFORM_DIR}\n")
            log.write(f"Terraform users: {team_users}\n")
            log.flush()

            subprocess.run(
                [
                    "terraform",
                    "apply",
                    "-auto-approve",
                    "-var",
                    f"team_users={json.dumps(team_users)}",
                ],
                cwd=TERRAFORM_DIR,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
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
                            "procedure": employee["proc"],
                            "uid": employee["zos_uid"],
                        }
                    ],
                }

            ANSIBLE_DIR = (
            Path(__file__).resolve().parent.parent
            / "zos-ansible"
            )
            '''
            #Run: report.yml
            try:
                subprocess.run(
                    [
                        "ansible-playbook",
                        "-i",
                        "inventory",
                        "report.yml",
                        "--extra-vars",
                        json.dumps(ansible_vars),
                    ],
                    cwd=ANSIBLE_DIR,
                    check=True,
                )
            except:
                print("report.yml failed") 
            '''

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
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    text=True,
                    check=True,
                )
            except Exception:
                log.write("\nWORKER FAILED\n")
                log.write(traceback.format_exc())
                log.flush()

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
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    text=True,
                    check=True,
                )
            except Exception:
                log.write("\nWORKER FAILED\n")
                log.write(traceback.format_exc())
                log.flush()

            log.write("\nWorker completed successfully.\n")
            log.flush()
        except Exception:
            log.write("\nWORKER FAILED\n")
            log.write(traceback.format_exc())
            log.flush()