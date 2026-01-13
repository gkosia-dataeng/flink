# Joins in Flink SQL

## Streaming joins with bounded characteristics (safe)

### Interval (window) joins
- Messages are dropped from state after:
  `window_end + allowed_lateness`

Example:

    SELECT *
    FROM A
    JOIN B
    ON A.id = B.id
    AND A.rowtime BETWEEN B.rowtime - INTERVAL '5' MINUTE
                      AND B.rowtime + INTERVAL '5' MINUTE

---

### Temporal joins

**Fact table**
- Minimal buffering

**Dimension table**
- Versioned
- Old versions removed based on:
  - Watermark progress
  - Retention configuration

Example:

    SELECT *
    FROM fact_stream f
    JOIN dim_table FOR SYSTEM_TIME AS OF f.rowtime d
    ON f.id = d.id

---

### Joins with State TTL
- Each record lives up to the configured TTL
- Prevents unbounded state growth

Configuration example:

    table.exec.state.ttl: 1 h

---

## Unbounded streaming joins (dangerous)

### Streaming joins without windows or TTL
- State grows indefinitely
- Applies to:
  - INNER JOIN
  - LEFT JOIN
  - RIGHT JOIN
  - FULL JOIN

⚠️ Strongly discouraged in streaming jobs
