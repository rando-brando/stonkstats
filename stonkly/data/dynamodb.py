import boto3


class DynamoDB:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.prices = self.dynamodb.Table('prices')
        self.earnings = self.dynamodb.Table('earnings')
        self.estimates = self.dynamodb.Table('estimates')
