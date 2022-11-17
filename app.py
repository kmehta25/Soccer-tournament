from logging import logProcesses
from re import match
import re
from flask import Flask,jsonify, session
from flask.scaffold import F
from flask_sqlalchemy import SQLAlchemy
from flask import render_template # to render our html page
from flask import request # to get user input from form
import hashlib # included in Python library, no need to install
import psycopg2
from psycopg2.extras import RealDictCursor, NamedTupleCursor
import datetime
import uuid

app=Flask(__name__)

t_host = "127.0.0.1"
t_port = "5432"
t_dbname = "postgres"
t_user = "postgres"
t_pw = "kunj0612"
db_conn = psycopg2.connect(host=t_host, port=t_port, dbname=t_dbname, user=t_user, password=t_pw)


@app.route('/', methods = ['GET'])
def index():
    if request.method =='GET':
        return render_template('index.html')


@app.route('/rank', methods = ['POST', 'GET'])
def rank():
    if request.method =='GET':
        s = "SELECT age_category, team_name, won, draw, lost, played, points FROM rank_table;"
        db_cursor = db_conn.cursor()
        db_cursor.execute(s)
        rankList = db_cursor.fetchall()

        for x in rankList:
            print("X is: " + str(x))

        db_cursor.close()

        return render_template('standings.html',rankList = rankList)
        

    if request.method == 'POST':
        form = request.form.to_dict()

        team_id = str(uuid.uuid4())
        team_name = form['team_name']
        age_category = form['age_category']
        # rank = form['rank']
        won = form['won']
        draw = form['draw']
        lost = form['lost']
        played = int(won) + int(draw) + int(lost)
        team_name = form['team_name']
        points = 3*int(won) + 1*int(draw) - 0*int(lost)

        db_cursor = db_conn.cursor()
        sp = 'INSERT INTO rank_table(team_id, age_category, won, draw, lost, played, points, team_name) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'
        db_cursor.execute(sp,(team_id, age_category, won, draw, lost, played, points, team_name))
        
        try:
            db_conn.commit()
        except psycopg2.Error as e:
            t_message = "Database error: " + e + "/n SQL: " + s
            return render_template("teamDirector_rankTeam.html", message = t_message)

        db_cursor.close()
        return "Points Updated Successfully"


@app.route('/addteam', methods = ['POST', 'GET'])
def addteam():

    if request.method =='GET':
        
        s = 'SELECT team_id, team_name, coach_name, players_name FROM team_info;'
        db_cursor = db_conn.cursor()
        db_cursor.execute(s)
        list = db_cursor.fetchall()

        for x in list:
            print("X is: " + str(x))

        db_cursor.close()

        return render_template('teamRegister.html')
        

    if request.method == 'POST':
        form = request.form.to_dict()

        team_id = str(uuid.uuid4())
        team_name = form['team_name']
        coach_name = form['coach_name']
        players_name = form ['players_name']
        poc_email = form['poc_email']
        poc_mob = form['poc_mob']
        poc_name = form['poc_name']
        approval_status = False

    
        db_cursor = db_conn.cursor()
        p = "SELECT team_name FROM team_info"
        db_cursor.execute(p)
        team_list=db_cursor.fetchall()
    

        for x in team_list:
            if(x[0] == team_name):
                return "Team already added! Please check!"
        if ((len(poc_name)!=0) and (len(poc_mob)!=0) and (len(poc_email)!=0)):
            s = 'INSERT INTO team_info(team_id,team_name,coach_name,players_name, poc_email,poc_mob,poc_name,approval_status) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)'
            db_cursor.execute(s,(team_id, team_name, coach_name,players_name, poc_email,poc_mob,poc_name,approval_status ))
        else:
            return "Please Check Point Of Contact Info. Missing info!!"

        try:
            db_conn.commit()
        except psycopg2.Error as e:
            t_message = "Database error: " + e + "/n SQL: " + s
            return render_template("teamDirector_addTeam.html", message = t_message)

        db_cursor.close()
        return "Team Added Successfully"


