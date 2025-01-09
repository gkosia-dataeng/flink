Download flink binaries to use flink cli commands:
            
    1. wget https://archive.apache.org/dist/flink/flink-1.19.0/flink-1.19.0-bin-scala_2.12.tgz
    2. tar xzf flink-1.19.0-bin-scala_2.12.tgz
    3. rm flink-1.19.0-bin-scala_2.12.tgz
    4. mv flink-1.19.0 flink-bins

Submit a flink job to cluster:
    ./flink-bins/bin/flink run -py ./flink-bins/examples/python/table/word_count.py





https://quix.io/blog/pyflink-deep-dive#what-is-pyflink