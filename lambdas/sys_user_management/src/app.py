import boto3
import json
import string
import random

from aws_lambda_powertools import Logger
from sosw.app import Processor as SoswProcessor, get_lambda_handler, LambdaGlobals

logger = Logger()


class Processor(SoswProcessor):
    DEFAULT_CONFIG = {
        'init_clients': ['iam'],
    }

    iam_client: boto3.client = None


    def get_config(self, name):
        pass


    def __call__(self, event):

        logger.info("Called the Processor")
        self.sys_user_management(event)


    def sys_user_management(self, event):

        names = event.get('names', [])

        users = {}

        for name in names:
            password = self.generate_random_password()

            self.iam_client.create_user(UserName=name)
            self.iam_client.create_login_profile(UserName=name, Password=password, PasswordResetRequired=False)
            self.iam_client.attach_user_policy(UserName=name, PolicyArn='arn:aws:iam::aws:policy/AdministratorAccess')
            users[name] = password

        logger.info(f"Created users: {json.dumps(users)}")
        return users


    def generate_random_password(self, length: int = 8):
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for _ in range(length))


global_vars = LambdaGlobals()
lambda_handler = get_lambda_handler(Processor, global_vars)
