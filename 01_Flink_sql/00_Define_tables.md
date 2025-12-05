## Flink Tables and Catalogs

When defining tables in Flink, **metadata** must be stored so that the Flink job can understand the structure of the data.  

For example, when defining a **source table** from a Kafka topic:  
- The **message structure** is mapped to table columns and their corresponding data types.  
- You also need to define **source properties** such as the Kafka broker addresses, topic name, and message format (e.g., JSON, Avro, or CSV).

Flink stores this metadata in a **Catalog**, which is similar to a database:  
- Each **Catalog** can contain one or more **databases**.  
- Each **database** can contain one or more **tables**.  

By default, a Catalog exists **only for the current session**.  
To share the catalog across multiple jobs or sessions, you need to configure an **external catalog** (e.g., HiveCatalog, JDBC catalog, or other persistent catalog implementations).