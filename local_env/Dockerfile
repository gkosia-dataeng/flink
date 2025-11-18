FROM flink:1.20.0-scala_2.12-java11

RUN apt-get update -y && \
apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev liblzma-dev libffi-dev && \
wget https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tgz && \
tar -xvf Python-3.11.0.tgz && \
cd Python-3.11.0 && \
./configure --without-tests --enable-shared && \
make -j6 && \
make install && \
ldconfig /usr/local/lib && \
cd .. && rm -f Python-3.11.0.tgz && rm -rf Python-3.11.0 && \
ln -s /usr/local/bin/python3 /usr/local/bin/python && \
apt-get clean && \
rm -rf /var/lib/apt/lists/*


RUN wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-connector-kafka/3.4.0-1.20/flink-connector-kafka-3.4.0-1.20.jar; \
    wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/kafka/kafka-clients/3.4.0/kafka-clients-3.4.0.jar; \
    wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-python/1.20.0/flink-python-1.20.0.jar; 
    
RUN chown -R flink:flink /opt/flink/lib

COPY ./requirements.txt .


ENV FLINK_APP_RUNTIME_ENV="DOCKER"
# install PyFlink
RUN pip3 install -r requirements.txt