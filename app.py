from flask import Flask,render_template,redirect,url_for,request,flash,session
import mysql.connector
from flask_wtf import FlaskForm
from flask_mail import Mail,Message
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField, IntegerField, DateField, DecimalField
from wtforms.validators import InputRequired, DataRequired, Email, ValidationError, Length, NumberRange
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'Rachit@123'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'rachitporwal554@gmail.com'
app.config['MAIL_PASSWORD'] = 'tzui pshx uoni rnsi'
app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = True
mail=Mail(app)

#MYSQL configuration
connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="dbms"
    )

def update_availability():
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    cur = connection.cursor()

    select_query = """
        SELECT V.VEHICLE_ID
        FROM BOOKING B
        INNER JOIN VEHICLE V ON B.VEHICLE_ID = V.VEHICLE_ID
        WHERE B.RENTAL_END_DATETIME = %s
    """
    cur.execute(select_query, (yesterday, ))
    vehicles_to_update = cur.fetchall()

    for vehicle_id in vehicles_to_update:
        update_query = """
            UPDATE VEHICLE
            SET AVAILABLE = TRUE
            WHERE VEHICLE_ID = %s
        """
        cur.execute(update_query, (vehicle_id, ))

    connection.commit()

    cur.close()

def validate_aadhaar(form, field):
    if not field.data.isdigit() or len(field.data) != 13:
        raise ValidationError("Aadhaar number must be 13 digits long and contain only numbers")

def validate_phone(form, field):
    if not field.data.isdigit() or len(field.data) != 10:
        raise ValidationError("Phone number must be 10 digits long and contain only numbers")

class SignUpForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={"placeholder": "Enter Name"})
    license = StringField('License Number', validators=[DataRequired()], render_kw={"placeholder": "Enter License Number"})
    adcard = StringField('Adhar Number', validators=[DataRequired(), Length(max=13), validate_aadhaar], render_kw={"placeholder": "Enter Adhar Number"})
    phno = StringField('Phone No', validators=[DataRequired(), Length(max=10), validate_phone], render_kw={"placeholder": "Enter Phone No"})
    emailid = StringField('Email Id', validators=[DataRequired(), Email()], render_kw={"placeholder": "Enter Email Id"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Enter Password"})

class SignInForm(FlaskForm):
   name = StringField('Name', validators=[DataRequired()], render_kw={"placeholder": "Enter Name"})
   emailid = StringField('Email_ID', validators=[DataRequired(),Email()], render_kw={"placeholder": "Enter Email Id"})
   password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Enter Password"})

class UserForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    emailid = StringField('Email_ID', validators=[InputRequired(), Email()])
    license = StringField('License', validators=[InputRequired()])
    adcard = StringField('Adhar Card', validators=[InputRequired(), Length(max=13), validate_aadhaar])
    phno = StringField('Phone No', validators=[InputRequired(), Length(max=10), validate_phone])
    age = IntegerField('Age')
    save = SubmitField('Save')

class FilterForm(FlaskForm):
    brand = SelectField('Select Brand', choices=[('','Select Brand', {'style': 'display: none;'}), ('Toyota', 'Toyota'), ('Honda', 'Honda'), ('Maruti', 'Maruti'), ('Kia', 'Kia'), ('Tata', 'Tata')], validators=[DataRequired()])
    bodytype = SelectField('Select Body Type', choices=[('','Select Body Type', {'style': 'display: none;'}), ('SUV', 'SUV'), ('Sedan', 'Sedan'), ('Hatchback', 'Hatchback')], validators=[DataRequired()])
    fueltype = SelectField('Select Fuel Type', choices=[('','Select Fuel Type', {'style': 'display: none;'}), ('Petrol', 'Petrol'), ('Diesel', 'Diesel'), ('CNG', 'CNG')], validators=[DataRequired()])
    fasttag = BooleanField('Fasttag')
    sunroof = BooleanField('Sun Roof')
    airbags = BooleanField('Air bags')
    apply = SubmitField('Apply')

class DatesForm(FlaskForm):
    location = StringField('Location', validators=[DataRequired()], render_kw={"placeholder": "Enter location"})
    pickup = DateField('Pick Up', validators=[DataRequired()], format='%Y-%m-%d', render_kw={"min": datetime.today().date()})
    return_date = DateField('Return Date', validators=[DataRequired()], format='%Y-%m-%d', render_kw={"min": datetime.today().date()})
    submit = SubmitField('Submit',validators=[DataRequired()],render_kw={"placeholder" : "Enter"})

class CarForm(FlaskForm):
    model = StringField('Model', validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=2017, max=2024)])
    licence_plate_number = StringField('Licence Plate Number', validators=[DataRequired()])
    body_type = StringField('Body Type', validators=[DataRequired()])
    fuel_type = StringField('Fuel Type', validators=[DataRequired()])
    mileage = DecimalField('Mileage', validators=[DataRequired()])
    puc = StringField('PUC', validators=[InputRequired()])
    insurance = StringField('Insurance', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    fasttag = BooleanField('FastTag')
    sunroof = BooleanField('Sunroof')
    airbags = BooleanField('Airbags')
    image = StringField('Image', validators=[DataRequired()])
    add = SubmitField("Add")

@app.route("/")
@app.route("/Home")
def home():
  return render_template("/users/home.html",check=session.get("current_id"))

@app.route("/About Us")
def aboutus():
  return render_template("/users/aboutus.html",check=session.get("current_id"))

@app.route("/Rent", methods=["POST","GET"])
def rent():
  form = FilterForm()
  dates = DatesForm()
  try:
    if session['check'] == 1:
      try:
        pickup_date_str = session['pickup_date']
        return_date_str = session['return_date']
        dates.location.data = session['location']
        dates.pickup.data = datetime.strptime(pickup_date_str, '%Y-%m-%d')
        dates.return_date.data = datetime.strptime(return_date_str, '%Y-%m-%d')
      except Exception as e:
        print(e)
  except Exception as e:
     print(e)
  if request.method == 'POST' and dates.validate():
    session["check"] = 1
    session['location'] = dates.location.data
    session['pickup_date'] = dates.pickup.data.strftime('%Y-%m-%d')
    session['return_date'] = dates.return_date.data.strftime('%Y-%m-%d')
    cur = connection.cursor()
    cur.execute("SELECT * FROM VEHICLE WHERE AVAILABLE = %s",(1,))
    session['car'] = cur.fetchall()
    cur.close()
  try:
    if session["check"]:
      if request.method == 'POST' and form.validate():
          brand = form.brand.data
          body_type = form.bodytype.data
          fuel_type = form.fueltype.data
          fasttag = form.fasttag.data
          sunroof = form.sunroof.data
          airbag = form.airbags.data
          cur = connection.cursor()
          query = '''
                  SELECT V.* 
                  FROM VEHICLE V
                  JOIN VEHICLE_FEATURES VF ON V.VEHICLE_ID = VF.VEHICLE_ID
                  WHERE V.MODEL LIKE %s 
                  AND V.BODY_TYPE = %s 
                  AND V.FUEL_TYPE = %s 
                  AND V.AVAILABLE = %s
              '''
          condition = ('%' + brand + '%', body_type, fuel_type, 1)

          if not (fasttag or sunroof or airbag):
            cur.execute(query, condition)
          else:
            if fasttag:
              query += 'AND VF.FASTTAG = %s '
              condition += (1,)
            if sunroof:
              query += 'AND VF.SUNROOF = %s '
              condition += (1,)
            if airbag:
              query += 'AND VF.AIRBAGS = %s '
              condition += (1,)
            cur.execute(query, condition)
          session['car'] = cur.fetchall()
          cur.close()
          print(session['car'])
      else:
         print("hello")
  except Exception as e:
    print(e,"hello")
  try:
    if session["car"] and session["check"]:
      return render_template("/users/rent.html",check=session.get("current_id"),form=form,date=dates,car=session['car'],carerror=session.get('check'))
    else:
      return render_template("/users/rent.html",check=session.get("current_id"),form=form,date=dates,car=[],carerror=session.get('check'))
  except:
    return render_template("/users/rent.html",check=session.get("current_id"),form=form,date=dates,car=[],carerror=session.get('check'))

@app.route("/How It Works")
def hiw():
  return render_template("/users/hiw.html",check=session.get("current_id"))

@app.route("/SignIn", methods=["GET", "POST"])
def signin():
  form = SignInForm()
  if request.method == 'POST' and form.validate():
    cur = connection.cursor()

    name = form.name.data
    emailid = form.emailid.data
    password = form.password.data

    cur.execute("SELECT * FROM USER WHERE NAME = %s AND EMAIL_ID = %s AND PASSWORD = %s", (name,emailid,password))
    user =  cur.fetchone()

    cur.close()

    if user:
      session["signinerror"] = False
      session["current_id"] = user[0]
      cur = connection.cursor()
      cur.execute('SELECT A.ADMIN_ID FROM ADMIN A INNER JOIN USER U ON A.USER_ID = U.USER_ID WHERE U.USER_ID = %s',(user[0],))
      temp = cur.fetchone()
      cur.close()
      if temp:
         session["admin_id"] = user[0]
         print(session["admin_id"])
         return redirect(url_for('admin'))
      return redirect(url_for('dash'))
    else:
       flash("No such user exist","info")
       session["signinerror"] = True
       return redirect(url_for('signin'))
  session.setdefault("signinerror",None)
  return render_template("/users/signin.html",form=form,sierror=session["signinerror"])

@app.route("/SignUp", methods=["GET", "POST"])
def signup():
    form = SignUpForm()
    if request.method == 'POST' and form.validate():
        
        cur = connection.cursor()

        name = form.name.data
        license = form.license.data
        adcard = form.adcard.data
        phno = form.phno.data
        emailid = form.emailid.data
        password = form.password.data

        cur.execute("SELECT * FROM USER WHERE NAME = %s OR EMAIL_ID = %s OR LICENSE = %s OR AADHAR_CARD = %s", (name, emailid, license, adcard))

        user = cur.fetchone()

        if user:
            flash(f"User already exists.", "info")
        else:
            cur.execute("INSERT INTO USER (NAME, LICENSE, AADHAR_CARD, PHONE_NUMBER, EMAIL_ID, PASSWORD) VALUES (%s, %s, %s, %s, %s, %s)",
                        (name, license, adcard, phno, emailid, password))
            connection.commit()
            cur.close()
            flash("Sign up successful.","info")
            return redirect(url_for("signin"))
    return render_template("/users/signup.html",form=form)

@app.route("/check_connection")
def check_connection():
    try:
        cur = connection.cursor()
        return "Connection to MySQL database is successful!"
    except Exception as e:
        print("Error:", e)
        return "Error: Unable to connect to MySQL database."

@app.route("/Dashboard", methods=["GET","POST"])
def dash():
  try:
    if(session["current_id"] != None):
      cur = connection.cursor()
      cur.execute("SELECT * FROM USER WHERE USER_ID = %s", (session["current_id"],) )
      user = cur.fetchone()
      form = UserForm()

      update_availability()

      cur.execute("SELECT V.MODEL AS Vehicle_Name, B.BOOKING_ID,B.RENTAL_START_DATETIME,B.RENTAL_END_DATETIME,B.RENT_COST,B.DROP_LOCATION,V.AVAILABLE AS AVAILABLE FROM BOOKING B INNER JOIN VEHICLE V ON B.VEHICLE_ID = V.VEHICLE_ID WHERE B.USER_ID = %s ORDER BY B.RENTAL_START_DATETIME DESC;", (session["current_id"],))
      booking = cur.fetchall()
      
      if booking:
        try:
          session.pop('location')
          session.pop('return_date')
          session.pop('pickup_date')
          session.pop('car')
        except Exception as e:
           print(e)

      if request.method == "POST" and form.validate():
        name = form.name.data
        emailid = form.emailid.data
        license = form.license.data
        adcard = form.adcard.data
        phno = form.phno.data
        age = form.age.data

        cur.execute("UPDATE USER SET NAME= %s , LICENSE = %s , AADHAR_CARD = %s, PHONE_NUMBER = %s, EMAIL_ID = %s, AGE = %s WHERE USER_ID = %s",(name,license,adcard,phno,emailid,age,session.get("current_id")))
        connection.commit()
        cur.close()
        flash("Profile Updated Successfully","info")
        return redirect(url_for('dash'))

      form.name.data = user[1]
      form.emailid.data = user[5]
      form.license.data = user[2]
      form.adcard.data = user[3]
      form.phno.data = user[4]
      form.age.data=user[6]
  except:
     return redirect(url_for("signin"))

  return render_template("/users/dashboard.html",form=form,user=user[1],booking=booking)

@app.route("/Billing", methods = ["GET","POST"])
def bill():
  try:
    fsa = ""
    pi = ""
    if session["vehicle_id"] and session["current_id"]:
      cur = connection.cursor()
      cur.execute('''
                    SELECT *
                    FROM VEHICLE V
                    JOIN VEHICLE_FEATURES VF ON V.VEHICLE_ID = VF.VEHICLE_ID
                    WHERE V.VEHICLE_ID = %s
                ''', (session.get('vehicle_id'),))
      vehicle = cur.fetchone()
      if vehicle[13]:
        fsa += "Yes/"
      else:
        fsa += "No/"
      if vehicle[14]:
        fsa += "Yes/"
      else:
        fsa += "No/"
      if vehicle[15]:
        fsa += "Yes"
      else:
        fsa += "No"
      if vehicle[7] == "Valid":
        pi += "Valid/"
      else:
        pi += "Not Valid/"
      if vehicle[8] == "Valid":
        pi += "Valid"
      else:
        pi += "Not Valid"
      pickup_date = datetime.strptime(session['pickup_date'], '%Y-%m-%d')
      return_date = datetime.strptime(session['return_date'], '%Y-%m-%d')
      days = (return_date - pickup_date).days
      price = vehicle[9]
      if days == 0:
         days = 1
         totalbill = price
      else:
         totalbill = days*price

      if request.method == 'POST':
        try:
          cur.execute("INSERT INTO BOOKING (VEHICLE_ID,USER_ID,RENTAL_START_DATETIME,RENTAL_END_DATETIME,RENT_COST,DROP_LOCATION) VALUES(%s,%s,%s,%s,%s,%s)",
                      (vehicle[0],session.get('current_id'),pickup_date,return_date,totalbill,session.get('location')))
          cur.execute("UPDATE VEHICLE SET AVAILABLE = FALSE WHERE VEHICLE_ID = %s",(vehicle[0],))
          connection.commit()
          cur.close()
        except Exception as e:
          print(e)
        try:
          cur = connection.cursor()
          cur.execute("SELECT * FROM USER WHERE USER_ID = %s",(session.get('current_id'),))
          user = cur.fetchone()
          sender ='noreply@ghumo.com'
          msg=Message('Greetings from Ghumo car rentals',sender=sender,recipients=[user[5]])
          msg.body = f"Hello {user[1]}, this is the confirmation mail to inform you that your car has been booked.\n\n\nPlease pay Rs{totalbill} using given link: 'PAYMENT_LINK'\n\n\n You will recieve your car as soon as your payment gets cleared.\n\n\nEnjoy your ride\nTHANK YOU!!!"
          mail.send(msg)
          cur.close()
        except Exception as e:
          print(e)
        return redirect(url_for('dash'))
      return render_template('/users/billing.html',img=vehicle[11],name=vehicle[1],year=vehicle[2],body_type=vehicle[4],fuel_type=vehicle[5],mileage=vehicle[6],license=vehicle[3],fsa=fsa,pi=pi,days=days,price=price,totalbill=totalbill)
  except Exception as e:
    try:
      if session['current_id']:
        flash("Re-enter your location and dates")
      else:
        flash("You aren't signed in.","error")
    except:
      flash("You aren't signed in.","error")
    return redirect(url_for('rent'))
     
@app.route("/button_clicked", methods=['POST'])
def button():
  session["vehicle_id"] = request.form["button_id"]
  return redirect(url_for('bill'))

@app.route("/admin")
def admin():
  try:
    if session["admin_id"]:
      cur = connection.cursor()
      cur.execute("SELECT * FROM USER WHERE USER_ID = %s", (session["current_id"],) )
      user = cur.fetchone()
      form = UserForm()
      form.name.data = user[1]
      form.emailid.data = user[5]
      form.license.data = user[2]
      form.adcard.data = user[3]
      form.phno.data = user[4]
      form.age.data=user[6]
      cur.execute("SELECT COUNT(VEHICLE_ID) FROM VEHICLE WHERE AVAILABLE = %s",(1,))
      available = int(cur.fetchone()[0])
      cur.execute("SELECT COUNT(VEHICLE_ID) FROM VEHICLE WHERE AVAILABLE = %s",(0,))
      not_available = int(cur.fetchone()[0])
      cur.execute("SELECT COUNT(USER_ID) FROM USER WHERE USER_ID <> %s",(session.get("admin_id"),))
      users = int(cur.fetchone()[0])
      cur.close()
      return render_template("/admins/admin.html",form=form,available=available,not_available=not_available,users=users)
    else:
      flash("Unauthorized Access","info")
      return redirect(url_for('home'))
    
  except:
    flash("Unauthorized Access","info")
    return redirect(url_for('home')) 

@app.route("/addvehicle", methods=['GET','POST'])
def addv():
  try:
    if session["admin_id"]:
      form = CarForm()
      if request.method == 'POST' and form.validate():
        model = form.model.data
        year = form.year.data
        licence_plate_number = form.licence_plate_number.data
        body_type = form.body_type.data
        fuel_type = form.fuel_type.data
        mileage = form.mileage.data
        puc = form.puc.data
        insurance = form.insurance.data
        price = form.price.data
        fasttag = form.fasttag.data
        sunroof = form.sunroof.data
        airbags = form.airbags.data
        image = form.image.data
        cur = connection.cursor()
        try:
          cur.execute("""
                          INSERT INTO VEHICLE 
                          (MODEL, YEAR, LICENCE_PLATE_NUMBER, BODY_TYPE, FUEL_TYPE, MILEAGE, PUC, INSURANCE, PRICE, AVAILABLE, IMAGE) 
                          VALUES 
                          (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                      """, (model, year, licence_plate_number, body_type, fuel_type, mileage, puc, insurance, price, True, image))
          connection.commit()
          cur.execute("SELECT * FROM VEHICLE WHERE LICENCE_PLATE_NUMBER = %s",(licence_plate_number,))
          vehicle_id = cur.fetchone()

          cur.execute("""
              INSERT INTO VEHICLE_FEATURES 
              (VEHICLE_ID, FASTTAG, SUNROOF, AIRBAGS) 
              VALUES 
              (%s, %s, %s, %s)
          """, (vehicle_id[0], fasttag, sunroof, airbags))
          session["error"] = 0
        except Exception as e:
          print(e)
          session["error"] = 1
          flash("Check Your Inputs","error")
          return redirect(url_for('addv'))
        connection.commit()
        flash("New Vechicle Added","info")
        cur.close()
        return redirect(url_for('addv'))
      return render_template("/admins/addvehicle.html",form=form)
    else:
      flash("Unauthorized Access","info")
      return redirect(url_for('home'))
  except:
    flash("Unauthorized Access","info")
    return redirect(url_for('home'))

@app.route("/Logout")
def logout():
  try:
    session.pop("current_id")
    try:
      if session["admin_id"]:
        session.pop("admin_id")
        print("Admin")
    except:
      print("Normal user")
    flash("You have been logged out.")
    return redirect(url_for('home'))
  except:
    flash("You haven't signed in.")
    return redirect(url_for('home'))

if __name__ == "__main__":
  app.run(debug=True)