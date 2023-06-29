from flask import Flask,render_template,request,g,url_for,flash,session
from database import get_database
from werkzeug.utils import redirect
from werkzeug.security import generate_password_hash,check_password_hash
import sqlite3
import os
# Creating a Flask instance

app=Flask(__name__)
app.config['SECRET_KEY']=os.urandom(8)

# means we remove name associated with the user
@app.teardown_appcontext
def close_database(error):
    
    # if g has crudapplication_db set?
    if hasattr(g,'crudapplication_db'):   
        # close the connection
        g.crudapplication_db.close()

def get_current_user():
    '''This function checks wheather session's user var is set or not.If yes then we will retrieve the user details else not'''
    user=None 
    # checking if session's user variable is set or not
    if 'user' in session:
        # if true then extract it and store to user
        user=session['user']
        db=get_database()
        user_cur=db.execute('select * from EMPLOYEE where EMP_NAME = ?',[user])
        user=user_cur.fetchone()
    return user[1]


# setting up global variables

updateDepartmentFlag=None


def standardFormatter(*args):
    '''Function that takes in a variable length of arguments and return the formatted data'''

    # 'abc'->'Abc' or 'ABC'->'Abc'

    args=list(args)

    for i in range(len(args)):
        args[i]=args[i].title()

    args=tuple(args)    

    return args

# route for index page
@app.route("/")
def home():
    '''Function to render a template "index.html".'''
    return render_template("index.html")

# route for signup page
@app.route("/signup",methods=['GET','POST'])
def signup():
    '''Function to take user data from the form and check if it exists in database if not the register/signup the user.'''

    error=None
    # opening database connection
    db=get_database()

    if request.method=='POST':

        # extracting form details

        name=request.form['signupUsername']
        email=request.form['signupEmail']
        password=request.form['signupPassword']

        formattedData=standardFormatter(name)
        
        name=formattedData[0]
        
        # convert the password to hash code
        hashed_password=generate_password_hash(password)

        # checking if data with current details already exists?

        user_cursor=db.execute('Select * from EMPLOYEE where EMP_NAME=?',[name])
        
        existing_user_name=user_cursor.fetchone()

        # if exists issue an error
        if(existing_user_name):
            
            password_cursor=db.execute('Select PASSWORD from PASSWORD_DATA Where EMP_ID=?',[existing_user_name[0]])

            password_of_existing_user_flag=password_cursor.fetchone()

            if(password_of_existing_user_flag):
                error='Account already exists! Please login!'
                return render_template('signup.html',registerError=error)

            db.execute('INSERT INTO PASSWORD_DATA(PASSWORD,EMP_ID) VALUES(?,?)',[hashed_password,existing_user_name[0]])

            db.commit()

            return redirect(url_for('login'))
        
        # if not then insert it into 'EMPLOYEE' 
        db.execute('Insert into EMPLOYEE(EMP_NAME,EMAIL) values(?,?)',[name,email])

        stored_emp_id_cursor=db.execute('Select EMP_ID from EMPLOYEE Where EMP_NAME=?',[name])

        db.commit()

        stored_emp_id=stored_emp_id_cursor.fetchone()
        print(stored_emp_id[0])
        db.execute('INSERT into PASSWORD_DATA(EMP_ID,PASSWORD) VALUES(?,?)',[stored_emp_id[0],hashed_password])

        # commiting the transaction
        db.commit()

        return redirect(url_for('login'))

    return render_template("signup.html")

