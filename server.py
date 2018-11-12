import flask as f
import db
import datetime
# noinspection PyUnresolvedReferences
import configuration
import subtitles

app = f.Flask(__name__)
app.config.from_object("configuration.Config")
db.database.init_app(app)


@app.before_request
def pre_request():
    f.g.subtitle = subtitles.generate_title()


@app.route("/")
def page_home():
    now = datetime.datetime.now()
    blogposts = db.BlogPost.query \
                           .filter(db.BlogPost.timestamp <= now) \
                           .order_by(db.BlogPost.timestamp.desc()) \
                           .limit(10) \
                           .all()
    return f.render_template("home.html", blogposts=blogposts)


@app.route("/blogpost/<int:i>")
def page_blogpost(i: int):
    now = datetime.datetime.now()
    blogpost = db.BlogPost.query \
                          .filter(db.BlogPost.timestamp <= now) \
                          .filter(db.BlogPost.post_id == i) \
                          .first_or_404()
    return f.render_template("post.html", blogpost=blogpost)



@app.route("/api/blog", methods=["GET", "POST", "PUT", "DELETE"])
def api_blog():
    if f.request.method == "POST":
        # New post
        # Get the correct password from the config; I don't care enough to bcrypt this
        correct_password = app.config.get("POST_PASSWORD")
        if correct_password is None:
            f.abort(500)
            return
        # Check password
        if f.request.form.get("password", "") != correct_password:
            f.abort(403)
            return
        # Get the current time
        timestamp = datetime.datetime.now()
        # Get the post content
        content = f.request.form.get("content")
        if content is None:
            f.abort(400)
            return
        # Create the new post
        post = db.BlogPost(author="Steffo",
                           content=content,
                           timestamp=timestamp)
        db.database.session.add(post)
        db.database.session.commit()
        return f.jsonify(post.as_dict())
    elif f.request.method == "GET":
        # Get post(s)
        # Get the correct password from the config
        correct_password = app.config.get("POST_PASSWORD")
        if correct_password is None:
            f.abort(500)
            return
        # Check password
        authenticated = (f.request.args.get("password", "") != correct_password)
        # Get n posts from a certain timestamp and the number of previous posts
        now = datetime.datetime.now()
        time = f.request.args.get("time")
        limit = f.request.args.get("limit", 50)
        # Make the f.request
        query = db.BlogPost.query()
        if not authenticated:
            # Hide hidden posts if not authenticated
            query = query.filter(db.BlogPost.timestamp <= now)
        if time is not None:
            # Hide all posts after the specified time
            query = query.filter(db.BlogPost.timestamp <= time)
        query = query.order_by(db.BlogPost.timestamp.desc())
        query = query.limit(limit)
        query = query.all()
        return f.jsonify([post.as_dict() for post in query])
    elif f.request.method == "PUT":
        # Edit post
        # Get the correct password from the config
        correct_password = app.config.get("POST_PASSWORD")
        if correct_password is None:
            f.abort(500)
            return
        # Check password
        if f.request.form.get("password", "") != correct_password:
            f.abort(403)
            return
        # Try to find the post to be edited
        post_id = f.request.form.get("post_id")
        if post_id is None:
            f.abort(400)
            return
        post = db.BlogPost.query().filter_by(post_id=post_id).one_or_404()
        # Get the new post contents
        content = f.request.form.get("content")
        if content is None:
            f.abort(400)
            return
        # Update the post
        post.content = content
        post.edit_timestamp = datetime.datetime.now()
        # Commit the updates
        db.database.session.commit()
        return f.jsonify(post.as_dict())
    elif f.request.method == "DELETE":
        # Delete post
        # Get the correct password from the config
        correct_password = app.config.get("POST_PASSWORD")
        if correct_password is None:
            f.abort(500)
            return
        # Check password
        if f.request.form.get("password", "") != correct_password:
            f.abort(403)
            return
        # Try to find the post to be deleted
        post_id = f.request.form.get("post_id")
        if post_id is None:
            f.abort(400)
            return
        post = db.BlogPost.query().filter_by(post_id=post_id).one_or_404()
        # Delete the post
        db.database.session.delete(post)
        db.database.session.commit()
    return "", 204


@app.after_request
def after_every_request(response):
    return response


if __name__ == "__main__":
    app.run()