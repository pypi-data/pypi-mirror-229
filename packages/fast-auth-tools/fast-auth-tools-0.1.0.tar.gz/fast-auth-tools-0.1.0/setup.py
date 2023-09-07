from setuptools import setup, find_packages

setup(
    name="fast-auth-tools",
    version="0.1.0",
    url="https://github.com/nihilok/auth_base",
    author="nihilok",
    author_email="",
    description="Simple Authentication Library for FastAPI",
    packages=find_packages(exclude=["main", "fast_auth.__tests__"]),
    install_requires=[
        "fastapi",
        "python-jose",
        "python-multipart",
        "passlib",
        "bcrypt",
        "aiosqlite",
    ],
)
