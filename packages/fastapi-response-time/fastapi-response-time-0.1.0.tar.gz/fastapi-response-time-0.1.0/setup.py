from setuptools import setup, find_packages

setup(
    name="fastapi-response-time",
    version="0.1.0",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=[
        "fastapi",
        "starlette"
    ],
    author="Raj Naik Dhulapkar",
    author_email="youremail@example.com",
    description="A FastAPI middleware to add X-Response-Time headers.",
    keywords="fastapi response time middleware",
    # if you plan to host it on GitHub
    url="https://github.com/RajNykDhulapkar/fastapi-response-time"
)
