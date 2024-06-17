# checkpoint_and_buffer.py
import os

# Checkpoint file path
checkpoint_file = 'kinesis_checkpoint.txt'

# Buffer for records
record_buffer = []
buffer_size = 100

# Processed records set
processed_records = set()

# Function to read the last checkpoint
def read_checkpoint():
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            return f.read().strip()
    return None

# Function to write the checkpoint
def write_checkpoint(sequence_number):
    with open(checkpoint_file, 'w') as f:
        f.write(sequence_number)

# Function to flush and process the buffer
def flush_buffer(process_json_records, unique_players, unique_logins_by_country, find_unique_records):
    global record_buffer
    if record_buffer:
        process_json_records(record_buffer, unique_players, unique_logins_by_country, find_unique_records)
        record_buffer = []

# Function to check and track unique records
def find_unique_records(json_data):
    global processed_records
    # Extract player_id and timestamp early
    player_id = json_data.get('playerId')
    timestamp_str = json_data.get('timestamp')

    # Skip if player_id or timestamp is missing
    if not player_id or not timestamp_str:
        return False

    # Check for duplicates
    record_key = (player_id, timestamp_str)
    if record_key in processed_records:
        return False  # Skip processing if already processed

    # Add to processed records
    processed_records.add(record_key)

    # Clear processed records if it reaches 1000 count
    if len(processed_records) > 1000:
        processed_records.clear()

    return True
