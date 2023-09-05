from distutils.core import setup

setup(
    name="nlsql-api",
    packages=["nlsql_api"],
    version="0.0.4",
    description="Python client for NLSQL API",
    url="https://github.com/denissa4/nlsql-api",
    project_urls={
            "Source Code": "https://github.com/denissa4/nlsql-api",
            "Issue Tracker": "https://github.com/denissa4/nlsql-api/issues",
        },
    python_requires=">=3.7, <4",
    install_require={
        "requests": ["requests>=2.31.0, <3.0.0"],
        "pydantic": ["pydantic>=2.2.1, <3.0.0"]
    },
)