@app.route('/acceptteam', methods = ['PUT','GET'])
def accept():
    if request.method == 'PUT':
        db_cursor = db_conn.cursor()
        p = "SELECT team_name, approval_status FROM team_info"
        db_cursor.execute(p)
        team_list = db_cursor.fetchall()

        form = request.form.to_dict()        
        team_name = form['team_name']
        for x in team_list:
            if x[0] == team_name:
                approval_status = 'true'
                db_cursor.execute(("UPDATE team_info SET approval_status = %s WHERE team_name = %s"),(approval_status,team_name))
                try:
                    db_conn.commit()
                except psycopg2.Error as e:
                    t_message = "Database error: " + e + "/n SQL"
                    return render_template("teamDirector_addTeam.html", message = t_message)

        db_cursor.close()

        return "Team Approved Successfully!"
    if request.method == 'GET':
        db_cursor = db_conn.cursor()
        p1 = "SELECT team_name, approval_status FROM team_reg;"
        db_cursor.execute(p1)
        approvalList = db_cursor.fetchall()
        return render_template('teamRegistration.html', approvalList = approvalList)


@app.route('/logout', methods = ['POST','GET'])
def logout():
    if request.method == 'POST' or request.method == 'GET':
        # if 'username' in session:
        #     session.pop('username', None)

        return render_template('index.html')


@app.route('/addfield', methods = ['POST'])
def addField():
    form = request.form.to_dict()
    db_cursor = db_conn.cursor()

    # match_id = str(uuid.uuid4())
    # team_a = form['team_a']
    # team_b = form['team_b']

    field_id = str(uuid.uuid4())
    field_name = form['field_name']
    field_size1 = form['field_size1']
    field_size2 = form['field_size2']
    description = form['description']

    s = "INSERT INTO field_info(field_id, field_name, field_size1, field_size2, description) VALUES (%s, %s, %s, %s,%s);"

    db_cursor.execute(s,(field_id,field_name,field_size1,field_size2,description))

    try:
        db_conn.commit()
        field_details = db_cursor.fetchall()
        print("field values inserted: " + str(field_details))
    except psycopg2.Error as e:
        t_message = "Database error: " + str(e) + "/n SQL" + str(s)
    db_cursor.close()

    return "field value updated successfully!!"


@app.route('/assignreferee', methods = ['PUT','GET','POST'])
def assign():
    if request.method == 'GET':
        db_cursor = db_conn.cursor()
        p1 = "SELECT referee_id FROM referee_info;"
        db_cursor.execute(p1)
        refereeList = db_cursor.fetchall()
        return render_template('refereeDir_assignRefs.html', refereeList = refereeList)

    if request.method == 'PUT' or request.method == 'POST':
        form = request.form.to_dict()
        db_cursor = db_conn.cursor()
        p = "SELECT referee_id, match_id FROM referee_info;"

        db_cursor.execute(p)
        referee_list = db_cursor.fetchall()
        print(referee_list)

        referee_id = form['referee_id']
        print(referee_id)
        match_id = form['match_id']
        for x in referee_list:
            if x[0] == referee_id:
                db_cursor.execute(("UPDATE referee_info SET match_id = %s WHERE referee_id = %s"),(match_id,referee_id))
                try:
                    db_conn.commit()
                except psycopg2.Error as e:
                    t_message = "Database error: " + e + "/n SQL"
                    return render_template("teamDirector_addTeam.html", message = t_message)
        db_cursor.close()
        return "Referee assigned to match Successfully!"

@app.route('/displayreferee', methods = ['GET'])
def displayReferee():
    db_cursor = db_conn.cursor()
    p1 = "SELECT referee_id, referee_name, referee_gender, referee_qualification, approval_status FROM referee_info;"
    db_cursor.execute(p1)
    refereeList = db_cursor.fetchall()
    return render_template('refereeDir_login.html',refereeList = refereeList)


