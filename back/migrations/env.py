from alembic import context

from app.db.session import engine
from app.models import Base

# URL comes from app settings (DATABASE_URL), not alembic.ini.
with engine.connect() as connection:
    # render_as_batch: lets future ALTERs work on SQLite (tests/E2E) too.
    context.configure(connection=connection, target_metadata=Base.metadata, render_as_batch=True)
    with context.begin_transaction():
        context.run_migrations()
