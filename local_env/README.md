# Local Flink + Kafka Environment

This repository provides a fully containerized local environment that deploys a **Kafka cluster** and a **Flink cluster** using Docker.  
It is ideal for **practicing**, **developing**, and **testing** Apache Flink jobs locally.

---

## 🚀 Getting Started

### 1. Start the Environment

Run the following command:

```bash
docker-compose up -d
```

## This will spin up:

- **Kafka Cluster**
- **Kafka Client**  
  - Automatically creates the topics:  
    - `json-customers`  
    - `json-transactions`
- **Flink Cluster**  
  - JobManager  
  - TaskManagers

---

## 📁 Mounted Flink Job Directories

The following directories are mounted into the Flink containers:

- `02_Flink_Table_api`
- `03_Flink_Datastream_api`

Any Flink job placed in these folders can be submitted to the running Flink cluster using the **Flink CLI**.


## Accessing and Submitting Jobs from the Flink JobManager

Run the following commands:

### 1. Enter the JobManager container
```bash
docker exec -it local_env_flinkjobmanager_1 /bin/bash
```

### 2. Locate the jobs
```bash
cd /home/jobs
```

### 3. Submit a job
```bash
flink run -py ./02_Flink_Table_api/flinkjob.py
```