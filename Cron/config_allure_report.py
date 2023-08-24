import json
import os
import shutil

import sys


def allure_misc_config(file_name):
    file_path = f'{os.path.join(os.getcwd(), "reports", "html", file_name)}'
    with open(file_name + '/widgets/summary.json', "r") as jsonFile:
        data = json.load(jsonFile)

    data["reportName"] = "Shuttle-Wallet"

    with open(file_name + '/widgets/summary.json', "w") as jsonFile:
        json.dump(data, jsonFile)

    jsonFile.close()
    html_update(file_name)
    copytree(file_name)


def html_update(file_path):
    with open(file_path + '/index.html', "r+") as html:
        lines = html.readlines()
        for i, line in enumerate(lines):
            if line.__contains__('link'):
                lines[i] = lines[
                               i].rstrip() + '\n <link rel = "stylesheet" href = "plugins/custom-logo-plugin/static/styles.css">' + '\n'
                break
        html.seek(0)
        for line in lines:
            html.write(line)


def copytree(file_path):
    root_dir = os.listdir(os.getcwd())
    if os.path.exists(f'{file_path}/plugins/custom-logo-plugin') is False:
        os.mkdir(f'{file_path}/plugins/custom-logo-plugin')
    for dirs in root_dir:
        if dirs == 'custom-logo-plugin':
            shutil.copytree(src=f'{os.getcwd()}/custom-logo-plugin', dst=f'{file_path}/plugins/custom-logo-plugin',
                            dirs_exist_ok=True)
            break





def get_file_name():
    filename = sys.argv[1]
    return filename
