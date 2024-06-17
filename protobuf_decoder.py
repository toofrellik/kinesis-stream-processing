# protobuf_decoder.py
import json
from google.protobuf.json_format import ParseDict, ParseError
from google.protobuf.timestamp_pb2 import Timestamp
import schema_pb2
import prometheus_metrics as pm

def process_json_records(records, unique_players, unique_logins_by_country, find_unique_records):
    for record in records:
        data = record['Data'].decode('utf-8')
        json_data = json.loads(data)
        # Count total records read
        pm.total_records_read_counter.inc()

        # Check for unique records
        if not find_unique_records(json_data):
            continue
        pm.total_unique_records_counter.inc()

        # Determine if it's LoginMessageV2 by checking for the 'country' field
        if 'country' in json_data:
            # Map to LoginMessageV2
            message = schema_pb2.LoginMessageV2()
            event_type = "LoginMessageV2"
            pm.records_with_LoginMessageV2_counter.inc()
        else:
            # Map to LoginMessageV1
            message = schema_pb2.LoginMessageV1()
            event_type = "LoginMessageV1"
            pm.records_with_LoginMessageV1_counter.inc()

        # Convert the timestamp from string to protobuf timestamp
        timestamp_str = json_data.pop('timestamp')
        timestamp = Timestamp()
        timestamp.FromJsonString(timestamp_str)
        
        # Assign timestamp directly to the message
        message.timestamp.CopyFrom(timestamp)
        
        # Parse remaining JSON fields
        try:
            ParseDict(json_data, message)
            pm.records_successfully_parsed.inc()
        except ParseError as e:
            print(f"Failed to parse JSON to {event_type}: {e}")
            pm.records_failed_to_parse.inc()
            continue

        # Extract player_id and country
        player_id = message.player_id
        country = getattr(message, 'country', None)  # Use getattr for optional fields
        
        # Update unique player logins
        unique_players.add(player_id)
        pm.unique_player_logins_gauge.set(len(unique_players))
        
        # Update unique player logins by country
        if country:
            if country not in unique_logins_by_country:
                unique_logins_by_country[country] = set()
            unique_logins_by_country[country].add(player_id)
            pm.unique_player_logins_by_country_gauge.labels(country=country).set(len(unique_logins_by_country[country]))
