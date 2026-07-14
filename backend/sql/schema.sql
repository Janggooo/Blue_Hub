-- BlueHub schema for Oracle Database
-- Run this connected as the app's schema user (e.g. bluehub_app).

CREATE TABLE organizations (
    organization_id   NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    organization_name VARCHAR2(150) NOT NULL,
    description        CLOB,
    category            VARCHAR2(100),
    contact_email       VARCHAR2(150),
    logo_url            VARCHAR2(500),
    created_at          TIMESTAMP DEFAULT SYSTIMESTAMP
);

CREATE TABLE users (
    user_id         NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name      VARCHAR2(100) NOT NULL,
    last_name       VARCHAR2(100) NOT NULL,
    email           VARCHAR2(150) NOT NULL UNIQUE,
    password_hash   VARCHAR2(255) NOT NULL,
    role            VARCHAR2(20) DEFAULT 'student' NOT NULL,
    organization_id NUMBER,
    created_at      TIMESTAMP DEFAULT SYSTIMESTAMP,
    CONSTRAINT chk_users_role CHECK (role IN ('student', 'officer', 'admin')),
    CONSTRAINT fk_users_org FOREIGN KEY (organization_id)
        REFERENCES organizations (organization_id) ON DELETE SET NULL
);

CREATE TABLE categories (
    category_id   NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_name VARCHAR2(100) NOT NULL UNIQUE
);

CREATE TABLE events (
    event_id        NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    organization_id NUMBER NOT NULL,
    title           VARCHAR2(200) NOT NULL,
    description     CLOB,
    venue           VARCHAR2(200),
    event_date      DATE NOT NULL,
    category        VARCHAR2(100),
    image_url       VARCHAR2(500),
    created_by      NUMBER,
    created_at      TIMESTAMP DEFAULT SYSTIMESTAMP,
    CONSTRAINT fk_events_org FOREIGN KEY (organization_id)
        REFERENCES organizations (organization_id) ON DELETE CASCADE,
    CONSTRAINT fk_events_creator FOREIGN KEY (created_by)
        REFERENCES users (user_id) ON DELETE SET NULL
);

CREATE INDEX idx_events_date ON events (event_date);
CREATE INDEX idx_events_org ON events (organization_id);
CREATE INDEX idx_events_category ON events (category);
CREATE INDEX idx_orgs_category ON organizations (category);