# route for login
@app.route("/login",methods=['GET','POST'])
def login():
    '''Function to check if user details are correct or not.If correct login will be successful.'''

    # opening database connection
    db=get_database()

    if request.method=='POST':

        # extracting form details
        
        username_or_email=request.form['loginUsernameEmail']
        userpassword=request.form['loginPassword']

        # checking db with current username/email
        
        emp_cur_obj=db.execute('Select * from EMPLOYEE WHERE EMP_NAME=? or EMAIL=?',[username_or_email,username_or_email])

        current=emp_cur_obj.fetchone()
        
        # if the record exits in db
        if current:
            
            password_cur=db.execute('Select PASSWORD From PASSWORD_DATA Where EMP_ID=?',[current['EMP_ID']])

            password_data=password_cur.fetchone()
            
            if current['EMP_NAME']==username_or_email or current['EMAIL']==username_or_email and check_password_hash(password_data,userpassword):

                # if it matches then:
                
                # create a session and set up user with user_name col 
                session['user']=current['EMP_NAME']

                # checking wheather it is admin or employee
                # if its admin render->admin dashboard
                if(current['ADMIN_FLAG']==1):
                    return redirect(url_for("adminDashboard"))
            
                # else render employee dashboard
                return redirect(url_for("employeeDashboard"))
            # here we are checking wheather the user have inserted username or email

            # in either case check for both
            if current['EMP_NAME']!=username_or_email:
                if current['EMAIL']!=username_or_email:
                    return render_template('login.html',login_error="Username/email does'nt exist!Please Signup!")

            # password check(invalid password)
            elif(not check_password_hash(password_data,userpassword)):
                return render_template('login.html',login_error="Enter a valid password!")

            
        # if there is no record in db
        return render_template("login.html",login_error='Signup Before Login!')
    
    # default
    return render_template("login.html")

# route for about
@app.route("/about")
def about():
    return render_template("about.html")

# route for adminDashboard
@app.route("/adminDashboard",methods=['GET'])
def adminDashboard():
    '''Function to render a template "adminDashboard.html" '''
    current_user=get_current_user()
    
    return render_template("adminDashboard.html",current_user=current_user)

# route for department
@app.route("/department")
def department():
    '''Function to display the records in "DEPARTMENT".'''
    
    current_user=get_current_user()
    
    # opening database connection
    db=get_database()

    # creating a cursor to hold data extracted from 'DEPARTMENT'
    dept_cur=db.execute('Select * from DEPARTMENT')

    # storing the data into dept_data
    dept_data=dept_cur.fetchall()

    return render_template("department.html",dept_data=dept_data,current_user=current_user)

# route for deleteDept
@app.route("/deleteDept/<int:DEPT_ID>",methods=['GET','POST'])
def deleteDept(DEPT_ID):
    '''Function to remove the record in "DEPARTMENT" with "DEPT_ID"="DEPT_ID".'''

    current_user=get_current_user()

    if request.method=='GET':
        
        # opening database connection
        db=get_database()

        # removing the record with 'DEPT_ID' = DEPT_ID
        db.execute('Delete from DEPARTMENT where DEPT_ID=?',[DEPT_ID])

        # committing into db
        db.commit()

        return redirect(url_for('department'))

    return render_template("department.html",current_user=current_user)

# route for updateDept1
@app.route("/updateDept1/<int:DEPT_ID>",methods=['GET','POST'])
def updateDept1(DEPT_ID):
    '''Function to set the status of global variable "updateDepartmentFlag" and render template updateDepartment.html'''

    current_user=get_current_user()

    if request.method=='GET':
        # using global variable 'updateDepartmentFlag'
        global updateDepartmentFlag

        # setting it to DEPT_ID
        updateDepartmentFlag=DEPT_ID

        return render_template("updateDepartment.html")   
    
    return render_template("updateDepartment.html",current_user=current_user)

# route for updateDept2
@app.route("/updateDept2",methods=['GET','POST'])
def updateDept2():
    '''Function to update the department name.'''

    current_user=get_current_user()


    global updateDepartmentFlag
    if request.method=='POST':
        db=get_database()

        updateDeptName=request.form['updated_deptname']

        formattedData=standardFormatter(updateDeptName)
        updateDeptName=formattedData[0]
        
        db.execute('Update DEPARTMENT Set DEPT_NAME=? Where DEPT_ID=?',[updateDeptName,updateDepartmentFlag])

        updateDepartmentFlag=None 

        db.commit()

        return redirect(url_for('department'))

    return render_template("updateEmployee.html",current_user=current_user)

# route for viewDepartment
@app.route("/viewDepartment")
def viewDepartment():
    return redirect(url_for('department'))

# route for add_dept
@app.route("/add_dept",methods=['GET','POST'])
def add_dept():

    current_user=get_current_user()

    db=get_database()

    if request.method=='POST':
        department_name=request.form['deptname']

        formattedData=standardFormatter(department_name)
        department_name=formattedData[0]

        db_cursor=db.execute('Select * from DEPARTMENT where DEPT_NAME=?',[department_name])

        current_data=db_cursor.fetchone()

        if current_data:
            return render_template("addDepartment.html",dept_error='Department already exists!')
        
        else:
            db.execute('Insert into DEPARTMENT(DEPT_NAME) values(?)',[department_name])

            db.commit()

            return render_template("addDepartment.html",dept_message='Department added successfully!')

    return render_template("addDepartment.html",current_user=get_current_user())

