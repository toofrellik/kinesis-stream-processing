import os

app_config={
'aws_access_key_id' : os.environ.get('aws_access_key_id'),
'aws_secret_access_key' : os.environ.get('aws_secret_access_key'),
'stream_name' : 'sc-kinesis-test-stream',
'port' : 8089}