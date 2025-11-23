USE GatorGuides;

-- Insert Users
INSERT INTO User (firstName, lastName, email, password, Type, profilePicture, bio) VALUES
('John', 'Smith', 'john.smith@sfsu.edu', 'password123', 'user', NULL, 'Experienced data structures tutor with 3 years of teaching experience. Specializing in trees, graphs, and algorithms.'),
('Jane', 'Smith', 'jane.smith@sfsu.edu', 'password123', 'user', NULL, 'Patient tutor focusing on programming fundamentals. Love helping beginners understand coding concepts!'),
('Michael', 'Johnson', 'michael.johnson@sfsu.edu', 'password123', 'user', NULL, 'Graduate student specializing in algorithms and data structures. Published researcher with strong teaching background.'),
('Emily', 'Johnson', 'emily.johnson@sfsu.edu', 'password123', 'user', NULL, 'Math enthusiast helping students conquer calculus. Clear explanations and lots of practice problems!'),
('David', 'Williams', 'david.williams@sfsu.edu', 'password123', 'user', NULL, 'Discrete math made easy! Proofs, logic, and set theory explained simply.'),
('Sarah', 'Williams', 'sarah.williams@sfsu.edu', 'password123', 'user', NULL, 'Software engineering professional with industry experience. Agile methodologies and best practices.'),
('Robert', 'Brown', 'robert.brown@sfsu.edu', 'password123', 'user', NULL, 'Physics tutor covering mechanics, electricity, and magnetism. Problem-solving focused approach.'),
('Jessica', 'Davis', 'jessica.davis@sfsu.edu', 'password123', 'user', NULL, 'Coding bootcamp graduate turned tutor. I understand the struggles of learning to code!'),
('James', 'Miller', 'james.miller@sfsu.edu', 'password123', 'user', NULL, 'Computer architecture and organization expert. Assembly language and digital logic specialist.'),
('Ashley', 'Wilson', 'ashley.wilson@sfsu.edu', 'password123', 'user', NULL, 'AI and machine learning tutor. Making complex concepts accessible to everyone.'),
('Christopher', 'Moore', 'chris.moore@sfsu.edu', 'password123', 'user', NULL, 'Data structures wizard! Let me help you ace CSC 220 with clear explanations and practice.'),
('Amanda', 'Taylor', 'amanda.taylor@sfsu.edu', 'password123', 'user', NULL, 'Linear algebra made simple. Matrices, vector spaces, and eigenvalues demystified.'),
('Daniel', 'Anderson', 'daniel.anderson@sfsu.edu', 'password123', 'user', NULL, 'Network protocols and architecture specialist. TCP/IP, routing, and network security.'),
('Jennifer', 'Thomas', 'jennifer.thomas@sfsu.edu', 'password123', 'user', NULL, 'Calculus tutor with a passion for teaching. Limits, derivatives, and integrals explained clearly.'),
('Matthew', 'Jackson', 'matthew.jackson@sfsu.edu', 'password123', 'user', NULL, 'Operating systems tutor covering processes, threads, memory management, and file systems.'),
('Lauren', 'White', 'lauren.white@sfsu.edu', 'password123', 'user', NULL, 'New tutor excited to help! Strong foundation in programming fundamentals.'),
('Andrew', 'Harris', 'andrew.harris@sfsu.edu', 'password123', 'user', NULL, 'Programming languages enthusiast. Functional programming, compilers, and language design.'),
('Brittany', 'Martin', 'brittany.martin@sfsu.edu', 'password123', 'user', NULL, 'Data structures tutor with focus on practical implementation and interview prep.'),
('Joshua', 'Thompson', 'joshua.thompson@sfsu.edu', 'password123', 'user', NULL, 'Numerical methods and scientific computing. MATLAB and computational mathematics.'),
('Samantha', 'Garcia', 'samantha.garcia@sfsu.edu', 'password123', 'user', NULL, 'OOP expert! Classes, inheritance, polymorphism, and design patterns made easy.'),
('Kevin', 'Martinez', 'kevin.martinez@sfsu.edu', 'password123', 'user', NULL, 'Computer organization tutor. CPU design, cache memory, and performance optimization.'),
('Nicole', 'Robinson', 'nicole.robinson@sfsu.edu', 'password123', 'user', NULL, 'Statistics tutor helping students with probability, distributions, and hypothesis testing.'),
('Ryan', 'Clark', 'ryan.clark@sfsu.edu', 'password123', 'user', NULL, 'OS concepts simplified. Scheduling algorithms, deadlocks, and synchronization.'),
('Megan', 'Rodriguez', 'megan.rodriguez@sfsu.edu', 'password123', 'user', NULL, 'Machine learning and neural networks. Theory and practical implementation with Python.'),
('Brandon', 'Lewis', 'brandon.lewis@sfsu.edu', 'password123', 'user', NULL, 'Logic and proofs specialist. Helping students build strong mathematical reasoning skills.'),
('Rachel', 'Lee', 'rachel.lee@sfsu.edu', 'password123', 'user', NULL, NULL),
('Tyler', 'Walker', 'tyler.walker@sfsu.edu', 'password123', 'user', NULL, NULL),
('Stephanie', 'Hall', 'stephanie.hall@sfsu.edu', 'password123', 'user', NULL, NULL),
('Justin', 'Allen', 'justin.allen@sfsu.edu', 'password123', 'user', NULL, NULL),
('Amber', 'Young', 'amber.young@sfsu.edu', 'password123', 'user', NULL, NULL),
('Admin', 'User', 'admin@sfsu.edu', 'admin123', 'admin', NULL, NULL),
('Mark', 'Johnson', 'mark.johnson@sfsu.edu', 'password123', 'user', NULL, 'Computer Science student looking for tutoring help.'),
('Lisa', 'Smith', 'lisa.smith@sfsu.edu', 'password123', 'user', NULL, 'Math major seeking calculus support.'),
('Tom', 'Williams', 'tom.williams@sfsu.edu', 'password123', 'user', NULL, NULL);

