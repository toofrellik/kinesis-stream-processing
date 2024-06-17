# prometheus_metrics.py
from prometheus_client import start_http_server, Counter, Gauge

# Define Prometheus metrics
total_records_read_counter = Counter('kinesis_total_records_read', 'Total number of records read from Kinesis')
total_unique_records_counter = Counter('kinesis_total_unique_records', 'Total number of unique records after deduplication')
records_with_LoginMessageV2_counter = Counter('kinesis_records_with_LoginMessageV2', 'Number of records identified as LoginMessageV2')
records_with_LoginMessageV1_counter = Counter('kinesis_records_with_LoginMessageV1', 'Number of records identified as LoginMessageV1')
records_failed_to_parse = Counter('kinesis_records_failed_to_parse', 'Number of records failed to parse')
records_successfully_parsed = Counter('kinesis_records_successfully_parsed', 'Number of parsed successfully')
unique_player_logins_gauge = Gauge('kinesis_unique_player_logins', 'Number of unique player logins')
unique_player_logins_by_country_gauge = Gauge('kinesis_unique_player_logins_by_country', 'Number of unique player logins by country', ['country'])

def start_prometheus_server(port):
    start_http_server(port)

def print_metrics(unique_players, unique_logins_by_country):
    print(f"Total records read: {total_records_read_counter._value.get()}")
    print(f"Total unique records: {total_unique_records_counter._value.get()}")
    print(f"Records with LoginMessageV2: {records_with_LoginMessageV2_counter._value.get()}")
    print(f"Records with LoginMessageV1: {records_with_LoginMessageV1_counter._value.get()}")
    print(f"Records failed to parse: {records_failed_to_parse._value.get()}")
    print(f"Records successfully parsed: {records_successfully_parsed._value.get()}")
    print(f"Total unique player logins: {len(unique_players)}")
    print("Unique player logins by country:")
    for country, players in unique_logins_by_country.items():
        print(f"  {country}: {len(players)}")
