import boto3
import urllib.parse

def lambda_handler(event, context):
    # Get input file from S3 Bucket
    print("Event received:", event)
    try:
        input_bucket = event['Records'][0]['s3']['bucket']['name']
        input_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
        print(f"Fetching s3://{input_bucket}/{input_key}")

        # Read input file from S3
        s3_client = boto3.client('s3')
        response = s3_client.get_object(Bucket=input_bucket, Key=input_key)

        input_data = response['Body'].read().decode('utf-8')

        # For each line, treat it as a word and batch insert into DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('english-words')

        words = [word for word in input_data.splitlines() if word.strip()]
        print(f"Inserting {len(words)} words into DynamoDB.")
        with table.batch_writer() as batch:
            for word in words:
                batch.put_item(Item={'word': word})

        return {
            'statusCode': 200,
            'body': f'Successfully processed {len(words)} words from {input_key} and inserted into DynamoDB.'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error processing file: {str(e)}'
        }