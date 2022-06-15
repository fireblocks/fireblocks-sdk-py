"""
This is a demo runner to experience with all the SDK functions from the CLI
In order to use it, please install "inquirer" that is not included as a requirement

pip3 install inquirer

Before running the file, make sure you set API_SERVER_ADDRESS, PRIVATE_KEY_PATH and USER_ID
to the correct values corresponding the environment you are working with.
"""

import inspect
import json
import os
from typing import Dict, List

import inquirer
from inquirer.themes import GreenPassion

from fireblocks_sdk import FireblocksSDK

API_SERVER_ADDRESS = os.getenv('API_SERVER_ADDRESS', 'https://api.fireblocks.io')
PRIVATE_KEY_PATH = os.getenv('PRIVATE_KEY_PATH', '')
USER_ID = os.getenv('USER_ID', '')

class DemoRunner:
    def __init__(self, api_server: str, key_path: str, user_id: str) -> None:
        private_key = open(key_path, 'r').read()
        self.client = FireblocksSDK(private_key, user_id, api_server)
        self.client_methods = self._get_client_methods()

    def run(self):
        while True:
            action_question = [
                inquirer.List('action',
                              message="What would you like to do?",
                              choices=self.client_methods.keys()),
            ]

            action_answer = inquirer.prompt(action_question, theme=GreenPassion())
            requested_action = str(action_answer['action'])
            print(f'needed params: {self.client_methods[requested_action]}')

            params_questions = []
            for param in self.client_methods[requested_action]:
                params_questions.append(inquirer.Text(f'{param}', f'{param}'))

            entered_params = []
            if params_questions:
                entered_params = inquirer.prompt(params_questions, theme=GreenPassion())
                for k, v in entered_params.items():
                    if v == '':
                        entered_params[k] = None

            print(f'entered_params: {entered_params}')

            service, method = requested_action.split('::')

            if entered_params:
                return_value = getattr(getattr(self.client, service), method)(
                    *entered_params.values() if entered_params else None)
            else:
                return_value = getattr(getattr(self.client, service), method)()

            self.print_obj(return_value)
            continue

    def print_obj(self, obj):
        if isinstance(obj, list):
            for i in range(len(obj)):
                self.print_obj(obj[i])
        elif isinstance(obj, Dict):
            print(json.dumps(obj))
        elif isinstance(obj, object):
            print(obj.__dict__)

    def _get_client_methods(self) -> Dict[str, List[str]]:
        services = ['vault', 'exchange', 'contracts', 'wallets', 'gas_station', 'transfer_tickets', 'transactions',
                    'web_hooks']
        methods: Dict[str, List[str]] = {}
        for service in services:
            client_service = getattr(self.client, service)
            object_methods = [f'{service}::{method_name}' for method_name in dir(client_service)
                              if callable(getattr(client_service, method_name)) and not method_name.startswith('_')]

            for m in object_methods:
                service, method = m.split('::')
                method_instance = getattr(getattr(self.client, service), method)
                methods[m] = list(inspect.signature(method_instance).parameters.keys())

        return methods


if __name__ == '__main__':
    runner = DemoRunner(API_SERVER_ADDRESS, PRIVATE_KEY_PATH, USER_ID)
    runner.run()
