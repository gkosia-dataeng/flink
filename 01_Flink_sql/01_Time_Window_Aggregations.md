Window Aggregations

Additional to the simple aggragations we can do on the incoming data Flink provides the future of Window aggregations.
A Window is a logical grouping of rows based on a time attribute.

Tubling window: Aggreagates the data by a fix non overlaping window size (every 10 minutes  [0-10, 10-20,20-30])
                
                Fixed window size
                Non overlaping windows
                Each message falls into one only window

                Usecase example: Perform aggragations over fixed period 

                -- window size
                SELECT * FROM TABLE( TUMBLE(TABLE orders, DESCRIPTOR(order_time), INTERVAL '10' MINUTES));

Hopping (sql) /Sliding(table, datastream) window: The window boundaries is [t - 10, t), [t - 5,  t) (t is the time of event)
                Window is sliding every time an event is coming

                Fixed window size
                Overlaping windows
                Each message can fall into multiple windows


                Usecase example: Calculating Movig Averages

                
                -- slide time, window size
                SELECT * FROM TABLE(HOP(TABLE orders, DESCRIPTOR(order_time), INTERVAL '5' MINUTES, INTERVAL '10' MINUTES));

Session window: The window group the events based on the gab between them 
                A new window opens every time we have a specific period gap (no events)
                
                Usecase: user web app session
               -- session gab
               SELECT * FROM TABLE(SESSION(TABLE orders , DESCRIPTOR(order_time), INTERVAL '2' MINUTES))



Cumulative window: Aggregates the cummulative amount until final length, emit a message every time you slide (0-2 => 3, 2-4 => 7, 4-6=> 9...8-10 =>13)
                   only the end boundary moves until the end
                
                -- slide, final length
                SELECT * FROM TABLE(CUMULATE(TABLE orders, DESCRIPTOR(order_time), INTERVAL '2' MINUTES, INTERVAL '10' MINUTES));


Pattern recognition: ???