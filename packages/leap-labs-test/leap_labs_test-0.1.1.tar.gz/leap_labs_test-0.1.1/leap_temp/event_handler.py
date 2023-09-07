import atexit
import threading
import os
import requests

NUMBER_PRIORITY = 3


class LeapLogger:
    def __init__(self, leap_api_key, config):
        self.base_url = 'https://front-end-one-woad.vercel.app/api'
        self.job_id = None
        self.headers = {
            "x-api-key": leap_api_key}

        response = requests.get(
            f"{self.base_url}/auth/verify-api-key", headers=self.headers)
        if not response.ok:
            print("Oops, you don't seem to have a valid Leap API key. Head over to https://app.leap-labs.com/ to generate one!")
            exit()

        atexit.register(self.finish)
        response = requests.post(f"{self.base_url}/events/job/start",
                                 headers=self.headers,
                                 json={
                                     "config": config})
        if response.ok:
            self.job_id = response.json()["job_id"]
        else:
            self.finish(
                error=True, error_message=f"Failed to start job: {response}")

    def upload_file(self, iteration_step, file_path, content_type):
        entity_name = file_path.split('/')[-1]
        ext = entity_name.split('.')[-1]

        # get url to sent file to
        body = {
            'job_id': self.job_id,
            'step': iteration_step,
            'entity_name': entity_name,
            'content_type': f'{content_type}/{ext}'}

        response = requests.post(
            f"{self.base_url}/events/job/upload", headers=self.headers, json=body)

        if response.ok:
            upload_url = response.json()["upload_url"]
            key = response.json()["key"]
        else:
            self.finish(
                error=True, error_message=f"Failed to get upload URL: {response}")

        with open(file_path, 'rb') as f:
            response = requests.put(upload_url, data=f)
        if response.ok:
            return key
        else:
            self.finish(
                error=True, error_message=f"Failed to get upload key: {response}")

    def upload_log(self, iteration_step, payload):
        # entity_type in ['IMAGE', 'STRING', 'NUMBER', 'CHART_JSON', 'VEGA'] (value for vega is just the json vega spec)
        # IMG is json object that contains key (from upload file), and caption
        body = {
            "step": iteration_step,
            "job_id": self.job_id,
            "payload": payload}
        response = requests.post(
            f"{self.base_url}/events/job/record", headers=self.headers, json=body)

        if not response.ok:
            self.finish(
                error=True, error_message=f"Failed to upload log: {response}")

    def finish(self, error=False, error_message=None):
        if error:
            print(f'Failed with {error_message}')
        print('Finishing...')

        body = {
            "job_id": self.job_id,
            "error": error,
            "error_message": error_message}
        response = requests.post(
            f"{self.base_url}/events/job/end", headers=self.headers, json=body)
        if not response.ok:
            raise Exception(f"Failed to end job: {response}")

    def log(self, step, data_log, file_log):
        threading.Thread(target=self.log_thread, args=(
            step, data_log, file_log)).start()
        return

    def log_thread(self, step, data_log, file_log):
        payload = []
        for k, v in data_log.items():
            if isinstance(v, dict):
                payload.append({
                    "name": k,
                    "type": 'NUMBER',
                    "value": v,
                    "priority": NUMBER_PRIORITY})
            elif v.content_type in ['IMAGE', 'STRING', 'NUMBER', 'VEGA']:
                payload.append({
                    "name": k,
                    "type": v.content_type,
                    "value": v.data,
                    "priority": v.priority})

        for k, v in file_log.items():
            if isinstance(v, list):
                for file in v:
                    key = self.upload_file(
                        step, file.path, content_type=file.content_type)
                    payload.append({
                        "name": k,
                        "type": file.content_type,
                        "value": {
                            "key": key,
                            "caption": file.caption},
                        "priority": file.priority})
            else:
                key = self.upload_file(
                    step, v.path, content_type=v.content_type)
                payload.append({
                    "name": k,
                    "type": v.content_type,
                    "value": {
                        "key": key,
                        "caption": v.caption},
                    "priority": v.priority})

        if payload:
            self.upload_log(step,
                            {
                                "data": payload})
