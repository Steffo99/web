import enum
import flask_sqlalchemy

database = flask_sqlalchemy.SQLAlchemy()


class Privacy(enum.IntEnum):
    PUBLIC = 0
    UNLISTED = 1
    PRIVATE = 2


class BlogPost(database.Model):
    __tablename__ = "blogposts"

    post_id = database.Column(database.String, primary_key=True)
    author = database.Column(database.String, nullable=False)
    content = database.Column(database.Text, nullable=False)
    timestamp = database.Column(database.DateTime, nullable=False)
    privacy = database.Column(database.Enum(Privacy), nullable=False)

    def as_dict(self):
        return {
            "id": self.post_id,
            "author": self.author,
            "content": self.content,
            "timestamp": self.timestamp
        }


class Redirect(database.Model):
    __tablename__ = "redirects"

    redirect_key = database.Column(database.String, primary_key=True)
    redirect_to = database.Column(database.String)
