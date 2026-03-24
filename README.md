# Online Shopping System

This repository contains a database systems course project for a console-based online shopping platform built with `Python` and `SQLite`. The project models the core flow of a small e-commerce system, including customer login, product browsing, cart management, checkout, and purchase-history analysis.

## What the Project Covers

- customer login and validation
- product browsing by category
- shopping cart and order placement flow
- inventory updates during checkout
- purchase and customer analysis using the backing database

## Tech Stack

- `Python`
- `SQLite`
- file-based local database for rapid prototyping

## Repository Structure

- `Zapnit.py`: application logic for the shopping flow
- `SQLzapnit.py`: schema setup and database-side logic
- `my_database.db`: sample SQLite database used by the project
- `Online Shopping System.zip`: archived submission bundle from the original course project

## Running the Project

Make sure Python 3 is installed, then run:

```powershell
python Zapnit.py
```

If you want to inspect or rebuild the database setup logic, review:

```powershell
python SQLzapnit.py
```

## Design Notes

The project was built as an academic system design exercise, so the focus is on demonstrating relational modeling and end-to-end application flow rather than production deployment. The schema and scripts show how products, customers, carts, orders, reviews, payments, and transaction records can work together in a small database-backed commerce system.

## Contributors

- Arnav Batra
- Dikshant
- Snigdha

## Future Improvements

- move from a script-based interface to a simple web UI
- separate database setup from runtime application code
- add stronger input validation and error handling
- add tests for cart, checkout, and stock updates
