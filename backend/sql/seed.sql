-- Sample data for local development.
-- All seeded users share the password: password123

INSERT INTO categories (category_name) VALUES ('Academic');
INSERT INTO categories (category_name) VALUES ('Sports');
INSERT INTO categories (category_name) VALUES ('Cultural');
INSERT INTO categories (category_name) VALUES ('Volunteer');
INSERT INTO categories (category_name) VALUES ('Technology');

INSERT INTO organizations (organization_name, description, category, contact_email)
VALUES ('The Ateneo Consortium of Technological, Information, and Computing Sciences (TACTICS)', 'The Official Organization for Department of Computer Studies.', 'Technology', 'tactics@adnu.edu.ph');

INSERT INTO organizations (organization_name, description, category, contact_email)
VALUES ('Ateneo Film Society (AFS)', 'An Organization for Aspiring Film Makers.', 'Cultural', 'afs@adnu.edu.ph');

INSERT INTO organizations (organization_name, description, category, contact_email)
VALUES ('ThePILLARS Publication', 'University Publication', 'Academic', 'thepillars@adnu.edu.ph');

INSERT INTO organizations (organization_name, description, category, contact_email)
VALUES ('Ateneo Golden Knights (AKG)', 'University Basketball Varsity Team', 'Sports', 'akg@adnu.edu.ph');

INSERT INTO organizations (organization_name, description, category, contact_email)
VALUES ('Liderato kan Nueva Atenista', 'University Student Government', 'Volunteer', 'liderato@adnu.edu.ph');

-- Admin account
INSERT INTO users (first_name, last_name, email, password_hash, role, organization_id)
VALUES ('Ada', 'Admin', 'admin@adnu.edu.ph', '$2b$12$1UNPEWIHjkLghPxw26T6jeHb1/gYssvVJVjPJ8AGV.O24hmAdqDUG', 'admin', NULL);

-- Main admin login for website management
INSERT INTO users (first_name, last_name, email, password_hash, role, organization_id)
VALUES ('Bluehub', 'Admin', 'bluehub@adnu.edu.ph', '$2b$12$Fs1zXkzKy/ByVjPW.F/USuEL1J609TO3ZLHHagh34wD18pkLFtKi.', 'admin', NULL);

-- Officer account tied to the CS Society (organization_id 1)
INSERT INTO users (first_name, last_name, email, password_hash, role, organization_id)
VALUES ('Micco', 'Alcantara', 'officer@adnu.edu.ph', '$2b$12$1UNPEWIHjkLghPxw26T6jeHb1/gYssvVJVjPJ8AGV.O24hmAdqDUG', 'officer', 1);

-- Regular student account
INSERT INTO users (first_name, last_name, email, password_hash, role, organization_id)
VALUES ('Sam', 'Student', 'student@adnu.edu.ph', '$2b$12$1UNPEWIHjkLghPxw26T6jeHb1/gYssvVJVjPJ8AGV.O24hmAdqDUG', 'student', NULL);

INSERT INTO events (organization_id, title, description, venue, event_date, category, created_by)
VALUES (1, 'TACTICS Tech Showcase', 'A showcase of student projects from the Department of Computer Studies.', 'Computer Labs', DATE '2026-09-10', 'Technology', 2);

INSERT INTO events (organization_id, title, description, venue, event_date, category, created_by)
VALUES (2, 'AFS Short Film Night', 'An evening of original short films created by aspiring filmmakers.', 'Multipurpose Hall', DATE '2026-09-17', 'Cultural', 3);

INSERT INTO events (organization_id, title, description, venue, event_date, category, created_by)
VALUES (3, 'ThePILLARS Journalism Forum', 'A discussion on university publication and student journalism.', 'Ateneo Avenue', DATE '2026-09-24', 'Academic', 3);

INSERT INTO events (organization_id, title, description, venue, event_date, category, created_by)
VALUES (4, 'AKG Home Game', 'Support the Ateneo Golden Knights at their university basketball match.', 'University Gymnasium', DATE '2026-10-01', 'Sports', 3);

INSERT INTO events (organization_id, title, description, venue, event_date, category, created_by)
VALUES (5, 'Liderato Townhall', 'Student government town hall meeting for the campus community.', 'Ignatius Park', DATE '2026-10-08', 'Volunteer', 3);

COMMIT;


--- admin account
--- email admin@adnu.edu.ph
--- password password123
