from chatbot import chatbot
from chatbot import trainer
from flask import Flask, render_template, redirect, request, session, flash
import mysql.connector
import secrets

# Create an instance of the Flask class, naming it "app"
app = Flask(__name__)
app.secret_key = secrets.token_hex()

# Database connectivity
conn = mysql.connector.connect(host="localhost", user="root", password="***********", database="chatbot")

cursor = conn.cursor()

# The route is "/", which means it is the root URL of the application.
# When a user visits this URL, the function below will be executed.
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home")
def home():
    if 'username' in session:
        cursor.execute("select firstname from user where email='" + session['username'] + "'")
        name = cursor.fetchall()
        return render_template("chatbot.html", message=name[0][0])
    else:
        return redirect("/")

@app.route("/adminpage")
def adminpage():
    if 'username' in session:
        return render_template("adminpage.html")
    else:
        return redirect("/")

@app.route("/login")
def login():
    return render_template("login1.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/forgot")
def forgot():
    return render_template("forgot.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

# Adds new user to the database
@app.route("/adduser", methods=['POST'])
def adduser():
    firstname = request.form["firstname"]
    lastname = request.form['lastname']
    email = request.form['email']
    password = request.form['password']
    cursor.execute("select * from user where email='" + email + "'")
    data = cursor.fetchall()
    if data:
        flash('Email ID already exists')
        return redirect("/signup")
    else:
        cursor.execute("insert into user (firstname, lastname, email, password) values ('" + firstname + "', '" + lastname + "', '" + email + "', '" + password + "')")
        conn.commit()
        flash("You have registered successfully. Please login to continue.")
        return redirect("/signup")
        # return "<p>" + "insert into user (firstname, lastname, email, password) values ('" + firstname + "', '" + lastname + "', '" + email + "', '" + password + "')" + "</p>"

# Login page authentication
@app.route("/verify", methods=['POST'])
def verify():
    username = request.form["username"]
    password = request.form["password"]
    cursor.execute("select * from user where email='" + username + "'")
    user = cursor.fetchall()
    if user and user[0][4] == password:
        session['username'] = username
        # flash('You were successfully logged in')
        return redirect("/home")
    else:
        flash('Invalid username or password')
        return redirect("/login")

# Login page authentication for Admin
@app.route("/verifyadmin", methods=['POST'])
def verifyadmin():
    username = request.form["username"]
    password = request.form["password"]
    cursor.execute("select * from admin where username='" + username + "'")
    admin = cursor.fetchall()
    if admin and admin[0][2] == password:
        session['username'] = username
        return redirect("/adminpage")
    else:
        flash("Invalid username or password")
        return redirect("/admin")

# Verifies Email in the database to change the password for forgotted user
@app.route("/verifyforgot", methods=['POST'])
def verifyforgot():
    email = request.form["email"]
    cursor.execute("select * from user where email='" + email + "'")
    user = cursor.fetchall()
    if user:
        return render_template("forgotpass.html", message=email)
    else:
        flash('Email ID not found')
        return redirect("/forgot")

# Updates the new password in the database
@app.route("/changepass", methods=['POST'])
def changepass():
    email = request.form["email"]
    password = request.form["password"]
    cursor.execute("update user set password='" + password + "' where email='" + email + "'")
    conn.commit()
    if cursor.rowcount:
        flash('Password changed successfully')
        return redirect("/forgot")
    else:
        flash('Password not updated. Please try again')
        return redirect("/verifyforgot")

# Stores the feedback in the database
@app.route("/feedback")
def feedback():
    if 'username' in session:
        feedback = request.args.get('feedvalue')
        cursor.execute("insert into feedback (email, feedback) values ('" + session['username'] + "', '" + feedback + "')")
        conn.commit()
        # flash('Feedback submitted successfully')
        return "Feedback submitted successfully"
    else:
        # flash('Feedback was not submitted, please login and try')
        return "Feedback was not submitted, please login and try"

# Gets the User's feedback from textbox
@app.route("/getfeedbacks")
def getfeedbacks():
    cursor.execute("select * from feedback")
    result = cursor.fetchall()
    data = []
    for i in result:
        data.append(list(i))
    return data

# Reads the training data for the chat bot
@app.route("/getchatdata")
def getchatdata():
    training_data = open("static/training_data.txt").read()
    return training_data

# Updates the training data and re-train the model when the Admin does any changes
@app.route("/updatechatdata")
def updatechatdata():
    chatdata = request.args.get('chatdata')
    f = open("static/training_data.txt", "w")
    f.write(chatdata)
    f.close()
    training_data = open("static/training_data.txt").read().splitlines()
    trainer.train(training_data)
    return "Saved successfully"

# Logs out the user or admin and terminates the session
@app.route("/logout")
def logout():
    session.pop('username')
    return redirect("/")

# Gets response from the chat bot for the user query
@app.route("/getresponse")
def get_bot_response():
    query = request.args.get('msg')
    return str(chatbot.get_response(query))

if __name__ == "__main__":
    # Create an instance of the Flask application.
    # The "app.run()" method starts the Flask development server.
    # It makes the application accessible via HTTP, allowing users to interact with it.
    app.run()
