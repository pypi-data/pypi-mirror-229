from setuptools import setup, find_packages

setup(
    name="chatstream",
    version="0.3.0",
    author="Qualiteg",
    author_email="qualiteger@qualiteg.com",
    description="A streaming chat toolkit for pre-trained large language models(LLM)",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/qualiteg/ChatStream",
    packages=find_packages(exclude=["tests.*", "tests", "example.*", "example", "doc", "doc.*"]),
    tests_require=["pytest", "pytest-asyncio", "pytest-cov", "httpx","aiohttp"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "transformers",
        "torch",
        "fastapi",
        "fastsession",
        "tokflow",
        "loadtime>=1.0.6"
    ]
)
