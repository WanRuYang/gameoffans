\c reddit

ALTER TABLE posts DROP CONSTRAINT id;
ALTER TABLE comments DROP CONSTRAINT id;

DROP TABLE IF EXISTS movies CASCADE;
DROP TABLE IF EXISTS posts CASCADE;
DROP TABLE IF EXISTS comments CASCADE;

CREATE TABLE movies(
    id varchar PRIMARY KEY,
    title varchar NOT NULL, 
    rating int, 
    votes int, 
    released TIMESTAMP
);

CREATE TABLE posts(
        id varchar PRIMARY KEY, 
        author varchar, 
        score int,
        pred boolean,
        vader numeric,
        num_comments int,
        title varchar,  
        -- media varchar,
        time TIMESTAMP NOT NULL
        );

CREATE TABLE comments(
        id varchar PRIMARY KEY,
        link_id varchar, 
        author varchar,
        score int,
        pred boolean,
        vader numeric,
        body varchar,
        time TIMESTAMP NOT NULL,
    CONSTRAINT link_id_key FOREIGN KEY (link_id) REFERENCES posts (id)
        );

\COPY movies FROM 'DB_movies.csv' DELIMITERS ',' CSV HEADER;
\COPY posts FROM 'DB_posts.csv' DELIMITERS ',' CSV HEADER;
\COPY comments FROM 'DB_comments.csv' DELIMITERS ',' CSV HEADER;
