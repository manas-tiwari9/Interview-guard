import random

QUESTIONS = [
    # ── Programming Fundamentals ─────────────────────────────
    "What is the difference between compiled and interpreted languages? Give one example of each.",
    "Explain recursion with a simple example. What is a base case and why is it essential?",
    "What is the difference between stack memory and heap memory? When is each used?",
    "What is type casting? Explain the difference between implicit and explicit type casting.",
    "What are pointers? How do references differ from pointers in modern languages?",
    "What is the difference between pass-by-value and pass-by-reference? Give examples.",

    # ── Object-Oriented Programming ──────────────────────────
    "What are the four pillars of Object-Oriented Programming? Explain each briefly.",
    "What is the difference between an abstract class and an interface?",
    "Explain method overriding and method overloading with examples.",
    "What is the difference between inheritance and composition? When would you prefer composition?",
    "What is polymorphism? Explain runtime polymorphism vs compile-time polymorphism.",
    "What is encapsulation? Why is it an important principle in software design?",
    "Explain the SOLID principles of software design.",
    "What is the difference between a class and an object?",

    # ── Data Structures ──────────────────────────────────────
    "What is the difference between an array and a linked list? When would you choose each?",
    "Explain how a hash table works internally. What is a collision and how is it resolved?",
    "What is a binary search tree? Describe its properties and time complexities.",
    "What is the difference between a stack and a queue? Provide real-world examples of each.",
    "What is a graph data structure? What are the differences between directed and undirected graphs?",
    "What is a heap data structure? Explain min-heap vs max-heap.",
    "What is a trie (prefix tree) and what are its primary use cases?",
    "What is the difference between a tree and a graph?",
    "What is a deque and how does it differ from a regular queue?",

    # ── Algorithms ───────────────────────────────────────────
    "What is the time complexity of binary search? Explain how it works step by step.",
    "What is the difference between BFS and DFS? When would you use each algorithm?",
    "What is dynamic programming? Explain with an example problem.",
    "Compare merge sort and quick sort in terms of time complexity, space complexity, and stability.",
    "What is Big O notation? Why is it important for algorithm analysis?",
    "What is a greedy algorithm? Provide a classic example and explain when greedy works.",
    "What is the difference between divide-and-conquer and dynamic programming?",
    "Explain the two-pointer technique and give an example problem it solves efficiently.",

    # ── Operating Systems ────────────────────────────────────
    "What is the difference between a process and a thread?",
    "What is a deadlock? What are the four necessary conditions (Coffman conditions)?",
    "Explain virtual memory. What is paging and how does a page table work?",
    "What is context switching in an operating system and why does it have overhead?",
    "What is the difference between a mutex and a semaphore?",
    "Describe the round-robin CPU scheduling algorithm and its advantages.",

    # ── Database Management Systems ──────────────────────────
    "What does ACID stand for in database transactions? Explain each property with an example.",
    "What is the difference between SQL and NoSQL databases? When would you choose each?",
    "Explain database normalization. What problems do 1NF, 2NF, and 3NF solve?",
    "What is a database index? How does it improve read performance and what is its tradeoff?",
    "What is a JOIN operation? Describe INNER JOIN, LEFT JOIN, RIGHT JOIN, and FULL OUTER JOIN.",
    "What is the difference between DELETE, DROP, and TRUNCATE in SQL?",
    "What is a database transaction? How do COMMIT and ROLLBACK work?",

    # ── Computer Networks ────────────────────────────────────
    "What are the seven layers of the OSI model? Briefly describe the role of each layer.",
    "What is the difference between TCP and UDP? When would you prefer UDP over TCP?",
    "What is the difference between HTTP and HTTPS? How does TLS/SSL provide security?",
    "What is a RESTful API? What are its six architectural constraints?",
    "How does DNS resolution work? Walk through the steps from a browser request to an IP address.",
    "What is the difference between a router and a switch?",
    "What is a three-way handshake in TCP? Why is it needed?",

    # ── Python ───────────────────────────────────────────────
    "What are Python decorators and how do they work? Write a simple example.",
    "Explain the difference between a list, tuple, set, and dictionary in Python.",
    "What are Python generators? How do they differ from regular functions returning lists?",
    "What is the difference between `is` and `==` in Python? Give an example where they differ.",
    "What is Python's GIL (Global Interpreter Lock) and how does it affect multi-threaded programs?",
    "What are list comprehensions in Python and how do they compare to traditional for loops?",

    # ── Machine Learning Basics ──────────────────────────────
    "What is the difference between supervised, unsupervised, and reinforcement learning?",
    "What is overfitting? List three techniques to prevent it.",
    "Explain the bias-variance tradeoff. What happens when bias is too high or variance is too high?",
    "What is cross-validation and why is it used instead of a single train/test split?",
    "What is the difference between precision and recall? When is each metric more important?",

    # ── System Design Basics ─────────────────────────────────
    "What is the difference between horizontal scaling and vertical scaling?",
    "What is a load balancer? Describe how it distributes incoming traffic.",
    "What is caching? Describe two common cache invalidation strategies.",
    "What is a microservices architecture and how does it compare to a monolithic architecture?",
    "Explain the CAP theorem. Can a distributed system guarantee all three properties simultaneously?",
    "What is an API gateway and what role does it play in a microservices system?",
]


def get_session_questions(n: int = 20) -> list:
    pool = QUESTIONS.copy()
    random.shuffle(pool)
    return pool[:n]
