Generic single-database configuration with an async dbapi.

generate migration file

    $ alembic revision --autogenerate -m "all models"


upgrade database to last migration

    $ alembic upgrade head


for more information on alembic commands check this out [Alembic web site](https://alembic.sqlalchemy.org/en/latest/tutorial.html#)
