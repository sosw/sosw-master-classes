import json
import logging


def lambda_handler(event, context):
    logging.info("Don't expect me to do your job")

    return {
        'statusCode': 403,
        'body':       json.dumps({"message": "It is forbidden to steal other people's code!"}),
        'headers':    {
            'Content-type': 'application/json'
        },
    }
