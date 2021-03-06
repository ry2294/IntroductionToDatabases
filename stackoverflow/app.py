from flask import Flask, render_template, request, redirect, url_for
from flask.ext.triangle import Triangle
import psycopg2
import json
import time
from datetime import date
from StringIO import StringIO

app = Flask(__name__)
Triangle(app)
conn = psycopg2.connect("dbname='ry2294' user='ry2294' password='VFGTHP' host='w4111db.eastus.cloudapp.azure.com'")

@app.route("/")
def indexHTML():
    return render_template('index.html')
    
@app.route("/auth",methods=['POST'])
def fbauth():
    global conn;
    content=request.get_json()["name"]
    sql='select * from users where name =%s;'
    print (sql)
    try:
        cur = conn.cursor()
        cur.execute(sql,[content])
        if(cur.fetchone()==None):
            sql = 'select max(userid) from users;'
            cur.execute(sql)
            userid=int(cur.fetchone()[0])+1
            today = date.today().isoformat()
            sql= ' insert into users values(%s,%s,%s);'
            cur.execute(sql,[userid,content,today])
            conn.commit()
        else:
            sql = 'select userid from users where name=%s;'
            cur.execute(sql,[content])
            userid=int(cur.fetchone()[0])
    except Exception as e:
        print e
    return str(userid)
    
@app.route("/search",methods=['POST'])
def search():
    global conn;
    if(request.method== 'POST'):
        content = request.get_json()["query"]
        print(content.lower())
        arg='%'+str(content.lower())+'%'
        sql = 'select * from questions where lower(title) like %s;'#%('%',content.lower(),'%')
        jsonArr=[]
        cur = conn.cursor()
        try:
            cur.execute(sql,[arg])
            rows=cur.fetchall()
            for row in rows:
                jsonOb={}
                jsonOb['questionid']=row[0]
                jsonOb['userid']=row[1]
                jsonOb['title']=row[3]
                jsonOb['body']=row[4]
                sqlnew='select tagname from tagged where questionid=%s;'
                curnew= conn.cursor()
                curnew.execute(sqlnew,[row[0]])
                result=curnew.fetchall()
                tags=[]
                for val in result:
                    tags.append(val[0])
                jsonOb['tags']=tags
                
                jsonArr.append(jsonOb)
        except Exception as e:
            print e
    return str(json.dumps(jsonArr))

@app.route("/question",methods=['POST'])
def questionSearch():
    global conn;
    if(request.method == 'POST'):
        content = request.get_json()["query"]
        print(content)
        sql = 'select * from answers a left outer join comments c on a.answerid=c.answerid where a.questionid=%s;'
        cur = conn.cursor()
        try:
            cur.execute(sql,[content])
            rows=cur.fetchall()
            jsonArr=[]
            ans={}
            for row in rows:
                answers={}
                comments=[]
                if(row[5]!=None):
                    # comments['answerid']=row[5]
                    # comments['userid']=row[6]
                    comments.append(row[8])
                if(row[0] not in ans):
                    answers['answerid']=row[0]
                    answers['questionid']=row[1]
                    answers['userid']=row[2]
                    answers['body']=row[4]
                    answers['comments']=comments
                    ans[row[0]]=answers
                else:
                    answers=ans[row[0]]
                    c=answers['comments']
                    c.extend(comments)
                    answers['comments']=c
                    ans[row[0]]=answers
        except Exception as e:
            print e
    return str(json.dumps(ans))
    
@app.route("/tags",methods=['POST'])
def getTags():
    global conn;
    sql='select * from tags'
    cur=conn.cursor()
    try:
        cur.execute(sql)
        rows=cur.fetchall()
        tags=[]
        for row in rows:
            tags.append(row[0])
    except Exception as e:
        print e
    return str(json.dumps(tags))

@app.route("/userinfo",methods=['POST'])
def getUserInfo():
    global conn;
    if(request.method== 'POST'):
        content = request.get_json()["username"]
        sql =' select * from users where lower(name)  =%s;'#%(content.lower())
        #sql='select * from users u left outer join userbadges b on u.userid=b.userid where lower(u.name) =\'%s\';'%(content.lower())
        userArr=[]
        cur = conn.cursor()
        try:
            cur.execute(sql,[content.lower()])
            rows=cur.fetchall()
            for row in rows:
                jsonOb={}
                jsonOb['userid']=row[0]
                jsonOb['name']=row[1]
                sqlnew='select b.badgename from users u left outer join userbadges b on u.userid=b.userid where u.userid=%s;'#%(row[0])
                curnew= conn.cursor()
                curnew.execute(sqlnew,[row[0]])
                result=curnew.fetchall()
                badges=[]
                for val in result:
                    badges.append(val[0])
                jsonOb['badges']=badges
                userArr.append(jsonOb)
        except Exception as e:
            print e
    print str(json.dumps(userArr))
    return str(json.dumps(userArr))
    
