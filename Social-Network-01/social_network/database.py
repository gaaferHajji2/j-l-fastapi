import databases

import sqlalchemy

from social_network.config import config

metadata = sqlalchemy.MetaData()

### Create The Posts Table ###
posts_table = sqlalchemy.Table(
    "posts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String),
)

### Create The Comments Table ###
comments_table = sqlalchemy.Table(
    "comments",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String),
    # Here We Don't Need To Tell The Type Of Column, Because It's ForeignKey
    # So It Will Give It The Same Type Of Id Of Posts Table.
    sqlalchemy.Column("post_id", sqlalchemy.ForeignKey("posts.id"), nullable=False, ),
)

# connect_args={ "check_same_thread": False } --> This Only Required For Sqlite
engine = sqlalchemy.create_engine(
    url = config.DATABASE_URL, connect_args={ "check_same_thread": False }
)

# Tell The Engine To Use The MetaData Object
# So, When We Run The Code, All The Tables That Are Combine 
# With The metadata-object, Will Be Created
metadata.create_all(engine)

database = databases.Database(
    url=config.DATABASE_URL, force_rollback=config.DB_FORCE_ROLL_BACK
)