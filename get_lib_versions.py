import importlib.metadata
packages = [
    "ipykernel",
    "python-dotenv",
    "langchain",
    "langchain-astradb",
    "langchain-core",
    "langchain-openai",
    "langchain-groq",
    "python-multipart",
    "fastapi",
    "streamlit",
    "uvicorn",
    "structlog",
    "beautifulsoup4",
    "html5lib",
    "jinja2",
    "lxml"
]
for pkg in packages:
    try:
        version = importlib.metadata.version(pkg)
        print(f"{pkg}=={version}")
    except importlib.metadata.PackageNotFoundError:
        print(f"{pkg} (not installed)")