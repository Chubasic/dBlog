from sqlalchemy import Table, Column, Integer, String, MetaData
users_metadata_obj = MetaData()

users = Table(
    "users",
    users_metadata_obj,
    Column("user_id", Integer, primary_key=True),
    Column("username", String(16), nullable=False),
    Column("email", String(60), key="email"),
    Column("password", String(18), nullable=False),
)