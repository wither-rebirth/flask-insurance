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
    person_gender TEXT NOT NULL,
    person_birth DATE NOT NULL,
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
    crime_id INTEGER NOT NULL,
    insurance_id INTEGER NOT NULL,
    FOREIGN KEY (service_id) REFERENCES person (id)
)
