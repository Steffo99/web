import flask as f
import db
import datetime
# noinspection PyUnresolvedReferences
import configuration
import subtitles

app = f.Flask(__name__)
app.config.from_object("configuration.Config")
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
db.database.init_app(app)

if not (app.config.get("POST_USERNAME") and app.config.get("POST_PASSWORD")):
    raise Exception("No username or password set.")


def is_steffo(username, password):
    # who cares about encrypting, i don't reuse passwords anyways
    correct_username = app.config["POST_USERNAME"]
    correct_password = app.config["POST_PASSWORD"]
    return username == correct_username and password == correct_password


@app.before_request
def pre_request():
    f.g.subtitle = subtitles.generate_title()


@app.route("/")
def page_home():
    now = datetime.datetime.now()
    page = f.request.args.get("page", 0)
    blogposts = db.BlogPost.query \
                           .filter(db.BlogPost.timestamp <= now) \
                           .order_by(db.BlogPost.timestamp.desc()) \
                           .limit(10) \
                           .offset(page * 10) \
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


@app.route("/goto/<key>")
def page_goto(key: str):
    goto: db.Redirect = db.Redirect.query.filter(db.Redirect.redirect_key == key).first_or_404()
    if goto.redirect_to is None:
        f.abort(404)
        return
    return f.redirect(goto.redirect_to)


@app.route("/admin")
def page_admin():
    auth = f.request.authorization
    if not auth or not is_steffo(auth.username, auth.password):
        return "Please insert Steffo's Password.", 401, {"WWW-Authenticate": 'Basic realm="You are entering Steffo\'s Realm. Please enter his password."'}
    page = f.request.args.get("page", 0)
    blogposts = db.BlogPost.query \
                           .order_by(db.BlogPost.timestamp.desc()) \
                           .limit(10) \
                           .offset(page * 10) \
                           .all()
    return f.render_template("admin.html",
                             blogposts=blogposts,
                             admin=True,
                             username=auth.username,
                             password=auth.password)


@app.route("/api/blog", methods=["GET", "POST", "PUT", "DELETE"])
def api_blog():
    if f.request.method == "POST":
        # New post
        # Check password
        if not is_steffo(f.request.form.get("username", ""), f.request.form.get("password", "")):
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
        # Check password
        authenticated = is_steffo(f.request.form.get("username", ""), f.request.form.get("password", ""))
        # Get n posts from a certain timestamp and the number of previous posts
        now = datetime.datetime.now()
        time = f.request.args.get("time")
        limit = f.request.args.get("limit", 50)
        # Make the f.request
        query = db.BlogPost.query
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
        # Check password
        if not is_steffo(f.request.form.get("username", ""), f.request.form.get("password", "")):
            f.abort(403)
            return
        # Try to find the post to be edited
        post_id = f.request.form.get("post_id")
        if post_id is None:
            f.abort(400)
            return
        post = db.BlogPost.query.filter_by(post_id=post_id).first_or_404()
        # Get the new post contents
        content = f.request.form.get("content")
        if content is not None:
            post.content = content
        # Update the timestamp
        timestamp = f.request.form.get("timestamp")
        if timestamp is not None:
            post.timestamp = timestamp
        # Commit the updates
        db.database.session.commit()
        return f.jsonify(post.as_dict())
    elif f.request.method == "DELETE":
        # Delete post
        # Check password
        if not is_steffo(f.request.form.get("username", ""), f.request.form.get("password", "")):
            f.abort(403)
            return
        # Try to find the post to be deleted
        post_id = f.request.form.get("post_id")
        if post_id is None:
            f.abort(400)
            return
        post = db.BlogPost.query.filter_by(post_id=post_id).first_or_404()
        # Delete the post
        db.database.session.delete(post)
        db.database.session.commit()
    return "", 204


@app.after_request
def after_every_request(response):
    return response


if __name__ == "__main__":
    with app.app_context():
        db.database.create_all()
    app.run(debug=True)
