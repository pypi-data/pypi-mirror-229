import os
import subprocess


def run(command):
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")


def env(var, flag=False):
    var = os.environ[var]
    assert var, f"Missing required env variable {var}"
    if flag:
        return var.upper() in ("TRUE", "Y", "YES", "1", "ENABLE", "ON")
    return var


def slugify(value) -> str:
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    value = re.sub(r'[-\s]+', '-', value)
    return value


def set_site(name):
    # TODO: Check if the file is well-formed before overwritting
    shutil.copy(f"sites/.env.{name}", ".env")

