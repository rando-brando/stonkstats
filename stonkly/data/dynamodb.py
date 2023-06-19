import boto3
import os


class DynamoDB:
    def __init__(self):
        self.resource = boto3.resource(
            'dynamodb',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        self.available_symbols = self.resource.Table('available_symbols')

    def put_items(table, )
    with table.batch_writer() as batch:
        for _ in range(1000000):
            batch.put_item(Item={'HashKey': '...', 'Otherstuff': '...'})
