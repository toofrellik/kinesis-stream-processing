# Kinesis Stream Processing with Prometheus Metrics

This project provides a system for reading, processing, and monitoring AWS Kinesis stream data using Protobuf and Prometheus.

## Architecture and Design

### Overview

The system processes data from an AWS Kinesis stream and provides real-time metrics using Prometheus. The architecture comprises the following components:

1. **Kinesis Client**: Reads records from an AWS Kinesis stream.
2. **Protobuf Decoder**: Decodes and processes Protobuf-encoded messages.
3. **Prometheus Server**: Exposes metrics on an HTTP endpoint for Prometheus scraping.
4. **Checkpointing and Buffering**: Manages checkpointing and buffering to ensure efficient data processing and resumption.

### Components

### 1. **Kinesis Client**
   - Reads data from a specified Kinesis stream.
   - Configured using AWS credentials.
   - Reads from a particular shard of the Kinesis stream, which allows for scaling by adding more consumers based on the number of shards.
   - Can be managed by a cluster manager to distribute the load across multiple shards and consumers.

### 2. **Protobuf Decoder**
   - Decodes messages using Protobuf schemas (`LoginMessageV1` and `LoginMessageV2`).
   - Counts unique player logins.
   - Handles decoding, parsing errors, and differentiates message formats.

### 3. **Prometheus Server**
   - Exposes metrics such as total records read, unique records, records by format type, and failed records.
   - Runs on a configurable port and can be stopped gracefully.
   - Metrics are accessible at `http://localhost:<port>/metrics` and can be scraped by Prometheus for monitoring.
   - Metrics can be visualized in a Grafana dashboard.
   - (Future scope) Node exporter metrics can be integrated to monitor the health of the system on which the consumers are running.

### 4. **Checkpointing and Buffering**
   - Manages buffering of records to enhance processing efficiency.
   - Uses checkpointing to ensure the application can resume processing from the last processed record.
   - Buffers 100 records by default (configurable based on the infrastructure).
   - Uses `processed_records` to track and deduplicate records. Future improvements could integrate stateful databases like RocksDB for enhanced state management.


### Data Flow

1. The application reads data from a Kinesis stream using the `Kinesis Client`.
2. Raw data is decoded and processed using the `Protobuf Decoder`.
3. Metrics are updated and exposed through the `Prometheus Server`.
4. Processed records are checkpointed and buffered using the `Checkpointing and Buffering` component.


## Prerequisites

- Python 3.8 or higher
- AWS credentials with access to Kinesis
- Prometheus setup to scrape metrics

1. **Create a virtual environment** (recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  
    ```

2. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

3. **Compile the Protobuf Schema**:

    Ensure you have the Protobuf compiler (`protoc`) installed. 

    Compile the Protobuf schema (`schema.proto`) to generate `schema_pb2.py`, (This step is completed and `schema_pb2.py` is provided)

    ```bash
    protoc --python_out=. schema.proto
    ```

4. **Ensure env variables are available**:
    `aws_access_key_id`
    `aws_secret_access_key`


## USAGE:
python run.py


## Project Structure

kinesis-stream-processing/
│
├── config.py # Configuration file for AWS credentials and settings
├── requirements.txt # Python dependencies
├── README.md # Documentation file
├── run.py # Main script to run the application
├── prometheus_metrics.py # Prometheus metrics server and definitions
├── protobuf_decoder.py # Protobuf message decoder and processor
└── checkpoint_and_buffer.py # Checkpointing, buffering, and deduplication logic
└── schema_pb2.py # Generated Protobuf classes (compiled from schema.proto file)


## Debugging:

incase if you face: Port Address already in use 
please kill the process running in port 8090
```lsof -i tcp:8089  
```
use PID from above command and run below
```
kill -9 <PID>
```


## Future scope:
Addition of proper logging
CICD with EKS or github actions or jenkins
Central repo for all the transformations and metrics where our processing engine can read through and output the data.