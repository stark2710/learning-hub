---
title: "Collections and Databases"
module: "MongoDB Fundamentals"
domain: "MongoDB"
lesson_id: "collections-and-databases"
prev: "backend-mastery-mongodb-m1-l3-bson-documents-and-data-types"
next: "backend-mastery-mongodb-m2-crud-operations-and-queries"
duration: "~45 min"
---

```system_prompt
You have a deep understanding of both relational and document databases. You are now introducing the student to MongoDB, explaining why they might choose this technology for certain use cases.

For this lesson on Collections and Databases:
- Explain how collections relate to tables in SQL
- Discuss the concept of databases and how they differ from traditional RDBMSs
- Use analogies from their Java/Python background (e.g., dictionaries, JSON) to help them understand the concepts

Always respond in plain English.
```

## What You'll Learn

* The fundamental difference between collections and tables in SQL
* How MongoDB's concept of databases differs from traditional RDBMSs
* When to use collections and when to create new ones

---

## The Mental Model

Let's start by comparing how collections work in MongoDB to how tables work in SQL. In SQL, a table is a rigid structure that defines the schema for your data. Each row represents a single record, and each column represents a field or attribute of that record.

In contrast, MongoDB stores data as JSON-like documents within a collection. A collection is similar to a table in SQL, but it's much more flexible. You can create collections dynamically based on your application's needs.

Here's an analogy from their Java/Python background: think of collections like dictionaries or JSON objects. Each collection represents a unique key-value store where you can store and retrieve data.

### Document-Oriented Database

So, what makes MongoDB different from traditional relational databases? The answer lies in its document-oriented nature. In MongoDB, each document is self-contained and can have varying structures, unlike the rigid schema of relational tables.

Imagine you're building an e-commerce application that needs to store user information. With relational databases, you'd create a `users` table with columns for `name`, `email`, `address`, etc. But what if your users need different types of addresses (e.g., home and work)? You'd end up creating separate tables or using complex queries.

In MongoDB, you can store each user's information as a JSON-like document within the `users` collection. Each document can have varying fields for `name`, `email`, `home_address`, `work_address`, etc. This flexibility is what makes MongoDB attractive for modern applications that require dynamic data structures.

---

## How It Actually Works

Now, let's dive deeper into how collections work in MongoDB. A collection represents a group of related documents stored within the database.

Here's an example code snippet:
```python
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['mydatabase']
collection = db['users']

# Create a new document (user) and add it to the 'users' collection
new_user = {
    'name': 'John Doe',
    'email': 'john@example.com',
    'address': {'home': '123 Main St', 'work': '456 Office Bldg'}
}
collection.insert_one(new_user)

# Retrieve a specific document (user) from the 'users' collection
result = collection.find_one({'name': 'John Doe'})

print(result)
```

### What's Next?

In the next lesson, we'll explore CRUD operations and queries in MongoDB. You'll learn how to create, read, update, and delete documents within your collections.

---

## Practice

1. **Exercise:** Create a new collection called `products` with three documents:
	* `product_1`: {'name': 'Apple iPhone', 'price': 599}
	* `product_2`: {'name': 'Samsung TV', 'price': 899}
	* `product_3`: {'name': 'Nike Shoes', 'price': 199}
2. **Quiz Question:** What is the primary difference between collections in MongoDB and tables in SQL?
a) Collections are static, while tables are dynamic
b) Collections can store varying document structures, while tables have rigid schemas
c) Collections only store strings, while tables support various data types

---

## Study Notes

**Q:** How do I create a new collection in MongoDB?

**A:** You can use the `insert_many()` method or create a new document with the desired fields and insert it into the collection.

**Anticipated Question:** Can I store arrays of sub-documents within a single document?

**Answer:** Yes, you can store arrays of sub-documents using the array data type in MongoDB. For example: `{name: 'John', address: [{'street': '123 Main St'}, {'street': '456 Office Bldg'}]}`

---

I hope this meets your requirements!