-- Insert Course Tags (SFSU naming)
INSERT INTO Tags (tags) VALUES
('CSC 210'),  -- 1: Introduction to Computer Programming
('CSC 215'),  -- 2: Intermediate Computer Programming
('CSC 220'),  -- 3: Data Structures
('CSC 600'),  -- 4: Programming Paradigms and Languages
('CSC 415'),  -- 5: Operating System Principles
('CSC 256'),  -- 6: Machine Structures (Computer Organization)
('CSC 230'),  -- 7: Discrete Mathematical Structures
('MATH 226'), -- 8: Calculus I
('MATH 227'), -- 9: Calculus II
('MATH 228'), -- 10: Calculus III
('PHYS 220'), -- 11: General Physics with Calculus I
('PHYS 230'), -- 12: General Physics with Calculus II
('CSC 648'),  -- 13: Software Engineering
('CSC 645'),  -- 14: Computer Networks
('CSC 665'),  -- 15: Artificial Intelligence
('CSC 675'),  -- 16: Introduction to Database Systems
('MATH 400'), -- 17: Numerical Analysis
('MATH 124'), -- 18: Elementary Statistics
('MATH 225'), -- 19: Introduction to Linear Algebra
('ENGR 305'); -- 20: Linear Systems Analysis (Signals & Systems)

-- Insert Tutors with varying ratings, statuses, and verification statuses
INSERT INTO Tutor (uid, rating, status, verificationStatus) VALUES
(1, 4.8, 'available', 'approved'),
(2, 4.5, 'available', 'approved'),
(3, 4.9, 'busy', 'approved'),
(4, 4.7, 'available', 'approved'),
(5, 4.3, 'available', 'approved'),
(6, 4.6, 'available', 'approved'),
(7, 4.4, 'away', 'approved'),
(8, 4.8, 'available', 'approved'),
(9, 4.2, 'available', 'approved'),
(10, 4.9, 'available', 'approved'),
(11, 4.5, 'available', 'approved'),
(12, 4.7, 'available', 'approved'),
(13, 4.6, 'available', 'approved'),
(14, 4.8, 'available', 'approved'),
(15, 4.4, 'busy', 'approved'),
(16, 4.9, 'available', 'pending'),
(17, 4.3, 'available', 'approved'),
(18, 4.7, 'available', 'approved'),
(19, 4.5, 'available', 'approved'),
(20, 4.8, 'available', 'approved'),
(21, 4.6, 'available', 'approved'),
(22, 4.4, 'available', 'approved'),
(23, 4.7, 'available', 'approved'),
(24, 4.9, 'available', 'approved'),
(25, 4.5, 'available', 'approved');