@app.route('/acceptreferee', methods = ['PUT'])
def acceptReferee():
    db_cursor = db_conn.cursor()
    
    p = "SELECT * FROM referee_info;"
    db_cursor.execute(p)
    referee_list = db_cursor.fetchall()
    
    # form = request.form.to_dict()
    
    referee_id = referee_list[0][0]
    print(referee_id)
    for x in referee_list:
        if x[0] == referee_id:
            approval_status = 'true'
            db_cursor.execute(("UPDATE referee_info SET approval_status = %s WHERE referee_id = %s"),(approval_status,referee_id))
            try:
                db_conn.commit()
            except psycopg2.Error as e:
                t_message = "Database error: " + e + "/n SQL"
                return render_template("teamDirector_addTeam.html", message = t_message)

    db_cursor.close()

    return "Referee Approved Successfully!"



@app.route('/login',methods=['POST','GET'])
def login():


    if request.method == 'GET':
        print("got request")
        return render_template('login.html')

    if request.method =='POST':
        print("code reached here")
        form = request.form.to_dict()
        db_cursor = db_conn.cursor() 
        username= form['email']
        s1 = "SELECT person_role from personnel_table where user_email ='"+ username+"'"
        db_cursor.execute(s1)
        person_role = db_cursor.fetchall()

        password = form['psw']
    
        
        s = "SELECT user_password FROM personnel_table WHERE user_email='"+ username+"'"
        db_cursor.execute(s)
        db_pass = db_cursor.fetchall()

        try:
            print(db_pass[0])
            if(password==db_pass[0][0]):
                print(password)
                print(db_pass[0][0])
                print(person_role[0][0])
                if person_role[0][0] == 'Field Director':
                    return render_template('fieldDir_login.html')
                if person_role[0][0] == 'Team Director':
                    return render_template('teamDirector.html')
                if person_role[0][0] == 'Volunteer Director':
                    return render_template('volunteerDirector.html')
                if person_role[0][0] == 'Referee Director':
                    return render_template('refereeDir_login.html')
                if person_role[0][0] == 'Tournament Director':
                    return render_template('tournamentDirector.html')
                #return "Login successful
            else:
                return "Incorrect username or password"
        except psycopg2.Error as e:
            t_message = "Database error: " + e + "/n SQL: " + s
            return render_template("register.html", message = t_message)


@app.route('/pendingreg', methods=['GET'])
def pending():
    if request.method == 'GET':
        db_cursor = db_conn.cursor()
        p1 = "SELECT team_name, approval_status FROM team_reg;"
        db_cursor.execute(p1)
        approvalList = db_cursor.fetchall()
        return render_template('teamRegistration.html', approvalList = approvalList)

@app.route('/addfields', methods=['GET'])
def addFields():
    if request.method == 'GET':
        return render_template('fieldDir_addFields.html')

@app.route('/maps', methods=['POST', 'GET'])
def maps_redirect():
    if request.method == 'POST' or request.method == 'GET':
        return render_template('fieldDir_addMaps.html')

@app.route('/getfixture', methods = ['GET'])
def getfix():
    return render_template('schedule.html')

@app.route('/about', methods = ['GET'])
def about():
    return render_template('about.html')

@app.route('/fixtures',methods=['POST','GET'])

