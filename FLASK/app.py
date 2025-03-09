from flask import Flask,redirect,render_template
app=Flask(__name__)

@app.route("/")
def sample():
    return "<h1>hey buddy</h1>"


# redirect
@app.route("/redirect")
def hello():
    return redirect("/")

#path param
@app.route("/path/<name>")
def path_param(name):
    return f"hello ,{name}"

@app.route("/home")
def home():
    return render_template("home.html",content=["AL","ML","DATASCIENCE"])


@app.route("/path1/<name>")
def path1(name):
    return f"this is {name}"

@app.route("/path2/<int:no>")
def path2(no):
    return f"this is {no}"










app.run(debug=True)
