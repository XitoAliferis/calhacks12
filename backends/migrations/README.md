# Database Migrations

We use Alembic to evolve the SQLModel schema.

```bash
cd backends
uv run alembic revision --autogenerate -m "describe change"
uv run alembic upgrade head
```

The configuration reads the SQLModel metadata from `app.models`. Ensure the `.env` file points to the correct database before running migrations.
