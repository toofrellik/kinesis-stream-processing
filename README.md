# kinesis-stream-processing

# Kinesis Stream Processing with Prometheus Metrics

This project reads from an AWS Kinesis stream, processes Protobuf messages, and exposes metrics via Prometheus.

## Prerequisites

- Python 3.8 or higher
- AWS credentials with access to Kinesis
- Prometheus setup to scrape metrics

## Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/toofrellik/kinesis-stream-processing.git
    cd kinesis-stream-processing
    ```

2. **Create a virtual environment** (recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

USAGE:

python run.py
