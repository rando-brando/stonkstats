import boto3
import os


class DynamoDB:
    def __init__(self):
        self.resource = boto3.resource('dynamodb')
        self.available_symbols = self.resource.Table('available_symbols')

    #def put_items(table, )
    #with table.batch_writer() as batch:
    #    for _ in range(1000000):
    #        batch.put_item(Item={'HashKey': '...', 'Otherstuff': '...'})
