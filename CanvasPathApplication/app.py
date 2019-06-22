from flask import Flask, render_template, request, session, logging, url_for, redirect, flash
from sqlalchemy import  create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from passlib.hash import sha256_crypt, pbkdf2_sha256

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, table,select, text




Base = declarative_base()


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:thomas123@localhost/CanvasPath"
adb = SQLAlchemy(app)




engine = create_engine("mysql+pymysql://root:thomas123@localhost/CanvasPath",pool_recycle=3600)
db = scoped_session(sessionmaker(bind=engine))

#Home Page
currentuser= ""
teacherusername= ""
@app.route('/')
def home():
    return  render_template ("home.html")

#Student Login
@app.route("/login", methods= ["GET", "POST"])
def login():
    if request.method == "POST":
        global currentuser
        username = request.form.get("name")
        password = request.form.get("password")
        usernamedata= db.execute("SELECT Email FROM Students WHERE email=:email", {"email":username}).fetchone()
        passworddata = db.execute("SELECT Password FROM Students WHERE email=:email", {"email":username}).fetchone()
        currentuser = usernamedata

        if currentuser:
            currentuser=currentuser[0]

        if usernamedata is None:
            flash("No username","danger")
            return render_template("login.html")
        else:
            for password_data in passworddata:
                phash=sha256_crypt.hash(password_data)
                if sha256_crypt.verify(password,phash):
                    session["student"] = True
                    flash("You are now logged in", "success")
                    return redirect(url_for('test1'))
                else:
                    flash("Incorrect password","danger")
                    return render_template("login.html")
    return render_template("login.html")

#Student
@app.route("/test1")
def test1():
    course = db.execute("SELECT E.CourseId,E.SectionNo, C.CourseDescription, R.Email, R.office FROM Enrolls E, Course C, RawProfessor R where R.Teaching = C.courseId AND C.courseId= E.Courseid AND StudentEmail=:StudentEmail",{"StudentEmail":currentuser}).fetchall()
    return render_template("test1.html", value=course)


#Student Personal Information
@app.route("/personalinfo", methods= ["GET", "POST"])
def personalinfo():
    personal = db.execute("SELECT Email,Password,FullName,Age,Gender,Major,Street FROM Students where Email=:Email",{"Email":currentuser}).fetchall()
    if request.method == "POST":
        cpassword = request.form.get("cpassword")
        npassword = request.form.get("npassword")
        db.execute(text("Update Students  SET Password =:Password where Password =:Password"), ({"Password":npassword}, {"Password":cpassword}))
        flash("Password has been Updated","success")
        return (render_template("personalinfo.html", value=personal))
    return render_template("personalinfo.html", value=personal)


#Student Homework Assignment
@app.route ("/studentassignment")
def studentassignment():
    assignment = db.execute("SELECT  E.CourseID, E.SectionNo, H.HwNo, H.HwDetails FROM Enrolls E, Homework H where  H.CourseId = E.Courseid AND H.SectionNo = E.Sectionno AND E.StudentEmail=:StudentEmail",{"StudentEmail":currentuser}).fetchall()
    return render_template("studentassignment.html", value=assignment)


#Student Homework Grades
@app.route ("/studentgrade")
def studentgrade():
    grade = db.execute("SELECT G.courseid, G.SectionNo, G.HwNo, G.Grade FROM HomeworkGrades G where G.StudentEmail=:StudentEmail",{"StudentEmail":currentuser}).fetchall()
    return render_template("studentgrade.html", value=grade)

#Student  Exam Assignment
@app.route ("/studentexamassignment")
def studentexamassignment():
    assignment = db.execute("SELECT  E.CourseID, E.SectionNo, H.ExamNo, H.ExamDetails FROM Enrolls E, Exams H where  H.CourseId = E.Courseid AND H.SectionNo = E.Sectionno AND E.StudentEmail=:StudentEmail",{"StudentEmail":currentuser}).fetchall()
    return render_template("studentexamassignment.html", value=assignment)

