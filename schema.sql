CREATE TABLE entries (
    id          SERIAL PRIMARY KEY,
    user_id     BIGINT NOT NULL,
    entry_date  DATE DEFAULT CURRENT_DATE,
    mood        INTEGER NOT NULL,
    work_hours  NUMERIC(4,1) NOT NULL,
    sleep_hours NUMERIC(4,1) NOT NULL,
    comment     TEXT,
    created_at  TIMESTAMP DEFAULT NOW()
);