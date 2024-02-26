DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS debit;
DROP TABLE IF EXISTS credit;
DROP TABLE IF EXISTS transaction_quarantine;
DROP TABLE IF EXISTS merchants;
DROP TABLE IF EXISTS travel;
DROP TABLE IF EXISTS budget;
DROP TABLE IF EXISTS merchants_quarantine;
DROP TABLE IF EXISTS weekly_quarters;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  misc_threshold REAL DEFAULT 20.0
);

CREATE TABLE debit (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  transaction_date DATE NOT NULL,
  card_no INTEGER NOT NULL,
  descr TEXT NOT NULL,
  parsed_descr TEXT NOT NULL,
  amount REAL NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user (id),
  FOREIGN KEY (descr) REFERENCES merchants (merchant)
);

CREATE TABLE credit (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  transaction_date DATE NOT NULL,
  card_no INTEGER NOT NULL,
  descr TEXT NOT NULL,
  parsed_descr TEXT NOT NULL,
  amount REAL NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE transaction_quarantine (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  transaction_date DATE,
  card_no INTEGER,
  descr TEXT,
  parsed_descr TEXT,
  amount REAL
);

CREATE TABLE merchants (
  merchant TEXT PRIMARY KEY NOT NULL,
  category TEXT NOT NULL,
  information TEXT,
  tags TEXT,
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE merchants_quarantine (
  merchant TEXT,
  category TEXT,
  information TEXT,
  tags TEXT,
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE travel (
  day_of DATE NOT NULL,
  user_id INTEGER NOT NULL,
  is_travel_day BOOLEAN NOT NULL DEFAULT FALSE,
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES user (id),
  PRIMARY KEY (day_of, user_id)
);

CREATE TABLE budget (
    category TEXT PRIMARY KEY NOT NULL,
    dollar_limit REAL NOT NULL,
    time_period TEXT DEFAULT 'Monthly'
);

CREATE TABLE weekly_quarters (
    day_of_month INTEGER,
    quarter INTEGER
);

INSERT INTO weekly_quarters VALUES (1, 1);
INSERT INTO weekly_quarters VALUES (2, 1);
INSERT INTO weekly_quarters VALUES (3, 1);
INSERT INTO weekly_quarters VALUES (4, 1);
INSERT INTO weekly_quarters VALUES (5, 1);
INSERT INTO weekly_quarters VALUES (6, 1);
INSERT INTO weekly_quarters VALUES (7, 1);
INSERT INTO weekly_quarters VALUES (8, 1);
INSERT INTO weekly_quarters VALUES (9, 2);
INSERT INTO weekly_quarters VALUES (10, 2);
INSERT INTO weekly_quarters VALUES (11, 2);
INSERT INTO weekly_quarters VALUES (12, 2);
INSERT INTO weekly_quarters VALUES (13, 2);
INSERT INTO weekly_quarters VALUES (14, 2);
INSERT INTO weekly_quarters VALUES (15, 2);
INSERT INTO weekly_quarters VALUES (16, 2);
INSERT INTO weekly_quarters VALUES (17, 3);
INSERT INTO weekly_quarters VALUES (18, 3);
INSERT INTO weekly_quarters VALUES (19, 3);
INSERT INTO weekly_quarters VALUES (20, 3);
INSERT INTO weekly_quarters VALUES (21, 3);
INSERT INTO weekly_quarters VALUES (22, 3);
INSERT INTO weekly_quarters VALUES (23, 3);
INSERT INTO weekly_quarters VALUES (24, 4);
INSERT INTO weekly_quarters VALUES (25, 4);
INSERT INTO weekly_quarters VALUES (26, 4);
INSERT INTO weekly_quarters VALUES (27, 4);
INSERT INTO weekly_quarters VALUES (28, 4);
INSERT INTO weekly_quarters VALUES (29, 4);
INSERT INTO weekly_quarters VALUES (30, 4);
INSERT INTO weekly_quarters VALUES (31, 4);