-- Insert TutorTags (tutor expertise)
INSERT INTO TutorTags (tid, tagsID) VALUES
-- John Smith - Data Structures & Programming
(1, 3), (1, 1),
-- Jane Smith - Programming Fundamentals
(2, 1), (2, 2),
-- Michael Johnson - Advanced CS
(3, 3), (3, 4), (3, 5),
-- Emily Johnson - Calculus
(4, 8), (4, 9), (4, 10),
-- David Williams - Discrete Math
(5, 7),
-- Sarah Williams - Software Engineering & Databases
(6, 13), (6, 16),
-- Robert Brown - Physics
(7, 11), (7, 12),
-- Jessica Davis - Programming (Multiple Courses)
(8, 1), (8, 2), (8, 3),
-- James Miller - Computer Organization
(9, 6),
-- Ashley Wilson - AI & Databases
(10, 15), (10, 16),
-- Christopher Moore - Data Structures
(11, 3),
-- Amanda Taylor - Linear Algebra
(12, 19),
-- Daniel Anderson - Computer Networks
(13, 14),
-- Jennifer Thomas - Calculus
(14, 8), (14, 9),
-- Matthew Jackson - Operating Systems
(15, 5),
-- Lauren White - Programming & Statistics
(16, 1), (16, 18),
-- Andrew Harris - Programming Languages
(17, 4),
-- Brittany Martin - Data Structures & Software Engineering
(18, 3), (18, 13),
-- Joshua Thompson - Numerical Analysis
(19, 17),
-- Samantha Garcia - OOP & Data Structures
(20, 2), (20, 3),
-- Kevin Martinez - Computer Organization
(21, 6),
-- Nicole Robinson - Statistics
(22, 18),
-- Ryan Clark - Operating Systems
(23, 5),
-- Megan Rodriguez - AI & Data Structures
(24, 15), (24, 3),
-- Brandon Lewis - Discrete Math
(25, 7);

-- Insert Posts for tutors
INSERT INTO Posts (tid, tagsID, content, timestamp) VALUES
-- John Smith (tid=1) - Data Structures & Programming
(1, 3, 'Offering tutoring sessions for CSC 220! I specialize in binary trees, AVL trees, and graph algorithms. Available Mon-Fri evenings.', '2024-11-01 10:00:00'),
(1, 3, 'New study group forming for midterm prep! Focusing on sorting algorithms and complexity analysis. DM me if interested.', '2024-11-03 14:30:00'),
(1, 1, 'Beginner-friendly programming sessions available. Let us work through your CSC 210 assignments together!', '2024-11-05 09:00:00'),

-- Jane Smith (tid=2) - Programming Fundamentals
(2, 1, 'Hi everyone! Offering help with loops, conditionals, and functions. Patient explanations guaranteed!', '2024-11-01 11:00:00'),
(2, 2, 'CSC 215 students - struggling with pointers? Let me break it down for you in simple terms.', '2024-11-04 15:00:00'),
(2, 1, 'Office hours this week: Tuesday 3-5pm, Thursday 2-4pm. Come by with questions!', '2024-11-06 08:00:00'),

-- Michael Johnson (tid=3) - Advanced CS
(3, 3, 'Graduate-level data structures tutoring available. Research experience in algorithm optimization.', '2024-11-01 12:00:00'),
(3, 4, 'Programming languages concepts: lexical analysis, parsing, and code generation. Let us dive deep!', '2024-11-02 16:00:00'),
(3, 5, 'OS scheduling algorithms giving you trouble? I can explain FCFS, SJF, Round Robin, and more.', '2024-11-07 10:00:00'),

