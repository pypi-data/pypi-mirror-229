import os

from setuptools import find_packages, setup

README_PATH = os.path.join(os.path.dirname(__file__), "README.md")

setup(
    name="django-fastapi-bridge",
    version="0.1-2",
    description="Build FastAPI app top of Django",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
    ],
    author="Marcin Nowak",
    author_email="marcin.j.nowak@gmail.com",
    url="https://gitlab.com/marcinjn/django-fastapi",
    keywords="web python django fastapi wrapper bridge",
    packages=find_packages("."),
    include_package_data=True,
    zip_safe=True,
    long_description=open(README_PATH).read(),
    long_description_content_type="text/markdown",
    license_files=("LICENSE.txt",),
)
