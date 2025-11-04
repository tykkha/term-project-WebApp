DROP DATABASE IF EXISTS GatorGuides;
CREATE DATABASE GatorGuides;
USE GatorGuides;

# Registered User table and content
DROP TABLE IF EXISTS User;
CREATE TABLE User
(
    uid      INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    email    VARCHAR(255) UNIQUE            NOT NULL,
    password VARCHAR(255)                   NOT NULL,
    Type     ENUM ('user', 'admin')
);

# Lookup table for tags (class name + number)
DROP TABLE IF EXISTS Tags;
CREATE TABLE Tags
(
    tagsID INT PRIMARY KEY AUTO_INCREMENT,
    tags   VARCHAR(8)
);

# Tutor (also a registered user) contains rating and relevant info
DROP TABLE IF EXISTS Tutor;
CREATE TABLE Tutor
(
    tid    INT PRIMARY KEY AUTO_INCREMENT,
    uid    INT NOT NULL,
    rating DOUBLE,
    FOREIGN KEY (uid) REFERENCES User (uid) ON DELETE CASCADE
);

# Posts table contains posts made by tutors and relevant content
DROP TABLE IF EXISTS Posts;
CREATE TABLE Posts
(
    pid       INT PRIMARY KEY AUTO_INCREMENT,
    tid       INT NOT NULL,
    tags      INT NOT NULL,
    content   TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tid) REFERENCES Tutor (tid) ON DELETE CASCADE,
    FOREIGN KEY (tags) REFERENCES Tags (tagsID) ON DELETE CASCADE
);

# Profile table contains information to populate profiles
DROP TABLE IF EXISTS Profile;
CREATE TABLE Profile
(
    profileID INT PRIMARY KEY AUTO_INCREMENT,
    uid       INT NOT NULL,
    tags      INT NOT NULL,
    status    VARCHAR(50),
    bio       TEXT,
    FOREIGN KEY (uid) REFERENCES User (uid) ON DELETE CASCADE,
    FOREIGN KEY (tags) REFERENCES Tags (tagsID) ON DELETE CASCADE
);

# Sessions table holds all past, current, and future tutoring sessions scheduled
DROP TABLE IF EXISTS Sessions;
CREATE TABLE Sessions
(
    sid       INT PRIMARY KEY AUTO_INCREMENT,
    tid       INT,
    uid       INT,
    tags      INT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    concluded DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tid) REFERENCES Tutor (tid) ON DELETE CASCADE,
    FOREIGN KEY (uid) REFERENCES User (uid) ON DELETE CASCADE,
    FOREIGN KEY (tags) REFERENCES Tags (tagsID) ON DELETE CASCADE
);

# Generic messages table to populate dms between users and tutors
DROP TABLE IF EXISTS Messages;
CREATE TABLE Messages
(
    mid       INT PRIMARY KEY AUTO_INCREMENT,
    uid       INT,
    content   TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uid) REFERENCES User (uid) ON DELETE CASCADE
);