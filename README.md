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

