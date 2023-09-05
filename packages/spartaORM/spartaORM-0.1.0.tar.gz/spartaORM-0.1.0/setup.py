from distutils.core import setup

setup(
    name="spartaORM",
    packages=["spartaORM"],
    version="0.1.0",
    license="MIT",
    description="Simple ORM for Sparta",
    author="Arun Kumar",
    author_email="arun.kumar@swimming.org.au",
    url="https://gitlab.com/arun-ak/sparta-database-orm",
    download_url="https://gitlab.com/arun-ak/sparta-database-orm/-/archive/0.1.0/sparta-database-orm-0.1.0.tar.gz",
    install_requires=["alembic", "sqlalchemy", "psycopg2"],
    classifiers=["Topic :: Software Development :: Build Tools",],
)