@app.route("/insertquestion",methods=['POST'])
def insertquestion():
    global conn;
    print(request.get_json())
    content = request.get_json()
    userid=content["userid"]
    title=content["title"]
    body=content["body"]
    tags=content["tags"]
    today = date.today().isoformat()
    sql='select max(questionid) from questions;'
    cur = conn.cursor()
    try:
        cur.execute(sql)
        res=cur.fetchone()
        questionid=int(res[0])+1
        sql='insert into questions values(%s,%s,%s,%s,%s);'#%(questionid,userid,today,title,body)
        cur.execute(sql,[questionid,userid,today,title,body])
        conn.commit()
        for  tag in tags:
            sql='insert into tagged values(%s,%s);'#%(questionid,tag)
            cur.execute(sql,[questionid,tag])
            conn.commit()
    except Exception as e:
        print(e)
    return "Successfully added to database"
    
@app.route("/insertanswer",methods=['POST'])
def insertAnswer():
    global conn;
    content = request.get_json()
    userid=content["userid"]
    questionid=content["questionid"]
    body=content["body"]
    today = date.today().isoformat()
    sql='select max(answerid) from answers'
    cur = conn.cursor()
    try:
        cur.execute(sql)
        res=cur.fetchone()
        answerid=int(res[0])+1
        sql='insert into answers values(%s,%s,%s,%s,%s);'#%(answerid,questionid,userid,today,body)
        print(sql)
        cur.execute(sql,[answerid,questionid,userid,today,body])
        conn.commit()
    except Exception as e:
        print(e)
    return "Successfully added answer to database"
    
@app.route("/insertcomment",methods=['POST'])
def insertComment():
    global conn;
    content = request.get_json()
    userid=content["userid"]
    answerid=content["answerid"]
    body=content["body"]
    today = date.today().isoformat() + ' ' +time.strftime("%H:%M:%S")
    sql='insert into comments values(%s,%s,%s,%s);'#%(answerid,userid,today,body)
    print (sql)
    cur = conn.cursor()
    try:
        cur.execute(sql,[answerid,userid,today,body])
        conn.commit()
    except Exception as e:
        print(e)
    return "Successfully added comment to database"
    
@app.route("/addbadge",methods=['POST'])
def addBadge():
    global conn;
    content = request.get_json()
    badge=content["badge"]
    userid=content["userid"]
    sql='insert into userbadges values(%s,%s);'#%(badge,userid);
    try:
        cur = conn.cursor()
        cur.execute(sql,[badge,userid])
        conn.commit()
    except Exception as e:
        print(e)
    return "Successfully added badge to database"

@app.route("/removebadge",methods=['POST'])
def removeBadge():
    global conn;
    content = request.get_json()
    badge=content["badge"]
    userid=content["userid"]
    sql='delete from userbadges where badgename = \'%s\' and userid=%s;'%(badge,userid);
    try:
        cur = conn.cursor()
        cur.execute(sql,[badge,userid])
        conn.commit()
    except Exception as e:
        print(e)
    return "Successfully removed badge from database"

    
@app.route("/login.html")
def loginHTML():
    return render_template('login.html')

@app.route("/search.html")
def searchHTML():
    return render_template('search.html')

@app.route("/question.html")
def questionHTML():
    return render_template('question.html')

@app.route("/createQuestion.html")
def createQuestionHTML():
    return render_template('createQuestion.html')

@app.route("/admin.html")
def adminHTML():
    return render_template('admin.html')

if __name__ == "__main__":
    conn = psycopg2.connect("dbname='ry2294' user='ry2294' password='VFGTHP' host='w4111db.eastus.cloudapp.azure.com'")
    import click
    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using
            python server.py
        Show the help text using
            python server.py --help
        """
    
        HOST, PORT = host, port
        print "running on %s:%d" % (HOST, PORT)
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)
    run()
