# Project Description

I am building a full-fledged chatbot system for an ecommerce website.

This chatbot is designed specifically for  ShopMate AI website and will act as a virtual shopping assistant for users. It will be integrated directly into the website UI, allowing users to interact with it in real time.

The system includes:

* A frontend chat interface where users can type their queries
* A backend system that processes user input
* An API that connects the frontend and backend
* Chatbot logic that generates responses

The chatbot will help users with tasks like searching for products, checking prices, exploring offers, and answering general queries related to the website.

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

