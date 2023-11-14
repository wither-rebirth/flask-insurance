DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS person;

CREATE TABLE user (
    id INTEGER PRIMARY KEY ,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);


-- 这里的user_id 映射的是user 表的id
-- 意味着user_id 为1时,对应的是user表id为1的用户填写的个人信息,当存在多个user_id=1的时候,意味着ID为1的人填写了多个个人信息,即多个服务


CREATE TABLE person (
    id INTEGER PRIMARY KEY,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER,
    person_name TEXT,
    person_phone INTEGER,
    person_rephone INTEGER,
    person_email TEXT,
    person_gender TEXT,
    person_birth DATE,
    person_idcard INTEGER,
    company_name TEXT,
    crime_id TEXT UNIQUE,
    insurance_id TEXT UNIQUE,
    FOREIGN KEY (user_id) REFERENCES user (id)
);


-- 这里的service_id 映射的是person 表的ID,即存在多个service_id=1时,意味着person的id 为1的这个人进行了多次服务

CREATE TABLE service (
    id INTEGER PRIMARY KEY ,
    service_id INTEGER,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    service_insurance TEXT UNIQUE,
    service_date DATETIME,
    service_reason TEXT,
    treatment TEXT,
    service_description TEXT,
    service_hospital TEXT, 
    case_progress TEXT,
    case_status TEXT,
    image_path_whole TEXT,
    image_path_part TEXT,
    image_path_accident TEXT,
    FOREIGN KEY (service_id) REFERENCES person (id)
)