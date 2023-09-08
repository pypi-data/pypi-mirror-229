import os.path
import configparser
import plumbum
from plumbum.path.utils import copy
from .tools import env


def get_ssh(
        host = env("IP_ADDRESS"),
        user = env("SSH_USER"),
        keyfile = env("SSH_KEYFILE"),
        sudo = False,
    ):
    ssh = plumbum.SshMachine(host, user=user, keyfile=keyfile)
    if sudo:
        return ssh["sudo"]
    return ssh


def sudo_systemctl(
        command = "status", 
        unit = env("SERVICE_NAME"),
    ):
    ssh = get_ssh(sudo=True)
    result = ssh["systemctl"](command, unit)
    return result

    
def start_server(service_name = env("SERVICE_NAME")):
    return sudo_systemctl("start", service_name)


def stop_server(service_name = env("SERVICE_NAME")):
    return sudo_systemctl("stop", service_name)


def restart_server(service_name = env("SERVICE_NAME")):
    return sudo_systemctl("restart", service_name)


def save_config(config, dest):
    dest_filename = os.path.basename(dest)
    temp = f"work/{dest_filename}"
    with open(temp, "w") as fp:
        config.write(fp)
        fp.flush()
    print(f"Flushed to {temp}, copying...")
    ssh = get_ssh()
    copy(temp, ssh.path(dest))
    print(f"Copied to {dest}.")


def odoo_config(
        base_path = env("BASE_PATH"),
        use_https = env("USE_HTTPS", flag=True),
        http_port = env("HTTP_PORT"),
        gevent_port = env("GEVENT_PORT"),
        db_host = env("DB_HOST"),
        db_port = env("DB_PORT"),
        db_user = env("DB_USER"),
        db_password = env("DB_PASSWORD"),
        db_name = env("DB_NAME"),
    ):
    # Values must always be strings for CP to work.
    config = configparser.ConfigParser(interpolation=None)
    config["options"] = {
        "http_interface": "127.0.0.1" if use_https else "0.0.0.0",
        "http_port": http_port, 
        "gevent_port": gevent_port, 
        "db_host": db_host,
        "db_port": db_port,
        "db_user": db_user,
        "db_password": db_password,
        "pidfile": f"{base_path}/server.pid",
        "addons_path": f"{base_path}/addons",
        "proxy_mode": str(use_https),
        "list_db": "False",
        "limit_memory_hard": "1073741824",
        "limit_memory_soft": "805306368",
        "limit_time_cpu": "45",
        "limit_time_real": "90",
        "max_cron_threads": "1",
        "workers": "2",
    }
    save_config(config, f"{base_path}/odoo/odoo.conf")


def create_service(
        service_name = env("SERVICE_NAME"),
        description = env("DESCRIPTION"),
        documentation = env("DOCUMENTATION"),
        service_user = env("SERVICE_USER"),
        base_path = env("BASE_PATH"),
        venv_dir = env("VENV_DIR"),
    ):
    bin_path = f"{base_path}/{venv_dir}/bin/python3"
    odoo_bin = f"{base_path}/odoo/odoo-bin"
    odoo_conf = f"{base_path}/odoo/odoo.conf"
    service_file = f"{base_path}/odoo.service"
    config = configparser.ConfigParser(interpolation=None)
    config["Unit"] = {
        "Description": description,
        "Documentation": documentation,
    }
    config["Service"] = {
        "User": service_user,
        "ExecStart": f"{bin_path} {odoo_bin} -c {odoo_conf}",
    }
    config["Install"] = {
        "WantedBy": "default.target",
    }
    save_config(config, service_file)
    ssh = get_ssh(sudo=True)
    ssh["cp"](service_file, f"/etc/systemctl/system/{service_name}.service")
        

def clone_repo(
        git_repo = env("GIT_REPO"),
        branch = env("GIT_BRANCH"),
        local_repo = env("LOCAL_REPO"),
    ):
    ssh = get_ssh()
    ssh["rm"]("-rf", local_repo)
    ssh["git"]("clone", "--branch", branch, "--single-branch", "--depth", 100, git_repo, local_repo)
    ssh["rm"]("-rf", f"{local_repo}/.git")


def install_odoo(
        base_path = env("BASE_PATH"),
        venv_dir = env("VENV_DIR"),
        local_repo = env("LOCAL_REPO"),
    ):
    ssh = get_ssh()
    ssh["mkdir"]("-p", base_path)
    result = ssh["cp"]("-R", f"{local_repo}/", f"{base_path}")
    ssh["python3"]("-m", "venv", f"{base_path}/{venv_dir}")
    ssh["chmod"]("+x", f"{base_path}/odoo/odoo-bin")
    odoo_config(use_https=False)
    create_service()
    start_server()

