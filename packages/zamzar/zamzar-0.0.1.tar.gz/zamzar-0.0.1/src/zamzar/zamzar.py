import re
import os
import sys
import time
import requests
from requests.auth import HTTPBasicAuth

api_key_init = None

def main():
    api_key = input("api密钥：")
    api_key_init = api_key
    suffix = re.compile(r'\.(\w)+')
    source_file = input("转换前文件（绝对路径+文件名+后缀名）：")
    target_format = input("转换格式（不加句点）：")
    endpoint = f"https://sandbox.zamzar.com/v1/formats/{suffix.search(source_file).group()[1:]}"
    formats = []

    file_content = {"source_file": open(source_file, "rb")}
    data_content = {"target_format": target_format}
    print("请求中...")
    res = requests.get(endpoint, auth=HTTPBasicAuth(api_key, ''))
    for i in res.json()["targets"]:
        formats.append(i["name"])
    if target_format not in formats:
        print("无法转换。")
        print("仅能转换至如下格式：")
        for i in formats:
            print(f'-{i}')
        return
    file_content = {'source_file': open(source_file, 'rb')}
    data_content = {'target_format': target_format}
    endpoint = "https://sandbox.zamzar.com/v1/jobs"
    res = requests.post(endpoint, data=data_content, files=file_content, auth=HTTPBasicAuth(api_key, ''))
    if res.json().get("errors") != None:
        print(f"错误代码:{res.json()['errors'][0]['code']}")
        print(f"错误信息:{res.json()['errors'][0]['context']}\n{res.json()['errors'][0]['message']}")
        return
    job_id = res.json()['id']
    print("转换中...")
    while True:
        response = requests.get(endpoint, auth=HTTPBasicAuth(api_key, ''))
        if response.json()["data"][0]['status'] == 'successful':
            break
        time.sleep(1)
    file_id = response.json()["data"][0]['target_files'][0]["id"]
    local_filename = f'{response.json()["data"][0]["target_files"][0]["name"]}'

    print("下载中...")

    endpoint = f"https://sandbox.zamzar.com/v1/files/{file_id}/content"
    resp = requests.get(endpoint, stream=True, auth=HTTPBasicAuth(api_key, ''))

    try:
      with open(local_filename, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=1024):
          if chunk:
            f.write(chunk)
            f.flush()

        print("下载完成。")
        print(f'它在\"{os.getcwd()}\"。')

    except IOError:
      print("下载错误，请检查权限后重试。")

def format_factory(source_file, target_format, api = None):
    if api:
        api_key_init = api
    else:
        if api_key:
            api_key_init = api_key
        else:
            raise ValueError("miss api key")

    suffix = re.compile(r'\.(\w)+')
    endpoint = f"https://sandbox.zamzar.com/v1/formats/{suffix.search(source_file).group()[1:]}"      
    formats = []

    file_content = {"source_file": open(source_file, "rb")}
    data_content = {"target_format": target_format}
    res = requests.get(endpoint, auth=HTTPBasicAuth(api_key, ''))
    for i in res.json()["targets"]:
        formats.append(i["name"])
    if target_format not in formats:
        raise AssertionError("cannot convert this format")
        
    file_content = {'source_file': open(source_file, 'rb')}
    data_content = {'target_format': target_format}
    endpoint = "https://sandbox.zamzar.com/v1/jobs"
    res = requests.post(endpoint, data=data_content, files=file_content, auth=HTTPBasicAuth(api_key, ''))
    if res.json().get("errors") != None:
        raise WindowsError(f"massage:{res.json()['errors'][0]['context']}{res.json()['errors'][0]['message']}\ncode:{res.json()['errors'][0]['code']}")
    job_id = res.json()['id']
    while True:
        response = requests.get(endpoint, auth=HTTPBasicAuth(api_key, ''))
        if response.json()["data"][0]['status'] == 'successful':
            break
        time.sleep(1)
    file_id = response.json()["data"][0]['target_files'][0]["id"]
    local_filename = f'{response.json()["data"][0]["target_files"][0]["name"]}'


    endpoint = f"https://sandbox.zamzar.com/v1/files/{file_id}/content"
    resp = requests.get(endpoint, stream=True, auth=HTTPBasicAuth(api_key, ''))

    with open(local_filename, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
    return str(Path.cwd() / Path(local_filename))

def farmat_search(format_, api = None):
    if api:
        api_key_init = api
    else:
        if api_key:
            api_key_init = api_key
        else:
            raise ValueError("miss api key")
    formats = []

    file_content = {"source_file": open(source_file, "rb")}
    data_content = {"target_format": target_format}
    endpoint = "https://sandbox.zamzar.com/v1/formats/format_"          
    res = requests.get(endpoint, auth=HTTPBasicAuth(api_key, ''))
    for i in res.json()["targets"]:
        formats.append(i["name"])
    return formats

def api_fill(api):
    api_key = api