def fixtures():
    if request.method == 'POST':
        db_cursor = db_conn.cursor()

        form = request.form.to_dict()

        match_id = str(uuid.uuid4())
        team_a = form['team_a']
        team_b = form['team_b']
        location = form['location']
        date_time = form['date_time']
        referee_id = form['referee_id']
        volunteer_id = form['volunteer_id']
        age_group = form['age_group']

        isTeamABooked = "SELECT team_a from fixtures WHERE team_a = '"+team_a+"' AND date_time = '"+date_time+"'"
        isTeamBBooked = "SELECT team_b from fixtures WHERE team_b = '"+team_b+"' AND date_time = '"+date_time+"'"
        isLocationBooked = "SELECT location from fixtures WHERE location = '"+location+"' AND date_time = '"+date_time+"'"
        isRefereeBooked = "SELECT referee_id from fixtures WHERE location = '"+referee_id+"' AND date_time = '"+date_time+"'"

        db_cursor.execute(isTeamABooked)
        l1 = db_cursor.fetchall()
        db_cursor.execute(isTeamBBooked)
        l2 = db_cursor.fetchall()
        db_cursor.execute(isLocationBooked)
        l3 = db_cursor.fetchall()
        db_cursor.execute(isRefereeBooked)
        l4 = db_cursor.fetchall()

        if l1 or l2 or l3 or l4:
            db_cursor.close()
            db_conn.close()
            return 'UNABLE TO SCHEDULE DUE TO CONFLICT'
            
        else:
            s = 'INSERT INTO fixtures(match_id,team_a,team_b,location,date_time,referee_id,volunteer_id,age_group) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)'
            db_cursor.execute(s,(match_id,team_a,team_b,location,date_time,referee_id,volunteer_id,age_group))
            db_conn.commit()
            db_cursor.close()
            db_conn.close()
            return 'MATCH SCHEDULED SUCCESSFULLY'

    if request.method == 'GET':
        s = "SELECT team_a, team_b, location, date_time FROM fixtures;"
        db_cursor = db_conn.cursor()
        db_cursor.execute(s)
        fixtureLists = db_cursor.fetchall()
        #return fixtureList

        print(fixtureLists)
        # for x in fixtureList:

        #     print(x)

        return render_template('fixtures.html', fixtureList = fixtureLists) 

@app.route('/trackvolunteer', methods = ['POST'])
def track_volunteer():
    db_cursor = db_conn.cursor()
    form = request.form.to_dict()

    volunteer_id = str(uuid.uuid4())
    volunteer_name = form['volunteer_name']
    host_team = form['host_team']
    away_team = form['away_team']
    match_id = form['match_id']
    time_volunteered = form['time_volunteered']
    amount = 15 * int(time_volunteered)

    s = 'INSERT INTO volunteer(volunteer_id,volunteer_name, host_team, away_team, match_id, time_volunteered, amount) VALUES(%s,%s,%s,%s,%s,%s,%s)'
    db_cursor.execute(s,(volunteer_id, volunteer_name,host_team, away_team, match_id, time_volunteered, amount))

    db_conn.commit()
    db_cursor.close()
    db_conn.close()

    return "volunteer hours added, host teams tracked and amount calculated!!"

@app.route('/volunteer',methods=['GET'])
def volunteer():
    s = "SELECT volunteer_name, host_team, away_team, time_volunteered, amount FROM volunteer;"
    db_cursor = db_conn.cursor()
    db_cursor.execute(s)
    volunteerList = db_cursor.fetchall()

    return render_template('volunteers.html', volunteerList = volunteerList)

@app.route('/editfaq', methods = ['POST','PUT'])
def edit():

    if request.method == 'POST':
        form = request.form.to_dict()
        faq_id = str(uuid.uuid4())
        query = form['query']
        db_curr = db_conn.cursor()
        s = 'INSERT INTO faq(faq_id,query) VALUES(%s,%s)'
        db_curr.execute(s,(faq_id,query))
        db_conn.commit()
        db_curr.close()
        
        return "query addedd"


    if request.method == 'PUT':
        form = request.form.to_dict()
        p = "SELECT faq_id, answer FROM faq"

        db_cursor = db_conn.cursor()
        db_cursor.execute(p)
        fList = db_cursor.fetchall()
        faq_id = form['faq_id']
        ans = form['answer']
        for x in fList:
            if x[0] == faq_id:
                db_cursor.execute(("UPDATE faq SET answer = %s WHERE faq_id = %s"),(ans,faq_id))
                db_conn.commit()
                return "answer addedd successfully"


@app.route('/location', methods = ['GET'])
def location():
    return render_template('location.html')

@app.route('/support', methods = ['GET'])
def support():
    return render_template('contact.html')

@app.route('/rules', methods = ['GET'])
def rules():
    return render_template('rules.html')

@app.route('/faq', methods = ['GET'])
def faq():
    s = "SELECT query, answer FROM faq"
    db_cursor = db_conn.cursor()
    db_cursor.execute(s)
    faqList = db_cursor.fetchall()
    return render_template('FAQ.html', faqList = faqList)

if __name__== "__main__":
    app.run(debug=True)

    