#Student Exam Grades
@app.route ("/studentexamgrade")
def studentexamgrade():
    grade = db.execute("SELECT G.courseid, G.SectionNo, G.ExamNo, G.Grades FROM ExamGrades G where G.StudentEmail=:StudentEmail",{"StudentEmail":currentuser}).fetchall()
    return render_template("studentexamgrade.html", value=grade)




#Faculty Login
@app.route("/flogin", methods= ["GET", "POST"])
def flogin():
    if request.method == "POST":
        global teacherusername
        username = request.form.get("name")
        password = request.form.get("password")
        usernamedata= db.execute("SELECT Email FROM Professor WHERE email=:email", {"email":username}).fetchone()
        passworddata = db.execute("SELECT Password FROM Professor WHERE email=:email", {"email":username}).fetchone()
        teacherusername = username
        if usernamedata is None:
            flash("No username","danger")
            return render_template("flogin.html")
        else:
            for password_data in passworddata:
                phash=sha256_crypt.hash(password_data)
                if sha256_crypt.verify(password,phash):
                    session["faculty"] = True
                    flash("You are now logged in", "success")
                    return redirect(url_for('addassignment'))
                else:
                    flash("Incorrect password","danger")
                    return render_template("flogin.html")
    return render_template("flogin.html")

#Create Assignment-Homework
class AssignmentAdd(adb.Model):
    __tablename__ = 'Homework'
    CourseId = Column(String, primary_key=True)
    SectionNo = Column(Integer)
    HwNo = Column(Integer)
    HwDetails = Column(String)

    def __init__(self, CourseId, SectionNo, HwNo, HwDetails):
        self.CourseId = CourseId
        self.SectionNo = SectionNo
        self.HwNo = HwNo
        self.HwDetails = HwDetails


@app.route ("/facultyassignemnt",methods= ["GET", "POST"])
def addassignment():
    if request.method == 'POST':
        if not request.form['CourseId'] or not request.form['SectionNo'] or not request.form['HwNo'] or not request.form['HwDetails']:
            flash('Please enter all the fields', 'error')
        else:
            hwadd = AssignmentAdd(request.form['CourseId'], request.form['SectionNo'], request.form['HwNo'], request.form['HwDetails'])
            adb.session.add(hwadd)
            adb.session.commit()
            flash('Record was successfully added', "success")
            return redirect(url_for('addassignment'))
    return render_template("facultyassignment.html")


#Create Assignment-Exam
class ExamAdd(adb.Model):
    __tablename__ = 'Exams'
    CourseId = Column(String, primary_key=True)
    SectionNo = Column(Integer)
    ExamNo = Column(Integer)
    ExamDetails = Column(String)

    def __init__(self, CourseId, SectionNo, ExamNo, ExamDetails):
        self.CourseId = CourseId
        self.SectionNo = SectionNo
        self.ExamNo = ExamNo
        self.ExamDetails = ExamDetails


@app.route ("/facultyaddexam",methods= ["GET","POST"])
def addExam():
    if request.method == 'POST':
        if not request.form['CourseId'] or not request.form['SectionNo'] or not request.form['ExamNo'] or not request.form['ExamDetails']:
            flash('Please enter all the fields', 'error')
        else:
            examadd = ExamAdd(request.form['CourseId'], request.form['SectionNo'], request.form['ExamNo'], request.form['ExamDetails'])
            adb.session.add(examadd)
            adb.session.commit()
            flash('Record was successfully added', "success")
            return redirect(url_for('addExam'))
    return render_template("facultyaddexam.html")

@app.route ("/facultyhwgrade",methods= ["GET","POST"])
def viewhwgrade():
    grade = db.execute("SELECT distinct H.studentemail, H.Courseid, H.sectionno, H.Hwno, H.grade from HomeworkGrades H, Sections1 S, RawProfessor P where P.Teaching = H.courseId AND P.email=:Email order by H.sectionno",{"Email":teacherusername}).fetchall()
    return render_template("facultyhwgrade.html", value=grade)

