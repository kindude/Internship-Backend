import os
from pathlib import Path
from dotenv import load_dotenv
from alembic import *
from logging.config import fileConfig
from alembic.util import CommandError
from sqlalchemy import engine_from_config, MetaData
from sqlalchemy import pool

sys.path.append(str(Path(__file__).resolve().parents[1]))

# Add the 'app' folder to sys.path
from app.models.Models import User, Company, Quiz, Question, Option
from app.models.BaseModel import Base


# Load environment variables from .env file
load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata




def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = os.getenv("DB_PATH")

    if not url:
        raise ValueError("DB_PATH environment variable is not set")

    config.set_main_option("sqlalchemy.url", url)

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    url = os.getenv("DB_PATH")

    if not url:
        raise ValueError("DB_PATH environment variable is not set")

    config.set_main_option("sqlalchemy.url", url)

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            try:
                context.run_migrations()
            except CommandError as e:
                if "Can't locate revision identified by" in str(e):
                    print(f'Migration error: {e}')
                else:
                    raise e


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
