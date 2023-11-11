DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS person;

CREATE TABLE user (
    id INTEGER PRIMARY KEY ,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE person (
    id INTEGER PRIMARY KEY,
    person_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    person_name TEXT NOT NULL,
    person_phone INTEGER NOT NULL,
    person_rephone INTEGER,
    person_email TEXT,
    person_gender TEXT ,
    person_birth DATE ,
    person_idcard INTEGER ,
    company_name TEXT,
    FOREIGN KEY (person_id) REFERENCES user (id)
);

CREATE TABLE service (
    id INTEGER PRIMARY KEY ,
    service_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    service_date DATETIME ,
    service_reason TEXT ,
    treatment TEXT ,
    service_description TEXT ,
    service_hospital TEXT, 
    crime_id INTEGER ,
    insurance_id INTEGER ,
    case_progress TEXT ,
    case_status TEXT ,
    image_path_whole TEXT,
    image_path_part TEXT,
    image_path_accident TEXT,
    FOREIGN KEY (service_id) REFERENCES person (id)
)