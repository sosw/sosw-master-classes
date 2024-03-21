import boto3
import json
import string
import random

from aws_lambda_powertools import Logger
from pwgen import pwgen
from sosw.app import Processor as SoswProcessor, get_lambda_handler, LambdaGlobals

logger = Logger()


class Processor(SoswProcessor):
    DEFAULT_CONFIG = {
        'init_clients':                ['iam', 'lambda'],
        'cleanup_exclude_list_lambda': ['sys_user_management'],
        'cleanup_exclude_list_role':   ['AWSServiceRoleForComputeOptimizer',
                                        'AWSServiceRoleForComputeOptimizer',
                                        'AWSServiceRoleForOrganizations',
                                        'AWSServiceRoleForSupport',
                                        'AWSServiceRoleForTrustedAdvisor',
                                        'OrganizationAccountAccessRole'],
        'cleanup_exclude_users':       ['ngr'],
    }

    iam_client: boto3.client = None
    lambda_client: boto3.client = None


    def get_config(self, name):
        pass


    def __call__(self, event):

        logger.info("Called the Processor")

        trigger = event.get('action', '')

        match trigger:
            case 'create':
                logger.info('Creating users')
                return self.sys_user_management_create_users(event)

            case 'delete':
                logger.info('Initializing deletion of users, roles, lambdas and policies.')
                self.sys_user_management_cleanup()

            case _:
                logger.info('Action is not supported')


    def sys_user_management_create_users(self, event):

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


    def sys_user_management_cleanup(self):

        for obj_name in ['user', 'group']:
            self.delete_listed_objects(obj_name)

        self.delete_customer_managed_policies()

        regions = [region['RegionName'] for region in self.iam_client.describe_regions()['Regions']]
        for region in regions:
            self.delete_all_lambda_functions(region)

        self.delete_listed_objects('role')


    def delete_all_lambda_functions(self, region: str = "us-west-2"):
        self.lambda_client = boto3.client('lambda', MasterRegion=region)
        response = self.lambda_client.list_functions()

        for function in response['Functions']:
            function_name = function['FunctionName']
            if function_name not in self.config['cleanup_exclude_list_lambda']:
                self.lambda_client.delete_function(FunctionName=function_name)
                logger.info('Deleted lambda function: %s', function_name)
                self.stats['lambdas_deleted'] += 1


    def delete_listed_objects(self, obj_type):
        list_method = getattr(self.iam_client, f'list_{obj_type}s')
        del_method = getattr(self.iam_client, f'delete_{obj_type}')

        response = list_method()

        for obj in response.get(f"{obj_type.title()}s", []):
            name = obj[f"{obj_type.title()}Name"]

            if name in self.config.get(f'cleanup_exclude_{obj_type}s', []):
                logger.info("Skipping excluded %s: %s", obj_type, name)
                continue

            logger.info("Deleting %s: %s", obj_type, name)
            del_method(**{f"{obj_type.title()}Name": name})
            self.stats[f'{obj_type}s_deleted'] += 1


    def delete_customer_managed_policies(self):

        response = self.iam_client.list_policies(Scope='Local')
        policies_to_die = [x['PolicyName'] for x in response['Policies']]

        for policy in policies_to_die:
            self.iam_client.delete_policy(PolicyName=policy)
            logger.info("Deleted policy: %s", policy)
            self.stats['policies_deleted'] += 1


    def generate_random_password(self, length: int = 8):
        return pwgen(length, symbols=True)


global_vars = LambdaGlobals()
lambda_handler = get_lambda_handler(Processor, global_vars)
