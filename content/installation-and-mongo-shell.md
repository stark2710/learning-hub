---
title: "Installation and MongoDB Shell"
module: "MongoDB Fundamentals"
domain: "MongoDB"
lesson_id: "installation-and-mongo-shell"
prev: "backend-mastery-mongodb-m1-l1-document-database-concepts"
next: ""
duration: "~30 min"
---

```system_prompt
You are a MongoDB expert and database architect with 15+ years of experience, including deep work with both relational and document databases. The student has 4+ years of backend experience (3 years Java, 1+ year Python) and understands SQL databases well.

For this lesson on Installation and MongoDB Shell:
- Walk the student through installing MongoDB
- Introduce the MongoDB shell and basic commands
- Highlight key differences from traditional SQL shells
- Encourage experimentation with simple queries

Always respond in plain English.
```

## What You'll Learn

- How to install MongoDB on your local machine (Windows, macOS, Linux)
- The basics of the MongoDB shell: `mongo` command, syntax, and navigation
- Key differences between MongoDB shell and traditional SQL shells (e.g., no SQL keywords)

---

## The Mental Model

Let's get started with installing MongoDB. This will be a hands-on experience!

**Install MongoDB**

You can download the Community Server from the official MongoDB website: [https://www.mongodb.com/download-center](https://www.mongodb.com/download-center). For this example, we'll use the Windows version.

Follow these steps:

1. Download and run the installer (approximately 200MB).
2. Choose the installation path and default settings.
3. Wait for the installation to complete.
4. Once installed, you can find the MongoDB Server in your Start menu or Spotlight search.

**Basic MongoDB Shell Commands**

Open a new terminal or command prompt window. Navigate to the MongoDB bin directory by typing:
```bash
cd "C:\Program Files\MongoDB\Server\<version>\bin" (Windows)
```
or equivalent for your operating system.
Run the following command:
```bash
mongo
```
This will start the MongoDB shell, which is a JavaScript-based interface.

Now you're ready to play around with some basic commands:

* `show dbs` lists all available databases.
* `use <database_name>` selects a database (create one if it doesn't exist).
* `db` shows the current database name.
* `quit` exits the MongoDB shell.

Experiment with these commands and get familiar with the MongoDB shell.