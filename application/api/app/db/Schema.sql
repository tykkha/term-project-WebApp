DROP DATABASE IF EXISTS GatorGuides;
CREATE DATABASE GatorGuides;
USE GatorGuides;

# Registered User table and content
DROP TABLE IF EXISTS User;
CREATE TABLE User
(
    uid            INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    firstName      VARCHAR(255)                   NOT NULL,
    lastName       VARCHAR(255)                   NOT NULL,
    email          VARCHAR(255) UNIQUE            NOT NULL,
    password       VARCHAR(255)                   NOT NULL,
    Type           ENUM ('user', 'admin'),
    profilePicture VARCHAR(255),
    bio            TEXT
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
    tid                INT PRIMARY KEY AUTO_INCREMENT,
    uid                INT NOT NULL,
    rating             DOUBLE,
    status             ENUM ('available', 'away', 'busy')         DEFAULT 'available',
    verificationStatus ENUM ('unapproved', 'pending', 'approved') DEFAULT 'unapproved',
    FOREIGN KEY (uid) REFERENCES User (uid) ON DELETE CASCADE
);

# Removes the need to search a tutors tags via their posts, streamlining the searching process
DROP TABLE IF EXISTS TutorTags;
CREATE TABLE TutorTags
(
    tutorTagID INT PRIMARY KEY AUTO_INCREMENT,
    tid        INT NOT NULL,
    tagsID     INT NOT NULL,
    FOREIGN KEY (tid) REFERENCES Tutor (tid) ON DELETE CASCADE,
    FOREIGN KEY (tagsID) REFERENCES Tags (tagsID) ON DELETE CASCADE,
    UNIQUE KEY (tid, tagsID)
);

# Posts table contains posts made by tutors and relevant content
DROP TABLE IF EXISTS Posts;
CREATE TABLE Posts
(
    pid       INT PRIMARY KEY AUTO_INCREMENT,
    tid       INT NOT NULL,
    tagsID    INT NOT NULL,
    content   TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tid) REFERENCES Tutor (tid) ON DELETE CASCADE,
    FOREIGN KEY (tagsID) REFERENCES Tags (tagsID) ON DELETE CASCADE
);

# Sessions table holds all past, current, and future tutoring sessions scheduled
DROP TABLE IF EXISTS Sessions;
CREATE TABLE Sessions
(
    sid       INT PRIMARY KEY AUTO_INCREMENT,
    tid       INT,
    uid       INT,
    tagsID    INT NOT NULL,
    day       ENUM ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),
    time      INT CHECK (time >= 0 AND time <= 23),
    started   DATETIME DEFAULT NULL,
    concluded DATETIME DEFAULT NULL,
    FOREIGN KEY (tid) REFERENCES Tutor (tid) ON DELETE CASCADE,
    FOREIGN KEY (uid) REFERENCES User (uid) ON DELETE CASCADE,
    FOREIGN KEY (tagsID) REFERENCES Tags (tagsID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS Ratings;
CREATE TABLE Ratings
(
    rid       INT PRIMARY KEY AUTO_INCREMENT,
    tid       INT    NOT NULL,
    uid       INT    NOT NULL,
    sid       INT    NOT NULL,
    rating    DOUBLE NOT NULL CHECK (rating >= 0 AND rating <= 5),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tid) REFERENCES Tutor (tid) ON DELETE CASCADE,
    FOREIGN KEY (uid) REFERENCES User (uid) ON DELETE CASCADE,
    FOREIGN KEY (sid) REFERENCES Sessions (sid) ON DELETE CASCADE,
    UNIQUE KEY per_session_rating (uid, sid)
);

# Generic messages table to populate dms between users and tutors
DROP TABLE IF EXISTS Messages;
CREATE TABLE Messages
(
    mid         INT PRIMARY KEY AUTO_INCREMENT,
    senderUID   INT  NOT NULL,
    receiverUID INT  NOT NULL,
    content     TEXT NOT NULL,
    timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (senderUID) REFERENCES User (uid) ON DELETE CASCADE,
    FOREIGN KEY (receiverUID) REFERENCES User (uid) ON DELETE CASCADE
);

# Login Sessions table for authentication
DROP TABLE IF EXISTS LoginSessions;
CREATE TABLE LoginSessions
(
    sessionID VARCHAR(64) PRIMARY KEY,
    uid       INT      NOT NULL,
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    expiresAt DATETIME NOT NULL,
    FOREIGN KEY (uid) REFERENCES User (uid) ON DELETE CASCADE,
    INDEX idx_session_expiry (expiresAt)
);

# Tutor Availability table for managing tutors available time slots
DROP TABLE IF EXISTS TutorAvailability;
CREATE TABLE TutorAvailability
(
    availabilityID INT PRIMARY KEY AUTO_INCREMENT,
    tid            INT NOT NULL,
    day            ENUM ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL,
    startTime      INT NOT NULL CHECK (startTime >= 0 AND startTime <= 23),
    endTime        INT NOT NULL CHECK (endTime >= 0 AND endTime <= 23),
    isActive       BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (tid) REFERENCES Tutor (tid) ON DELETE CASCADE,
    UNIQUE KEY unique_availability (tid, day, startTime, endTime)
);