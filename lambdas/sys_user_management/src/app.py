import boto3
import json
import string
import random

from aws_lambda_powertools import Logger
from sosw.app import Processor as SoswProcessor, get_lambda_handler, LambdaGlobals

logger = Logger()


class Processor(SoswProcessor):
    DEFAULT_CONFIG = {
        'init_clients':                ['iam', 'lambda'],
        'cleanup_exclude_list_lambda': [],
        'cleanup_exclude_list_role':   ['AWSServiceRoleForComputeOptimizer ',
                                        'AWSServiceRoleForOrganizations',
                                        'AWSServiceRoleForSupport',
                                        'AWSServiceRoleForTrustedAdvisor',
                                        'OrganizationAccountAccessRole'],
    }

    iam_client: boto3.client = None
    lambda_client: boto3.client = None


    def get_config(self, name):
        pass


    def __call__(self, event):

        logger.info("Called the Processor")

        trigger = event.get('action', [])

        match trigger:
            case ['create']:
                self.sys_user_management(event)
                logger.info('Creating users')

            case ['delete']:
                self.sys_user_management_cleanup()
                logger.info('Initialize deletion of users, roles, lambdas and policies.')

            case _:
                logger.info('Action is not supported')


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


    def sys_user_management_cleanup(self):

        self.delete_users_and_groups()
        self.delete_customer_managed_policies()

        regions = [region['RegionName'] for region in self.iam_client.describe_regions()['Regions']]
        for region in regions:
            self.delete_all_lambda_functions(region)

        self.delete_iam_roles()


    def delete_all_lambda_functions(self, region):
        self.lambda_client = boto3.client('lambda', MasterRegion=region)
        response = self.lambda_client.list_functions()

        for function in response['Functions']:
            function_name = function['FunctionName']
            if function_name not in self.config['cleanup_exclude_list_lambda']:
                self.lambda_client.delete_function(FunctionName=function_name)
                logger.info('deleted lambda function', function_name)

                self.stats['lambdas_deleted'] += 1
                self.stats['lambdas_deleted'].append(function_name)


    def delete_users_and_groups(self):

        response = self.iam_client.list_users()
        users = response['Users']

        for user in users:
            username = user['UserName']
            user_groups = self.iam_client.list_groups(UserName=users['UserName'])

            for group in user_groups:
                self.iam_client.delete_group(GroupName=group)
                self.stats['groups_deleted'] += 1
                self.stats['groups_deleted'].append(group)

            self.iam_client.delete_user(UserName=username)
            self.iam_client.delete_login_profile(UserName=username)
            logger.info('Removed user:', username)
            self.stats['users_deleted'] += 1
            self.stats['users_deleted'].append(username)


    def delete_customer_managed_policies(self):

        response = self.iam_client.list_policies(Scope='Local')
        policies_to_die = response['PolicyName']

        for policy in policies_to_die:
            self.iam_client.delete_policy(PolicyName=policy)
            logger.info("Deleted policy:", policy)
            self.stats['policies_deleted'] += 1
            self.stats['policies_deleted'].append(policy)


    def delete_iam_roles(self):

        response = self.iam_client.list_roles()
        roles_to_die = response['Roles']

        for role in roles_to_die:
            role_name = role['RoleName']

            if role_name != self.config['cleanup_exclude_list_role']:
                self.iam_client.delete_role(RoleName=role_name)
                logger.info('Role successfully deleted:', role_name)
                self.stats['roles_deleted'] += 1
                self.stats['roles_deleted'].append(role_name)
            else:
                logger.info('Role is in exclude list:', role_name)


    def generate_random_password(self, length: int = 8):

        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for _ in range(length))


global_vars = LambdaGlobals()
lambda_handler = get_lambda_handler(Processor, global_vars)
