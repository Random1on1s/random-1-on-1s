import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="random1on1",
    version="0.0.27",
    author="Quinn Winters",
    author_email="contact-me@qwinters.me",
    description="Discord bot to match people together for random 1 on 1s",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/random1on1s/random1on1s-bot",
    project_urls={
        "Bug Tracker": "https://github.com/random1on1s/random1on1s-bot/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(where="."),
    python_requires=">=3.6",
)
