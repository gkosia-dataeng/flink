## Data Producer

`data_producer` is a Python script that generates messages to Kafka topics.  
The messages are stored in text files unde the folder `data` in the following format:

```
<topic>@{json message}
```

---

## 🚀 How to Run

### 1. Set up the Python environment

Create a virtual environment:

```bash
virtualenv myenv
```

Activate the virtual environment:

```bash
. myenv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

### 2. Run the script

Make sure your `local_env` environment (Kafka + Flink) is running.  
Then start producing messages:

```bash
python python_from_file_to_kafka.py --file simple_transactions
```

---

## ✅ Verify Produced Data

### 1. Enter the Kafka container

```bash
docker exec -it kafka /bin/bash
```

### 2. Start consuming messages from the console

```bash
kafka-console-consumer --bootstrap-server kafka:19092 --topic json-customers --from-beginning
```