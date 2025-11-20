


INSERT INTO SQL_LAB.customer_sum
SELECT cust_id, sum(amount)
from SQL_LAB.transactions
group by cust_id;