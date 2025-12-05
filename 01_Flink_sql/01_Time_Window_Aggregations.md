Window Aggregations

Additional to the simple aggragations we can do on the incoming data Flink provides the future of Window aggregations.
A Window is a logical grouping of rows based on a time attribute.

Tubling window: Aggreagates the data by a fix non overlaping window size (every 10 minutes  [0-10, 10-20,20-30])

                -- window size
                SELECT * FROM TABLE( TUMBLE(TABLE orders, DESCRIPTOR(order_time), INTERVAL '10' MINUTES));

Hopping window: Aggreagates the data by a fix window size which is hopping N time (every 10 mins slide 5 mins [0-10, 5-15, 10-20, 15-25])
                Boundaries of windows are based on clock time even if no data arrives
                fixed overlapping windows at clock intervals
                Usecase: time buckets

                -- hop size, window size
                SELECT * FROM TABLE(HOP(TABLE orders, DESCRIPTOR(order_time), INTERVAL '5' MINUTES, INTERVAL '10' MINUTES));

Sliding window: The window boundaries is [t - 10, t), [t - 5,  t) (t is the time of event)
                Window is sliding every time an event is coming
                Usecase: Rolling/Continues KPIs

                
                -- slide time, window size
                SELECT * FROM TABLE(SLIDE(TABLE events, DESCRIPTOR(ts), INTERVAL '5' MINUTE, INTERVAL '10' MINUTE))

Cumulative window: Aggregates the cummulative amount until final length, emit a message every time you slide (0-2 => 3, 2-4 => 7, 4-6=> 9...8-10 =>13)
                   only the end boundary moves until the end
                
                -- slide, final length
                SELECT * FROM TABLE(CUMULATE(TABLE orders, DESCRIPTOR(order_time), INTERVAL '2' MINUTES, INTERVAL '10' MINUTES));


Pattern recognition: ???