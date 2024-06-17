# run.py
import boto3
import time
import psutil
from datetime import datetime, timedelta
import config
import prometheus_metrics as pm
import protobuf_decoder as pd
import checkpoint_and_buffer as cb

# Set your AWS credentials
aws_access_key_id = config.app_config['aws_access_key_id']
aws_secret_access_key = config.app_config['aws_secret_access_key']

# Initialize a Kinesis client
client = boto3.client(
    'kinesis',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name='us-east-1'
)

# Specify the stream name and Prometheus server port
stream_name = config.app_config['stream_name']
port = config.app_config['port']

# Get all shards in the stream
response = client.describe_stream(StreamName=stream_name)
shards = response['StreamDescription']['Shards']

# Start Prometheus client on the specified port
pm.start_prometheus_server(port)

def kill_process_using_port(port):
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        try:
            for conn in proc.connections(kind='inet'):
                if conn.laddr.port == port:
                    print(f"Killing process {proc.info['pid']} ({proc.info['name']}) on port {port}")
                    proc.terminate()  # or proc.kill()
                    proc.wait()  # Wait for the process to terminate
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue


# Function to get the shard ID dynamically
def get_shard_id():
    shards = client.list_shards(StreamName=stream_name)['Shards']
    if not shards:
        raise Exception(f"No shards found for stream {stream_name}")
    # For simplicity, select the first shard
    return shards[0]['ShardId']

# Function to process a single shard
def process_shard(shard_id):
    # Get the last checkpoint
    last_checkpoint = cb.read_checkpoint()
    
    # Prepare parameters for get_shard_iterator
    iterator_args = {
        'StreamName': stream_name,
        'ShardId': shard_id,
        'ShardIteratorType': 'LATEST' if last_checkpoint is None else 'AFTER_SEQUENCE_NUMBER',
    }
    if last_checkpoint:
        iterator_args['StartingSequenceNumber'] = last_checkpoint

    # Get shard iterator for the current shard
    shard_iterator_response = client.get_shard_iterator(**iterator_args)
    shard_iterator = shard_iterator_response['ShardIterator']

    while True:
        # Get records using the shard iterator
        record_response = client.get_records(ShardIterator=shard_iterator, Limit=100)
        records = record_response['Records']
        
        # Buffer records
        cb.record_buffer.extend(records)
        
        # Process the buffer when it reaches the specified size
        if len(cb.record_buffer) >= cb.buffer_size:
            cb.flush_buffer(pd.process_json_records, unique_players, unique_logins_by_country, cb.find_unique_records)
        
        # Save the checkpoint
        if records:
            last_sequence_number = records[-1]['SequenceNumber']
            cb.write_checkpoint(last_sequence_number)
        
        # Update the shard iterator to the next position
        shard_iterator = record_response.get('NextShardIterator')
        
        # Pause to avoid rate limiting
        time.sleep(1)

        # Break if no more records
        if not records:
            break

# Initialize unique players and logins
unique_players = set()
unique_logins_by_country = {}

# Main loop to process shards continuously
try:
    last_print_time = datetime.now()
    shard_id = get_shard_id()
    print(f"Processing shard ID: {shard_id}")
    while True:
        process_shard(shard_id)
        
        # Print metrics every minute
        if datetime.now() - last_print_time >= timedelta(minutes=1):
            pm.print_metrics(unique_players, unique_logins_by_country)
            last_print_time = datetime.now()
        
        # Flush remaining records in buffer
        cb.flush_buffer(pd.process_json_records, unique_players, unique_logins_by_country, cb.find_unique_records)

except KeyboardInterrupt:
    print("\nStopping the stream processing...")
    cb.flush_buffer(pd.process_json_records, unique_players, unique_logins_by_country, cb.find_unique_records)
    pm.print_metrics(unique_players, unique_logins_by_country)
finally:
    kill_process_using_port(port)