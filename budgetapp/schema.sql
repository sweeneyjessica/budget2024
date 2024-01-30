DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS debit;
DROP TABLE IF EXISTS credit;
DROP TABLE IF EXISTS transaction_quarantine;
DROP TABLE IF EXISTS merchant_to_category;
DROP TABLE IF EXISTS travel;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE debit (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  transaction_date DATE NOT NULL,
  card_no INTEGER NOT NULL,
  descr TEXT NOT NULL,
  amount REAL NOT NULL,
  category TEXT,
  information TEXT,
  tags TEXT,
  FOREIGN KEY (user_id) REFERENCES user (id),
  FOREIGN KEY (descr) REFERENCES merchant_to_category (merchant)
);

CREATE TABLE credit (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  transaction_date DATE NOT NULL,
  card_no INTEGER NOT NULL,
  descr TEXT NOT NULL,
  amount REAL NOT NULL,
  category TEXT,
  information TEXT,
  tags TEXT,
  FOREIGN KEY (user_id) REFERENCES user (id),
  FOREIGN KEY (descr) REFERENCES merchant_to_category (merchant)
);

CREATE TABLE transaction_quarantine (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  transaction_date DATE,
  card_no INTEGER,
  descr TEXT,
  amount REAL,
  category TEXT,
  information TEXT,
  tags TEXT
);

CREATE TABLE merchant_to_category (
  merchant TEXT PRIMARY KEY NOT NULL,
  category TEXT NOT NULL,
  information TEXT,
  tags TEXT
);

CREATE TABLE travel (
  day_of DATE NOT NULL,
  user_id INTEGER NOT NULL,
  is_travel_day BOOLEAN NOT NULL DEFAULT FALSE,
  FOREIGN KEY (user_id) REFERENCES user (id)
);