# route for employee
@app.route("/employee")
def employee():

    current_user=get_current_user()

    db=get_database()
    
    emp_cursor=db.execute("Select * from EMPLOYEE")
    
    employee_data=emp_cursor.fetchall()

    db.commit()

    return render_template("employee.html",employee_data=employee_data,current_user=get_current_user()) 

# route for viewEmployee
@app.route("/viewEmployee")
def viewEmployee():
    return redirect(url_for("employee")) 

# route for add_employee
@app.route("/add_employee",methods=['GET','POST'])
def add_employee():

    current_user=get_current_user()

    if request.method=='POST':    
        db=get_database()

        emp_name=request.form['empname']
        gender=request.form['gender']
        date_of_birth=request.form['dob']
        emp_email=request.form['email']
        emp_phone=request.form['phone']
        emp_department=request.form['department']
        emp_designation=request.form['designation']
        emp_address=request.form['address']
        emp_ctc=request.form['ctc']
        
        formattedData=standardFormatter(emp_name,gender,emp_designation,emp_address)
    
        emp_name=formattedData[0]
        gender=formattedData[1]
        emp_designation=formattedData[2]
        emp_address=formattedData[3]


        data_of_dept_id=db.execute('Select DEPT_ID from DEPARTMENT Where DEPT_NAME=?',[emp_department])
       
        emp_department=data_of_dept_id.fetchone()
        emp_department=emp_department[0]
        db.commit()

        add_emp_cursor=db.execute('Select * from EMPLOYEE Where EMP_NAME=?',[emp_name])
        
        stored_emp_details=add_emp_cursor.fetchone()
        
        db.commit()

        if stored_emp_details:
            
            error=f"Employee with {emp_name} already exists!If you want are trying to insert new employee please try with different name!"

            flash(error,"error")
            return redirect(url_for("addEmployee"))

        db.execute('Insert into EMPLOYEE(EMP_NAME,GENDER,DOB,EMAIL,PHONE,DEPT_ID,DESIGNATION,EMP_ADDRESS,CTC) Values (?,?,?,?,?,?,?,?,?)',[emp_name,gender,date_of_birth,emp_email,emp_phone,emp_department,emp_designation,emp_address,emp_ctc])

        db.commit()

        return (url_for("employee"))
    
    db=get_database()

    dept_data_cursor=db.execute('Select DEPT_NAME from DEPARTMENT')
    stored_dept=dept_data_cursor.fetchall()

    db.commit()
    return render_template('addEmployee.html',dept_data=stored_dept,current_user=current_user())
  

@app.route("/delete_Employee/<int:EMP_ID>")
def delete_Employee(EMP_ID):

    current_user=get_current_user()

    if request.method=='GET':
        
        db=get_database()

        db.execute('Delete from EMPLOYEE where EMP_ID=?',[EMP_ID])

        db.execute('Delete from PASSWORD_DATA where EMP_ID=?',[EMP_ID])

        db.commit()

        return redirect(url_for("employee"))


    return render_template("employee.html",current_user=current_user)

@app.route("/viewFullProfileOfEmp/<int:EMP_ID>")
def viewFullProfileOfEmp(EMP_ID):
    
    current_user=get_current_user()

    db=get_database()

    emp_cursor=db.execute('Select * from EMPLOYEE Where EMP_ID=?',[EMP_ID])
    
    stored_emp_complete_details=emp_cursor.fetchone()

    return render_template('viewFullProfile.html',data=stored_emp_complete_details,current_user=current_user)

# route for add_salary
@app.route("/add_salary")    
def add_salary():
    return render_template("addSalary.html")

# route for employeeDashboard
@app.route("/employeeDashboard")
def employeeDashboard():
    return render_template("employeeDashboard.html")

# route for employeeLeaves
@app.route("/employeeLeaves")
def employeeLeaves():
    return render_template("employeeLeaves.html")

# route for salaryHistory
@app.route("/salaryHistory")
def salaryHistory():
    return render_template("salaryHistory.html")


if __name__=="__main__":

    # running Flask instance
    
    app.run(debug=True)