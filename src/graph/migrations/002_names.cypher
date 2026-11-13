CREATE INDEX person_name IF NOT EXISTS FOR (p:Person) ON (p.name);
CREATE INDEX movie_title IF NOT EXISTS FOR (m:Movie) ON (m.title);
