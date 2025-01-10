from setuptools import setup, find_packages

setup(
    name="privacy_scanner",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "mypy>=1.0.0",
        ],
    },
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool to scan Android apps for privacy concerns using the Gravy Analytics dataset",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="privacy, android, security, data collection",
    url="https://github.com/yourusername/privacy-scanner",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
) 