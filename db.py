import flask_sqlalchemy

database = flask_sqlalchemy.SQLAlchemy()


class BlogPost(database.Model):
    __tablename__ = "blogposts"

    post_id = database.Column(database.Integer, primary_key=True)
    author = database.Column(database.String)
    content = database.Column(database.Text)
    timestamp = database.Column(database.DateTime, nullable=False)
    edit_timestamp = database.Column(database.DateTime)

    def as_dict(self):
        return {
            "id": self.post_id,
            "author": self.author,
            "content": self.content,
            "timestamp": self.timestamp,
            "edit_timestamp": self.edit_timestamp
        }
