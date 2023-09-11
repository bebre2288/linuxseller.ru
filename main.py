#/usr/bin/python3
from flask import Flask, render_template, request, url_for, flash, redirect
import sqlite3
from waitress import serve

app = Flask(__name__)

@app.route("/stories/<storyid>")
def showStory(storyid: str):
    conn = sqlite3.connect('stories.db')
    c = conn.cursor()
    try:
        c.execute(f"SELECT * FROM STORIES where storyId==\"{storyid}\"")
    except:
        return render_template("error.html", error="sql request failed")
    storyData = c.fetchone()
    if storyData == None:
        return render_template("error.html", error=f"Could not load {storyid}, probably no such story exists")
    storyId = storyData[0]
    userLogin = storyData[1]
    storyName = storyData[2]
    storyText = storyData[3]
    dateTime = storyData[4]
    return render_template('story.html', userLogin=userLogin, dateTime=dateTime, storyName=storyName, storyText=storyText)

@app.route("/stories_index")
def showStoryIndex():
    storiesListHtml = []
    conn = sqlite3.connect('stories.db')
    c = conn.cursor()
    try:
        c.execute(f"SELECT * FROM STORIES")
    except:
        return render_template("error.html", error="fetching DB")
    for storyEntry in c.fetchall():
        storyId = storyEntry[0]
        userLogin = storyEntry[1]
        storyName = storyEntry[2]
        storyText = storyEntry[3]
        dateTime = storyEntry[4]
        storiesListHtml.append([storyId, storyName, userLogin])
    return render_template("storiesindex.html", storiesListHtml=storiesListHtml)

@app.route("/add_story/", methods=('GET', 'POST'))
def showAddStory():
    if request.method != 'POST':
        return render_template("addstory.html")
    storyName = request.form['storyName']
    storyText = request.form['storyText']
    login = request.form['login']
    password = request.form['password']
    if not storyName:
        return render_template("error.html", error='Title is required!')
    elif not storyText:
        return render_template("error.html", error='Story text is required!')
    elif not (password and login):
        return render_template("error.html", error='Login and passwords are required')
    ## adding 
    conn = sqlite3.connect('stories.db')
    c = conn.cursor()
    try:
        c.execute(f"select password from users where login=='{login}'")
    except:
        return render_template("error.html", error="could not load DB")
    req_res = c.fetchone()
    if req_res == None:
        return render_template("error.html", error="could not load DB")
    if req_res[0]!=password:
        return "Wrong passsword or user does not exist"

    
    #print(stmt)
    c.execute("INSERT INTO stories (userLogin, storyName, storyText) VALUES ( ? , ? , ? )", (login, storyName, storyText))
    conn.commit()
    return redirect(url_for("showStoryIndex"))

@app.route("/register/", methods=('GET', 'POST'))
def showRegister():
    if request.method != 'POST':
        return render_template("register.html")
    email = request.form['email']
    login = request.form['login']
    password = request.form['password']
    if not (password and login and email):
        return render_template("error.html", error='Login, passwords and email are required')
    ## adding 
    conn = sqlite3.connect('stories.db')
    c = conn.cursor()
    try:
        c.execute(f"select password from users where email==?", (email,))
    except:
        return render_template("error.html", error="could not load DB")
    req_res = c.fetchone()
    if req_res == None: # creating user
        c.execute("INSERT INTO users (login, password, email) VALUES ( ?, ?, ?)", (login, password, email))
        conn.commit()
        return redirect(url_for("showStoryIndex"))
    else: # balling out
        return render_template("error.html", error='This email already in use, or user with same name already exists')

@app.route("/")
def showIndex():
    return redirect(url_for("showStoryIndex"))

# stories DB row format
# +--------+-----+----------+----------+----------+
# |story id|login|story name|story text|date stamp|
# +--------+-----+----------+----------+----------+

# users DB row format
# +-------+--------+-----------+--------+------------+
# |user id|login 20|password 20|email 50|creationDate|
# +-------+--------+-----------+--------+------------+

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8080)


#CREATE TABLE stories ( storyId integer PRIMARY KEY , userLogin TEXT, storyName TEXT, storyText LONGTEXT, dateTime DATETIME DEFAULT CURRENT_TIMESTAMP );
