from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nlp2cmd",
    version="0.1.0",
    author="Softreck",
    author_email="info@softreck.com",
    description="NLP-driven automation framework for converting natural language to commands, configs, and code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/softreck/nlp2cmd",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "sentencepiece>=0.1.99",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "jinja2>=3.1.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
    },
)