@app.route ("/facultyexamgrade",methods= ["GET","POST"])
def viewexamgrade():
    grade = db.execute("select distinct H.studentemail, H.Courseid, H.sectionno, H.examno, H.grades from ExamGrades H, Sections1 S, RawProfessor P where P.Teaching = H.courseId AND P.email=:Email order by H.sectionno",{"Email":teacherusername}).fetchall()
    return render_template("facultyexamgrade.html", value=grade)


#Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("You are now logged out", "success")
    return redirect(url_for('home'))


#View Assignments



#Admin Login
@app.route("/adminlogin", methods= ["GET", "POST"])
def adminlogin():
    if request.method == "POST":
        username = request.form.get("email")
        password = request.form.get("password")
        usernamedata= db.execute("SELECT Email FROM Admin WHERE email=:email", {"email":username}).fetchone()
        passworddata = db.execute("SELECT Password FROM Admin WHERE email=:email", {"email":username}).fetchone()

        if usernamedata is None:
            flash("No username","danger")
            return render_template("adminlogin.html")
        else:
            for password_data in passworddata:
                phash=sha256_crypt.hash(password_data)
                if sha256_crypt.verify(password,phash):
                    session["admin"] = True
                    flash("You are now logged in", "success")
                    return redirect(url_for('addcourse'))
                else:
                    flash("Incorrect password","danger")
                    return render_template("adminlogin.html")
    return render_template("adminlogin.html")


#Admin Add Course
class Courseadd(adb.Model):
    __tablename__ = 'Course'
    CourseId = Column(String, primary_key=True)
    CourseName = Column(String)
    CourseDescription = Column(String)

    def __init__(self, CourseId, CourseName, CourseDescription):
        self.CourseId = CourseId
        self.CourseName = CourseName
        self.CourseDescription = CourseDescription

class Sectionadd(adb.Model):
    __tablename__ = 'Sections1'
    CourseId = Column(String, primary_key=True)
    SectionNo = Column(Integer, primary_key=True)
    SectionType= Column(String)
    Limit = Column(Integer)
    profid=  Column(String)

    def __init__(self, CourseId, SectionNo, SectionType,Limit,profid):
        self.CourseId = CourseId
        self.SectionNo = SectionNo
        self.SectionType = SectionType
        self.Limit = Limit
        self.profid = profid

@app.route("/adminaddcourse", methods= ["GET", "POST"])
def addcourse():
    if request.method == 'POST':
        if not request.form['CourseId'] or not request.form ['CourseName'] or not request.form['CourseDescription'] or not request.form ['SectionNo'] or not request.form['SectionType'] or not request.form['SectionLimit'] or not request.form['Professor']:
            flash('Please enter all the fields', 'error')
        else:
            Course = Courseadd(request.form['CourseId'],request.form ['CourseName'], request.form['CourseDescription'])
            adb.session.add(Course)
            adb.session.commit()
            Section = Sectionadd(request.form['CourseId'],request.form ['SectionNo'], request.form['SectionType'], request.form['SectionLimit'], request.form['Professor'])
            adb.session.add(Section)
            adb.session.commit()
            flash('Record was successfully added', "success")
            return redirect(url_for('addcourse'))
    return render_template("adminaddcourse.html")

@app.route("/adminremovecourse", methods= ["GET", "POST"])
def removecourse():
    if request.method == 'POST':
        if not request.form['CourseId']:
            flash('Please enter all the fields', 'error')
        else:
            Course1 = request.form['CourseId']
            Course=Courseadd.query.filter_by(CourseId=Course1).first()
            adb.session.delete(Course)
            adb.session.commit()
            flash('Record was successfully removed', "success")
            return redirect(url_for('removecourse'))
    return render_template("adminremovecourse.html")


if __name__ == "__main__":
    app.secret_key="123456nt"
    app.run(debug=True)

'''
Student
aan1394@lionstate.edu
hj0n3pp5

Faculty
bbu@lionstate.edu
wgqpqh2t
'''

