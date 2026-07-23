from flask import Flask, render_template, request, redirect, flash
import subprocess, yaml


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/create-user", methods=["POST"])
def create_user():

    username = request.form["username"]
    fullname = request.form["fullname"]

    print(f"Creating {username}")

    with open("zos-ansible/vars/users.yml", "r") as f:
        data = yaml.safe_load(f)

    existing_uids = [
        user.get("uid", 8000)
        for user in data["racf_users"]
    ]

    existing_users = [
        user.get("userid")
        for user in data["racf_users"]
    ]

    next_uid = max(existing_uids, default=8040) + 1

    user = {
        "userid": username,
        "name": fullname,
        "default_group": "{{ team_group }}",
        "password": "TEMP123",
        "account": "ACCT001",
        "procedure": "DB13PROC",
        "uid": next_uid,
    }

    data["racf_users"].append(user)

    if username in existing_users:
        return f"""
        <h2>User already exists ⚠️</h2>

        <p>
            The userid <strong>{username}</strong> is already in use.
        </p>

        <a href="/">Try another userid</a>
        """


    with open("zos-ansible/vars/users.yml", "w") as f:
        yaml.dump(data, f, sort_keys=False)

    result = subprocess.run(
        [
            "ansible-playbook",
            "-i",
            "zos-ansible/inventory/hosts.yml",
            "--private-key",
            "/home/ansible/.ssh/id_rsa",
            "zos-ansible/playbooks/create_users.yml",
        ],
        [
            "ansible-playbook",
            "-i",
            "zos-ansible/inventory/hosts.yml",
            "--private-key",
            "/home/ansible/.ssh/id_rsa",
            "zos-ansible/playbooks/sync_seed_libraries.yml",
        ],
        [
            "ansible-playbook",
            "-i",
            "zos-ansible/inventory/hosts.yml",
            "--private-key",
            "/home/ansible/.ssh/id_rsa",
            "zos-ansible/playbooks/sync_user_libraries.yml",
        ]
    )


    return f"""
    <h2>Provision Result</h2>

    <pre>
    {result.stdout}
    {result.stderr}
    </pre>
    """


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )