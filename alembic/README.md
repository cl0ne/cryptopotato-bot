[SQLAlchemy Database connection URL](https://docs.sqlalchemy.org/en/13/core/engines.html#engine-configuration) specified directly in `alembic.ini` can be overridden with:

- `DB_URL` environment variable
- `db_url` [command line argument](https://alembic.sqlalchemy.org/en/latest/api/runtime.html#alembic.runtime.environment.EnvironmentContext.get_x_argument) of alembic tool specified with `-x` option, e.g.:

    ```
    alembic -x db_url=postgresql://user:pass@host/dbname upgrade head
    ```

Note that command line argument takes precedence over environment variable.
