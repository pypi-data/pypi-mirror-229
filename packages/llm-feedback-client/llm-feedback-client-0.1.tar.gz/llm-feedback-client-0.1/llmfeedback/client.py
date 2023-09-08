import requests
import uuid
import hashlib

class Client:
    def __init__(self, project_id, api_key, base_url="https://api.llmfeedback.com"):
        self.project_id = project_id
        self.api_key = api_key
        self.base_url = base_url

    def register_config(self, config_name, config):
        print(f"Config {config_name} registered:", config)

        config_request_body = {
            "project_id": self.project_id,
            "name": config_name,
            "config": config
        }

        response = requests.put(f"{self.base_url}/api/v0/register-llm-config", json=config_request_body)
        if response.status_code != 200:
            print(f"HTTP error! Status: {response.status_code}")

        return config_name

    @staticmethod
    def content_uuid(s, time=None):
        time_stamp = time if time else str(uuid.uuid4().time)
        res = s + time_stamp
        hash_result = hashlib.md5(res.encode('utf-8')).hexdigest()

        # Convert the hash to UUID format
        result = [
            hash_result[:8],
            hash_result[8:12],
            hash_result[12:16],
            hash_result[16:20],
            hash_result[20:]
        ]
        return '-'.join(result)

    def store_content(self, content, config_name, id=None, group_id=None, created_by=None):
        content_id = id if id else str(uuid.uuid4())
        print(f"Content stored with ID {content_id} and config {config_name}:", content)

        request_body = {
            "content": content,
            "id": content_id,
            "project_id": self.project_id,
            "config_name": config_name
        }

        if created_by:
            request_body["created_by"] = created_by
        if group_id:
            request_body["group_id"] = group_id

        response = requests.put(f"{self.base_url}/api/v0/store-content", json=request_body)
        if response.status_code != 200:
            print(f"HTTP error! Status: {response.status_code}")

        return content_id

    def log_dialogue(self, instruction, response, config_name, id=None, group_id=None, created_by=None):
        id = id if id else str(uuid.uuid4())
        print(f"Dialogue stored with ID {id} and config {config_name}:", instruction, response)

        request_body = {
            "instruction": instruction,
            "response": response,
            "id": id,
            "project_id": self.project_id,
            "config_name": config_name
        }

        if created_by:
            request_body["created_by"] = created_by
        if group_id:
            request_body["group_id"] = group_id

        response = requests.put(f"{self.base_url}/api/v0/log-dialogue", json=request_body)
        if response.status_code != 200:
            print(f"HTTP error! Status: {response.status_code}")

        return id

    def create_feedback(self, content_id, key, score, comment=None, user=None):
        print(f"Feedback for content ID {content_id}:")
        print(f"Key: {key}")
        print(f"Score: {score}")
        if comment:
            print(f"Comment: {comment}")
        if user:
            print(f"User: {user}")

        feedback_body = {
            "project_id": self.project_id,
            "content_id": content_id,
            "key": key,
            "score": score
        }

        if comment:
            feedback_body["comment"] = comment
        if user:
            feedback_body["user"] = user

        response = requests.put(f"{self.base_url}/api/v0/create-feedback", json=feedback_body)
        if response.status_code != 200:
            print(f"HTTP error! Status: {response.status_code}")

