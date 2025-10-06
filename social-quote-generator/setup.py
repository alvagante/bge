from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bge-social-quote-generator",
    version="0.1.0",
    author="BGE Team",
    description="Automated quote image generator and social media publisher for BGE podcast",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/bge-social-quote-generator",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Graphics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Pillow>=10.0.0",
        "PyYAML>=6.0",
        "python-frontmatter>=1.0.0",
        "python-dotenv>=1.0.0",
        "tenacity>=8.2.0",
        "tweepy>=4.14.0",
        "instagrapi>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
            "types-PyYAML>=6.0.0",
            "types-Pillow>=10.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "bge-quote-gen=main:main",
        ],
    },
)
