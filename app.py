from flask import Flask, render_template, request, redirect, url_for, send_file
#from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from csv import writer

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
SCOPES = ['https://www.googleapis.com/auth/documents']

# The ID of a sample document.
DOCUMENT_ID = '1M9uOZ'


def update(data):
    """Shows basic usage of the Docs API.
    Prints the title of a sample document.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=63726)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('docs', 'v1', credentials=creds)

        # Retrieve the documents contents from the Docs service.
        document = service.documents().get(documentId=DOCUMENT_ID).execute()
        requests = [
         {
            'insertText': {
                'location': {
                    'index': 1
                },
                'text': data+"\n",
            }},
    ]
        result = service.documents().batchUpdate(
        documentId=DOCUMENT_ID, body={'requests': requests}).execute()
        print('The title of the document is: {}'.format(document.get('title')))
    except HttpError as err:
        print(err)
    





app = Flask(__name__)

#def data_write(data):
#    d = data.split(",")
#    with open("data.csv",'a', newline='') as dat:
#        writer_object = writer(dat)
#        writer_object.writerow(d)
#        dat.close()

@app.route('/',methods=['GET', 'POST'])
def entry():
    if request.method == 'POST':
        data=str(request.form['email'])
        return redirect(url_for("home",data=data))
    return render_template("index.html")


@app.route('/home/<data>', methods=['GET', 'POST'])
def home(data):
    degree_list = ["Bachelor", "Master", "Already Graduated"]
    if request.method == 'POST':
        data += "," + str(request.form['options']) + "," + str(request.form["degree_list"])
        return redirect(url_for("page1",data=data))
    return render_template("home.html",degree_list=degree_list)


@app.route('/page1/<data>', methods=['GET', 'POST'])
def page1(data):
    desc = "The Figure on the right is a simple gridworld problem where the agent has to navigate from the bottom left to the top right " \
           "(target) while evading traps, monsters, and a forest. The agent will be terminated when in a tile with a " \
           "trap or adjacent to the monster, and will be penalized when going into a forest. This task is failed " \
           "when the agent is terminated or when the agent cannot reach the target in 20 steps. The agent can act in " \
           "four ways: left, right, up, down and the agent needs to reach the target as quickly as possible. " \
           "This graph is also labeled with a human-understandable description about the different regions of the " \
           "graph at which an agent possibly can be located. "

    if request.method == 'POST':
        data += "," + str(request.form["options2"])
        return redirect(url_for("page2",data=data))
    return render_template("page1.html", figurename="Figure 1",ims="image1.png",describe=desc)

@app.route('/page2/<data>', methods=['GET', 'POST'])
def page2(data):
    if request.method == 'POST':
        data += "," + str(request.form["options2"])
        data += "," + str(request.form["options3"])
        data += "," + str(request.form["options4"])
        print(data)
        return redirect(url_for("page3",data=data))
    return render_template("page2.html", figurename="Figure 1",ims="image1.png",ims2="scenario.png")

@app.route('/page3/<data>',methods=["GET","POST"])
def page3(data):
    print(data)
    state = ["Select", "at the start", "Near the start or Leave the start", "In normal path or Near the goal"]
    directions = ["Select","up", "down", "left", "right"]

    if request.method == 'POST':
        data += "," + str(request.form["state"])
        data += "," + str(request.form["directions"])
        print(data)
        return redirect(url_for("page4", data=data))
    return render_template("page3.html",figurename="Figure 1",ims="image1.png",directions=directions,state=state)


@app.route('/page4/<data>', methods=["GET", "POST"])
def page4(data):
    # horrible code to choose image
    d = data.split(",")
    dir = d[-1].lower()
    state = d[-2].lower()
    states = ["Select", "at the start", "near the start or leave the start", "in normal path or near the goal"]
    s = states.index(state)
    choices = ["Start", "Leave", "Near"]
    img_page = "graphs/Grid_(" + choices[s - 1] + "," + dir + ").png"
    opt = [("up", "Start"), ("up","Leave"), ("right", "Near"), ("up","Near")]

    if (dir,choices[s-1]) in opt:
        img_page = "graphs/optimal_green/Grid_optimal("+choices[s-1]+","+dir+").png"
    line = "What if the agent moves " + dir + " starting from " + state + "?"

    if request.method == "POST":
        data += "," + str(request.form["options"])
        if str(request.form["options"]) == "No":
            data += "," + str(request.form["options2"])
        print(data)
        return redirect(url_for("page5", data=data))

    return render_template("page4.html", figurename=line, ims="image1.png", ims2=img_page)

@app.route('/page5/<data>', methods=["GET", "POST"])
def page5(data):

    #TODO needs functionality work bad
    d = data.split(",")
    d = d[1:]
    val = 2
    if len(d) > 11:
        val = 1
    if len(d) > 14:
        val = 0
    if request.method == "POST":
        if request.form.getlist('a')[0] == "Again":
            if val != 0:
                return redirect(url_for("page3", data=data))
            else:
                return redirect(url_for('finish', data=data))

        else:
            return redirect(url_for('finish', data=data))
    return render_template("page5.html", times=val)



@app.route('/done/<data>',methods=["GET","POST"])
def finish(data):
    if request.method == "POST":
        data += "," + request.form["options2"]
        data +="&"
        #data_write(data)
        update(data)
        return redirect(url_for('begin_mtn',data=data))
        # uncomment below to revert to prior functionality
        #update(data)
        #return redirect(url_for("entry"))

    return render_template('exit.html')

#@app.route('/download')
#def download():
#    return send_file("data.csv", as_attachment=True)




@app.route('/mtn/<data>',methods=["GET","POST"])
def begin_mtn(data):
    if request.method == 'POST':
        data +=  str(request.form["options2"])
        return redirect(url_for("mtn2",data=data))
    return render_template("mtncar/mtnpage1.html", figurename="Figure 1")

@app.route('/mtn2/<data>',methods=["GET","POST"])
def mtn2(data):
    if request.method == 'POST':
        data += "," + str(request.form["options2"])
        data += "," + str(request.form["options3"])
        data += "," + str(request.form["options4"])
        print(data)
        return redirect(url_for("mtn3",data=data))
    return render_template("mtncar/mtnpage2.html", figurename="Figure 1",ims="mountaincar.jpg",ims2="MC_optimal.png")


@app.route('/mtn3/<data>',methods=["GET","POST"])
def mtn3(data):
    print(data)
    state = ["Select", "at the bottom and moving right slowly", "on the left slope and moving left slowly", "high up on the left slope and moving left slowly", "on the right slope and moving right quickly"]
    directions = ["Select","accelerates left", "accelerates right", "does not accelerate"]

    if request.method == 'POST':
        data += "," + str(request.form["state"])
        data += "," + str(request.form["directions"])
        print(data)
        return redirect(url_for("mtn4", data=data))
    return render_template("mtncar/mtnpage3.html",figurename="Figure 1",ims="mountaincar.jpg",directions=directions,state=state)


@app.route('/mtn4/<data>', methods=["GET", "POST"])
def mtn4(data):
    #TODO: FIX THIS FOR MOUNTAIN CAR
    d = data.split(",")

    state = d[-2].lower() # entered state
    #list of the states
    states = ["Select", "at the bottom and moving right slowly", "on the left slope and moving left slowly", "high up on the left slope and moving left slowly", "on the right slope and moving right quickly"]
    #the index on states entered
    s = states.index(state)
    # conversion from entered value to useful data
    choices = ["Bottom", "Left", "High", "Right"]

    dir = d[-1].lower() # entered direction
    choices2 =  ["Select","accelerates left", "accelerates right", "does not accelerate"]

    the_directions = ["Select","left", "right", "No"]
    di = choices2.index(dir)
    img_page = "MC_(" + choices[s - 1] + "," + the_directions[di] + ").png"
    opt = [("Bottom", "No"), ("High","left"), ("High", "right"), ("Right","right"),("Right","left")]
    
    if (choices[s-1],the_directions[di]) not in opt:
        img_page = "optimal_mc(" + choices[s - 1] + "," + the_directions[di] + ").png"
        #img_page = "MC_optimal.png"
    line = "What if the agent moves " + dir + " starting from " + state + "?"

    if request.method == "POST":
        print(img_page)
        data += "," + str(request.form["options"])
        if str(request.form["options"]) == "No":
            data += "," + str(request.form["options2"])
        return redirect(url_for("mtn5", data=data))

    return render_template("mtncar/mtnpage4.html", figurename=line, ims="mountaincar.jpg", ims2=img_page)

@app.route('/mtnpage5/<data>', methods=["GET", "POST"])
def mtn5(data):
    # awful way to differentiate sections
    d1 = data.split("&")
    d = d1[1].split(",")
    val = 2
    if len(d) > 8:
        val = 1
    if len(d) > 11:
        val = 0
    print(len(d))
    if request.method == "POST":
        if request.form.getlist('a')[0] == "Again":
            if val != 0:
                return redirect(url_for("mtn3", data=data))
            else:
                return redirect(url_for('finish', data=data))

        else:
            return redirect(url_for('finish2', data=data))
    return render_template("mtncar/mtnpage5.html", times=val)



@app.route('/done2/<data>',methods=["GET","POST"])
def finish2(data):
    if request.method == "POST":
        data += "," + request.form["options2"]
        data+="^"
        update(data)
        return redirect(url_for("entry"))

    return render_template('exit.html')
