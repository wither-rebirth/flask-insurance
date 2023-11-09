DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS person;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE person (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    person_name TEXT NOT NULL,
    person_phone INTEGER NOT NULL,
    person_rephone INTEGER,
    person_email TEXT,
    person_gender TEXT ,
    person_birth DATE ,
    person_idcard INTEGER ,
    company_name TEXT ,
    FOREIGN KEY (person_id) REFERENCES user (id)
);

CREATE TABLE service (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    service_date DATETIME NOT NULL,
    service_reason TEXT NOT NULL,
    treatment TEXT NOT NULL,
    service_description TEXT NOT NULL,
    service_hospital TEXT, 
    crime_id INTEGER ,
    insurance_id INTEGER NOT NULL,
    case_progress TEXT ,
    case_status TEXT ,
    FOREIGN KEY (service_id) REFERENCES person (id)
)