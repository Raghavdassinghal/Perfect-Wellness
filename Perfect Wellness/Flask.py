from flask import Flask,render_template,request,make_response,session
from flask import redirect,url_for
import pymysql as sql
import smtplib,ssl,requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import http.client


app = Flask(__name__)
app.secret_key = "hfiejjfoijepijepijoiejowlkmsknjdnoejpipwjojoiji"

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/login/")
def login():
    if session.get("islogin"):
        return render_template("login.html")
    return render_template("home.html")

@app.route("/signup/")
def signup():
    if request.cookies.get("islogin"):
        return render_template("afterlogin.html")
    return render_template("signup.html")

@app.route("/aftersignup/",methods=["POST","GET"])
def aftersignup():
    if request.method == "POST":
        firstname = request.form.get("fname")
        lastname = request.form.get("lname","Null")
        email = request.form.get("email")
        password = request.form.get("passwd")
        cpassword = request.form.get("cpasswd")
        mobile = request.form.get("mobile") 
        if password == cpassword:
            try:
                db = sql.connect(host="localhost",port=3306,user="root",password="",database="customers")
                cur = db.cursor()
                cmd = f"select email from user where email='{email}'"
                cur.execute(cmd)
                data = cur.fetchone()  
                if data:
                    error = "Email already exist.....Enter new email"
                    return render_template("signup.html",error=error)
                else:
                    s = 0
                    l = 0
                    u = 0
                    n = 0
                    if len(password) >= 8:
                        for i in password:
                            if i.isupper():
                                u += 1
                            if i.islower():
                                l += 1
                            if i in ["@","#","*","%","$","^","&"]:
                                s += 1
                            if i.isnumeric():
                                n += 1
                        else:
                            if s>=1 and l>=1 and u>=1 and n>=1:
                                from_email = "perfectwellness7181@gmail.com"
                                to_email = email
                                p = 'perfectwellness@123'
                                message = MIMEMultipart("alternative")
                                message["Subject"] = "Mail for your account activation"
                                message["To"] = to_email
                                message["From"] = from_email
                                html = """
                                    <h1 style='color:red'>Your activation link is as follows</h1>
                                    <a href="localhost/activate/">Click on this link to activate your account<a>
                                    """
                                msg = MIMEText(html,"html")
                                message.attach(msg)
                                context = ssl.create_default_context()
                                with smtplib.SMTP_SSL("smtp.gmail.com",465,context=context) as server:
                                    server.login(from_email,p)
                                    server.sendmail(from_email,to_email,message.as_string())
                                    session['firstname'] = firstname
                                    session['lastname'] = lastname
                                    session['email'] = email
                                    session['password'] = password
                                    session['cpassword'] = cpassword
                                    session['mobile'] = mobile
                                return render_template("home.html")
                            else:
                                error = "Password does not match the conditions"
                                return render_template("signup.html",error=error)
                    else:
                        error = "Password must be of 8 characters long"
                        return render_template("signup.html",error=error)
            except Exception as e:
                return f"{e}"
        else:
            return render_template("signup.html")



    
@app.route("/afterlogin/",methods=["GET","POST"])
def afterlogin():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("passwd")  
        try:
            db = sql.connect(host="localhost",port=3306,user="root",password="",database="customers")
            cmd = f"select * from user where email='{email}'"
            cur = db.cursor()
            cur.execute(cmd)
            data = cur.fetchone()
            if data:
                #print(data)
                if password == data[3]:
                    session['email'] = email
                    session['islogin'] = "true"
                    return render_template("afterlogin.html")
                else:
                    error = "Invalid password!!!!!"
                    return render_template("login.html",error=error)
            else:
                #email does not exist
                error = "Invalid email"
                return render_template("login.html",error=error)
        except Exception as e:
            return f"{e}"
    else:
        return render_template("login.html")