-- Emily Johnson (tid=4) - Calculus
(4, 8, 'Calculus 1 tutoring: limits, derivatives, and applications. Visual learning approach!', '2024-11-01 13:00:00'),
(4, 9, 'Integration techniques workshop this Saturday! Series and sequences included.', '2024-11-03 17:00:00'),
(4, 10, 'Multivariable calculus help: partial derivatives, multiple integrals, vector calculus.', '2024-11-05 11:00:00'),

-- David Williams (tid=5) - Discrete Math
(5, 7, 'Discrete structures tutoring: mathematical induction, recursion, and combinatorics.', '2024-11-01 14:00:00'),
(5, 7, 'Struggling with proofs? Let us work through direct proofs, contradiction, and contraposition.', '2024-11-04 12:00:00'),

-- Sarah Williams (tid=6) - Software Engineering & Databases
(6, 13, 'Software engineering best practices: Agile, Scrum, and version control with Git.', '2024-11-02 09:00:00'),
(6, 16, 'Database design and SQL queries. Normalization, ER diagrams, and query optimization.', '2024-11-05 14:00:00'),
(6, 13, 'Working on group projects? I can help with team coordination and project management.', '2024-11-07 11:00:00'),

-- Robert Brown (tid=7) - Physics
(7, 11, 'Physics 1 tutoring: kinematics, dynamics, energy, and momentum. Problem-solving focus.', '2024-11-01 15:00:00'),
(7, 12, 'Electricity and magnetism explained! Circuits, fields, and electromagnetic induction.', '2024-11-06 13:00:00'),

-- Jessica Davis (tid=8) - Programming (Multiple Courses)
(8, 1, 'Just finished CSC 210 with an A! Happy to help fellow students with programming basics.', '2024-11-02 10:00:00'),
(8, 2, 'Object-oriented programming workshop: classes, objects, inheritance, and polymorphism.', '2024-11-04 16:00:00'),
(8, 3, 'Data structures study session! Bring your questions about linked lists and stacks.', '2024-11-06 09:00:00'),

-- James Miller (tid=9) - Computer Organization
(9, 6, 'Computer organization help: assembly language programming and CPU architecture.', '2024-11-02 11:00:00'),
(9, 6, 'Cache memory and performance optimization. Let us speed up your code!', '2024-11-05 15:00:00'),

-- Ashley Wilson (tid=10) - AI & Databases
(10, 15, 'Introduction to AI: search algorithms, knowledge representation, and machine learning basics.', '2024-11-01 16:00:00'),
(10, 16, 'SQL mastery sessions! From basic SELECT to complex JOINs and subqueries.', '2024-11-03 10:00:00'),
(10, 15, 'Neural networks and deep learning. Building your first AI model with Python.', '2024-11-07 14:00:00'),

-- Christopher Moore (tid=11) - Data Structures
(11, 3, 'CSC 220 exam prep! Hash tables, heaps, and priority queues explained clearly.', '2024-11-02 12:00:00'),
(11, 3, 'Algorithm analysis workshop: Big O notation, time complexity, and space complexity.', '2024-11-05 16:00:00'),

-- Amanda Taylor (tid=12) - Linear Algebra
(12, 19, 'Linear algebra tutoring: matrix operations, determinants, and linear transformations.', '2024-11-01 17:00:00'),
(12, 19, 'Eigenvalues and eigenvectors demystified! Applications in CS and engineering.', '2024-11-06 10:00:00'),

-- Daniel Anderson (tid=13) - Computer Networks
(13, 14, 'Computer networks help: OSI model, TCP/IP, and network protocols.', '2024-11-02 13:00:00'),
(13, 14, 'Network security basics: encryption, firewalls, and secure communication.', '2024-11-04 17:00:00'),

