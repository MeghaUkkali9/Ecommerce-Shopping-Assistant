# ShopMate AI – Ecommerce Shopping Assistant

## Project Description

I am building a full-fledged chatbot system for an ecommerce website.

This chatbot is designed specifically for the ShopMate AI website and acts as a virtual shopping assistant for users. It is integrated directly into the website UI, allowing users to interact with it in real time.

The system includes:

* A frontend chat interface where users can type their queries
* A backend system that processes user input
* An API that connects the frontend and backend
* Chatbot logic that generates responses

The chatbot helps users with tasks such as searching for products, checking prices, exploring offers, and answering product-related queries on the website.

## What We Are Building

This project focuses on building an **Ecommerce Chatbot (Product Assistant)** where customers can ask questions and receive instant responses.

This chatbot acts as a virtual assistant for the website, helping users interact with the platform in a simple and conversational way.

## What Problem It Solves

* Helps users quickly find products without manually browsing
* Provides instant answers instead of waiting for customer support
* Improves user experience by guiding customers through the website
* Assists in decision-making (price comparison, reviews, offers)

## What Kind of Products It Supports

The chatbot can work for any ecommerce category, such as:

* Electronics (phones, laptops, accessories)
* Fashion (clothing, shoes)
* Groceries
* Home & kitchen products
* Beauty & personal care

It can be customized for any specific website or product catalog.

## Types of Queries It Can Answer

The chatbot can handle different types of user queries, including:

### Product Search

* "Show me laptops under ₹50,000"
* "Find running shoes for men"

### Price & Offers

* "What is the price of iPhone 13?"
* "Are there any discounts available?"

### Reviews & Recommendations

* "Is this product good?"
* "Which is the best phone under ₹30,000?"

### Order & General Queries (extendable)

* "Where is my order?"
* "What are the delivery charges?"

### General Assistance

* "Help me choose a product"
* "Suggest something for daily use"

## Tech Stack
(TODO)

## How It Works

1. User enters a query in the chatbot UI
2. The message is sent to the backend via an API endpoint
3. The backend processes the query using chatbot logic
4. A response is generated
5. The response is displayed back in the UI


## Why to Use Web Scraping

We use web scraping to fetch product data from ecommerce platforms so that the chatbot can use real product information to answer user queries.

This data is then stored and used by the chatbot to provide accurate and meaningful responses to user queries.

### Purpose

* To make the chatbot **data-driven** instead of rule-based
* To provide **real product information** rather than generic answers
* To enable **better recommendations and decision-making**

## SET-UP GUIDE

### Required Tools & Packages

Check if `uv` is installed:

```bash
uv --version
```

If not installed, run:

```bash
pip install uv
```

### Project Initialization

Create a new project:

```bash
uv init ecommerce-shopping-assistant
cd ecommerce-shopping-assistant
```

### Create Virtual Environment

Create a virtual environment with Python 3.10:

```bash
uv venv ecomassistant --python 3.10
```

Activate the environment:

```bash
source ecomassistant/bin/activate
```

### Clone GitHub Repository

Create a repository on GitHub, then link local project to Github repo :

```bash
git init
git remote add origin https://github.com/MeghaUkkali9/Ecommerce-Shopping-Assistant.git
```

To install packages under this project run:
```bash
uv pip install -r requirements.txt
```


To run scapper, streamlit is required
```bash
streamlit run scrapper_ui.py
```