@app.route("/nutrients/",methods=['GET','POST'])
def calories():
    if request.method == "GET":
        return render_template("try.html")
    elif request.method == "POST":
        food = request.form.get("food")
        querystring = {"ingr":f"{food}"}
        api_key = "ed5a02d727msh803fdfa8466b440p1fd778jsn6401716cdce0"
        url = f"https://edamam-food-and-grocery-database.p.rapidapi.com/parser?q={food}&appid={api_key}"
        headers = {
            'x-rapidapi-host': "edamam-food-and-grocery-database.p.rapidapi.com",
            'x-rapidapi-key': "ed5a02d727msh803fdfa8466b440p1fd778jsn6401716cdce0"
            }

        response = requests.request("GET", url, headers=headers, params=querystring)
        if response.status_code == 200:
            data = response.json()
            text = data['text']
            energy = data['hints'][0]['food']['nutrients']['ENERC_KCAL']
            protein = data['hints'][0]['food']['nutrients']['PROCNT']
            fat = data['hints'][0]['food']['nutrients']['FAT']
            carbohydrate = data['hints'][0]['food']['nutrients']['CHOCDF']
            fibre = data['hints'][0]['food']['nutrients']['FIBTG']
            category = data['hints'][0]['food']['category']
            category_label = data['hints'][0]['food']['categoryLabel']
            nut = {
                "Name" : text,
                "Energy" : energy,
                "Protein" : protein,
                "Fat" : fat,
                "Carbohydrates" : carbohydrate,
                "Fibre" : fibre,
                "Category" : category,
                "Category Name" : category_label
                }
            return render_template("try.html",data=nut)


@app.route("/bmi/")
def bmi():
    if request.method == "GET":
        return render_template("bmi.html")
    elif request.method == "POST":
        age = request.form.get("age")
        weight = request.form.get("weight")
        height = request.form.get("height")
        conn = http.client.HTTPSConnection("fitness-calculator.p.rapidapi.com")
        headers = {
            'x-rapidapi-host': "fitness-calculator.p.rapidapi.com",
            'x-rapidapi-key': "ed5a02d727msh803fdfa8466b440p1fd778jsn6401716cdce0"
            }

        conn.request("GET", f"/bmi?age={age}&height={height}&weight={weight}", headers=headers)
        res = conn.getresponse()
        print(res.status_code)
        if res.status_code == 200:
            data = res.json()
            f = data.decode("utf-8")
            f = json.loads(f)
            bmi = f['bmi']
            health = f['health']
            healthy_range = f['healthy_bmi_range']
            print(bmi)
        return render_template("bmi.html",bmi ,health ,healthy_range)




@app.route("/activate/")
def account_activate():
    try:
        firstname = session.get('firstname')
        lastname = session.get('lastname')
        email = session.get('email')
        password = session.get('password')
        cpassword = session.get('cpassword')
        mobile = session.get('mobile')
        db = sql.connect(host="localhost",port=3306,user="root",password="",database="customers")
        cursor = db.cursor()
        cmd = f"insert into user values('{firstname}','{lastname}','{email}','{password}','{cpassword}','{mobile}')"
        cursor.execute(cmd)
        db.commit()
        del session['firstname']
        del session['lastname']
        del session['email']
        del session['password']
        del session['cpassword']
        del session['mobile']
        error = "Login to continue....."
        return render_template("login.html",error=error)
    except Exception as e:
        return f"{e}"



@app.route("/admin/")
def admin():
    return render_template("admin.html")


@app.route("/diseases/")
def diseases():
    return render_template("diseases.html")

@app.route("/days/")
def days():
    return render_template("days.html")

@app.route("/fever/")
def fever():
    return render_template("fever.html")

@app.route("/fevers/")
def fevers():
    return render_template("fevers.html")

@app.route("/anemia/")
def anemia():
    return render_template("anemia.html")

@app.route("/anemias/")
def anemias():
    return render_template("anemias.html")

@app.route("/bp/")
def bp():
    return render_template("bp.html")

@app.route("/bps/")
def bps():
    return render_template("bps.html")

@app.route("/constipation/")
def constipation():
    return render_template("constipation.html")

@app.route("/constipations/")
def constipations():
    return render_template("constipations.html")


@app.route("/cold/")
def cold():
    return render_template("cold.html")

@app.route("/colds/")
def colds():
    return render_template("colds.html")

@app.route("/headache/")
def headache():
    return render_template("headache.html")

@app.route("/headaches/")
def headaches():
    return render_template("headaches.html")

@app.route("/wloss/")
def wloss():
    return render_template("wloss.html")

@app.route("/wgain/")
def wgain():
    return render_template("wgain.html")


@app.route("/exwloss/")
def exwloss():
    return render_template("exwloss.html")

@app.route("/exwgain/")
def exwgain():
    return render_template("exwgain.html")


@app.route("/dietwloss/")
def dietwloss():
    return render_template("dietwloss.html")

@app.route("/dietwgain/")
def dietwgain():
    return render_template("dietwgain.html")


@app.route("/tipwloss/")
def tipwloss():
    return render_template("tipwloss.html")

@app.route("/tipwgain/")
def tipwgain():
    return render_template("tipwgain.html")

@app.route("/logout/")
def logout():
    return render_template("login.html")


    
app.run(host="localhost",port=80,debug=True)