-- Jennifer Thomas (tid=14) - Calculus
(14, 8, 'Struggling with derivatives? Let us master the chain rule, product rule, and quotient rule!', '2024-11-03 11:00:00'),
(14, 9, 'Calculus 2 final exam prep! Integration techniques and series convergence.', '2024-11-06 14:00:00'),

-- Matthew Jackson (tid=15) - Operating Systems
(15, 5, 'Operating systems concepts: processes, threads, and inter-process communication.', '2024-11-02 14:00:00'),
(15, 5, 'Memory management techniques: paging, segmentation, and virtual memory.', '2024-11-05 12:00:00'),

-- Lauren White (tid=16) - Programming & Statistics
(16, 1, 'New tutor here! Strong foundation in programming. Let us learn together!', '2024-11-03 12:00:00'),
(16, 18, 'Statistics help: probability distributions, confidence intervals, and hypothesis testing.', '2024-11-07 15:00:00'),

-- Andrew Harris (tid=17) - Programming Languages
(17, 4, 'Functional programming workshop! Learn the paradigm with Haskell and Scheme examples.', '2024-11-02 15:00:00'),
(17, 4, 'Compiler design: lexical analysis, syntax analysis, and code generation phases.', '2024-11-06 11:00:00'),

-- Brittany Martin (tid=18) - Data Structures & Software Engineering
(18, 3, 'Interview prep for tech companies! Data structures and algorithms practice.', '2024-11-01 18:00:00'),
(18, 13, 'Agile development and Scrum methodology. Real-world software engineering experience.', '2024-11-04 13:00:00'),
(18, 3, 'Graph algorithms: BFS, DFS, Dijkstra, and minimum spanning trees explained.', '2024-11-07 16:00:00'),

-- Joshua Thompson (tid=19) - Numerical Analysis
(19, 17, 'Numerical methods: root finding, interpolation, and numerical integration.', '2024-11-03 13:00:00'),
(19, 17, 'MATLAB tutoring for scientific computing and engineering applications.', '2024-11-06 12:00:00'),

-- Samantha Garcia (tid=20) - OOP & Data Structures
(20, 2, 'Object-oriented design patterns: Singleton, Factory, Observer, and more!', '2024-11-02 16:00:00'),
(20, 3, 'Advanced data structures: Red-Black trees, B-trees, and Fibonacci heaps.', '2024-11-05 17:00:00'),

-- Kevin Martinez (tid=21) - Computer Organization
(21, 6, 'Assembly language programming: MIPS architecture and instruction set.', '2024-11-03 14:00:00'),
(21, 6, 'CPU design and pipelining. Understanding instruction execution cycles.', '2024-11-07 12:00:00'),

-- Nicole Robinson (tid=22) - Statistics
(22, 18, 'Statistics tutoring: descriptive statistics, probability, and inferential statistics.', '2024-11-01 19:00:00'),
(22, 18, 'Regression analysis and ANOVA. Statistical modeling for research projects.', '2024-11-05 13:00:00'),

-- Ryan Clark (tid=23) - Operating Systems
(23, 5, 'File systems and storage management. Understanding disk scheduling and RAID.', '2024-11-02 17:00:00'),
(23, 5, 'Deadlock prevention and avoidance strategies. Resource allocation graphs explained.', '2024-11-06 15:00:00'),

-- Megan Rodriguez (tid=24) - AI & Data Structures
(24, 15, 'Deep learning fundamentals: CNNs, RNNs, and transformers for NLP.', '2024-11-03 15:00:00'),
(24, 3, 'Competitive programming practice! LeetCode and algorithmic problem-solving.', '2024-11-05 18:00:00'),
(24, 15, 'Machine learning project help: data preprocessing, model training, and evaluation.', '2024-11-07 13:00:00'),

-- Brandon Lewis (tid=25) - Discrete Math
(25, 7, 'Graph theory: paths, cycles, trees, and graph coloring problems.', '2024-11-02 18:00:00'),
(25, 7, 'Number theory and cryptography basics. Modular arithmetic and RSA algorithm.', '2024-11-06 16:00:00');