from flask import Flask,render_template,request,g,url_for,flash,session
from database import get_database
from werkzeug.utils import redirect
from werkzeug.security import generate_password_hash,check_password_hash
import sqlite3
import os
from datetime import datetime

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
        user_cur=db.execute('SELECT * FROM employee WHERE empName = ?',[user])
        user=user_cur.fetchone()
        return user['empName']
    return user

def standardFormatter(*args):
    '''Function that takes in a variable length of arguments and return the formatted data'''

    # 'abc'->'Abc' or 'ABC'->'Abc'

    args=list(args)

    for i in range(len(args)):
        args[i]=args[i].title()

    args=tuple(args)    

    return args

# route for index page
@app.route("/",methods=['GET'])
def home():
    '''Function to render a template "index.html".'''
    return render_template("index.html")

# route for signup page
@app.route("/signup",methods=['GET','POST'])
def signup():
    '''Function to take user data FROM the form and check if it exists in database if not the register/signup the user.'''

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

        user_cursor=db.execute('SELECT * FROM employee WHERE empName=?',[name])
        
        existing_user_name=user_cursor.fetchone()

        # if exists then there are 2 possibilities 

        # 1-> admin would have added the employee without inserting the password

        # 2-> the user might already have a password as well

        if(existing_user_name):
            
            # checking wheather user has a password or not

            password_cursor=db.execute('SELECT passwordEmp FROM passwordData WHERE empId=?',[existing_user_name[0]])

            password_of_existing_user_flag=password_cursor.fetchone()

            # if password exists we can clearly say that user exists
            if(password_of_existing_user_flag):
                error='Account already exists! Please login!'
                return render_template('signup.html',registerError=error)

            # if password does'nt exist then we can say admin have inserted this data

            # so now user is signing up for first time so they can sign up by inserting the password
            db.execute('INSERT INTO passwordData(passwordEmp,empId) VALUES(?,?)',[hashed_password,existing_user_name[0]])

            db.commit()
            signupSuccess=f'{name} signed up successfully!Provide valid credetials for login!'
            
            flash(signupSuccess,"info")

            return redirect(url_for('login'))
        
        # if not then INSERT it INTO 'EMPLOYEE' 
        db.execute('INSERT INTO employee(empName,email) VALUES(?,?)',[name,email])

        # retrieve the inserted empId
        stored_empId_cursor=db.execute('SELECT empId FROM employee WHERE empName=?',[name])

        db.commit()

        stored_empId=stored_empId_cursor.fetchone()

        # use the empId to insert the password data

        db.execute('INSERT INTO passwordData(empId,passwordEmp) VALUES(?,?)',[stored_empId[0],hashed_password])

        # commiting the transaction
        db.commit()

        signupSuccess=f'{name} signed up successfully!Provide valid credetials for login!'
            
        flash(signupSuccess,"info")

        return redirect(url_for('login'))

    return render_template("signup.html")

# route for login
@app.route("/login",methods=['GET','POST'])
def login():
    '''Function to check if user details are correct or not.If correct login will be successful and Session will be created else not.'''

    # opening database connection
    db=get_database()

    if request.method=='POST':

        # extracting form details
        
        username_or_email=request.form['loginUsernameEmail']
        userpassword=request.form['loginPassword']

        # checking db with current username/email
        
        emp_cur_obj=db.execute('SELECT * FROM employee WHERE empName=? or email=?',[username_or_email,username_or_email])

        current=emp_cur_obj.fetchone()

        # if there is no record in db
        if current==None:
            return render_template("login.html",login_error='Signup Before Login!')
    
        
        # if the record exits in db
        if current['empId']:
            
            password_cur=db.execute('SELECT passwordEmp FROM passwordData WHERE empId=?',[current['empId']])

            passwordData=password_cur.fetchone()['passwordEmp']

            if (current['empName']==username_or_email or current['email']==username_or_email) and (check_password_hash(passwordData,userpassword)):
                # if it matches then:

                # create a session and set up user with user_name col 
                session['user']=current['empName']

                # checking wheather it is admin or employee
                # if its admin render->admin dashboard
                if(current['adminFlag']==1):
                    return redirect(url_for("adminDashboard"))
            
                # else render employee dashboard
                return redirect(url_for("employeeDashboard"))
            # here we are checking wheather the user have INSERTed username or email
            # in either case check for both

            if current['empName']!=username_or_email:
                if current['email']!=username_or_email:
                    return render_template('login.html',login_error="Username/email does'nt exist!Please Signup!")
            
            # password check(invalid password)
            return render_template('login.html',login_error="Enter a valid password!")    
        
    # default
    return render_template("login.html")

# route for about
@app.route("/about",methods=['GET'])
def about():
    return render_template("about.html")

# route for adminDashboard
@app.route("/adminDashboard",methods=['GET'])
def adminDashboard():
    '''Function to render a template "adminDashboard.html" '''
    current_user=get_current_user()
    
    return render_template("adminDashboard.html",current_user=current_user)

# route for department
@app.route("/department",methods=['GET'])
def department():
    '''Function to display the records in "DEPARTMENT".'''
    
    current_user=get_current_user()
    
    # opening database connection
    db=get_database()

    # creating a cursor to hold data extracted FROM 'DEPARTMENT'
    dept_cur=db.execute('SELECT deptId,deptName FROM department')

    # storing the data INTO dept_data
    dept_data=dept_cur.fetchall()

    return render_template("department.html",dept_data=dept_data,current_user=current_user)

# route for DELETEDept
@app.route("/deleteDept/<int:deptId>",methods=['GET','POST'])
def deleteDept(deptId):
    '''Function to remove the record in "DEPARTMENT" with "DEPT_ID"="DEPT_ID".'''

    current_user=get_current_user()

    if request.method=='GET':
        
        # opening database connection
        db=get_database()

        # removing the record with 'DEPT_ID' = DEPT_ID
        db.execute('DELETE FROM department WHERE deptId=?',[deptId])

        # committing INTO db
        db.commit()

        return redirect(url_for('department'))

    return render_template("department.html",current_user=current_user)

# route for updateDept1
@app.route("/updateDept1/<int:deptId>",methods=['GET','POST'])
def updateDept(deptId):
    '''Function to set the status of global variable "updateDepartmentFlag" and render template updateDepartment.html'''

    current_user=get_current_user()

    if request.method=='GET':

        return render_template("updateDepartment.html",current_user=current_user,deptId=deptId)   
    
    if request.method=='POST':
    
        db=get_database()

        updateDeptName=request.form['updated_deptname']

        formattedData=standardFormatter(updateDeptName)
        updateDeptName=formattedData[0]
        
        db.execute('UPDATE department SET deptName=? WHERE deptId=?',[updateDeptName,deptId])

        db.commit()

        return redirect(url_for('department'))
    
# route for viewDepartment
@app.route("/viewDepartment",methods=['GET'])
def viewDepartment():
    '''Function to view all the department.'''
    return redirect(url_for('department'))

# route for add_dept
@app.route("/add_dept",methods=['GET','POST'])
def add_dept():
    '''Function to insert new department into db.'''
    
    current_user=get_current_user()

    # opening a db connection
    db=get_database()

    # if user is submitting data
    if request.method=='POST':
        # extract form details
        department_name=request.form['deptname']

        formattedData=standardFormatter(department_name)
        department_name=formattedData[0]
        
        #check wheather it already exists 
        db_cursor=db.execute('SELECT * FROM department WHERE deptName=?',[department_name])

        current_data=db_cursor.fetchone()

        # if the return an error
        if current_data:
            
            dept_error='Department already exists!'
            
            flash(dept_error,"error")
            
            return render_template("addDepartment.html")
        
        # else insert the data to database
        else:
            db.execute('INSERT INTO department(deptName) VALUES(?)',[department_name])

            db.commit()

            dept_message='Department added successfully!'

            flash(dept_message,'info')
            return render_template("addDepartment.html")

    return render_template("addDepartment.html",current_user=get_current_user())

# route for employee
@app.route("/employee",methods=['GET'])
def employee():
    '''Function to fetch all employee records and display them accordingly.'''

    current_user=get_current_user()

    # opening a db connection
    db=get_database()
    
    # selecting the rows from employee
    emp_cursor=db.execute("SELECT * FROM employee")
    
    # storing the dat in employee_data
    employee_data=emp_cursor.fetchall()

    db.commit()

    return render_template("employee.html",employee_data=employee_data,current_user=current_user) 

# route for viewEmployee
@app.route("/viewEmployee",methods=['GET'])
def viewEmployee():
    '''Function that perform simliar action as that of employee().'''
    return redirect(url_for("employee")) 

# route for add_employee
@app.route("/add_employee",methods=['GET','POST'])
def add_employee():
    
    current_user=get_current_user()
    
    db=get_database()

    # if user submits the data 
    if request.method=='POST':    
        # open a database connection
        
        # extract data from form
        empName=request.form['empname']
        gender=request.form['gender']
        date_of_birth=request.form['dob']
        emp_email=request.form['email']
        emp_phone=request.form['phone']
        emp_department=request.form['department']
        emp_designation=request.form['designation']
        emp_address=request.form['address']
        emp_ctc=request.form['ctc']
        
        # format the extracted data
        formattedData=standardFormatter(empName,gender,emp_designation,emp_address)
    
        empName=formattedData[0]
        gender=formattedData[1]
        emp_designation=formattedData[2]
        emp_address=formattedData[3]

        # in form we take department of employee as text

        # but in database we are storing it as id

        # hence here we are doing dept_name->dept_id 
        data_of_dept_id=db.execute('SELECT deptId FROM department WHERE deptName=?',[emp_department])
       

        emp_department=data_of_dept_id.fetchone()
        emp_department=emp_department[0]
        db.commit()

        # check wheather employee already exists
        add_emp_cursor=db.execute('SELECT * FROM employee WHERE empName=?',[empName])
        
        stored_emp_details=add_emp_cursor.fetchone()
        
        db.commit()

        # if true then
        if stored_emp_details:
            
            error=f"Employee with {empName} already exists!If you want are trying to INSERT new employee please try with different name!"

            # set a flash that display the above error
            flash(error,"error")

            return redirect(url_for("add_employee"))

        # if not insert the data to database

        db.execute('INSERT INTO employee(empName,gender,dob,email,phone,deptId,designation,empAddress,ctc) VALUES (?,?,?,?,?,?,?,?,?)',[empName,gender,date_of_birth,emp_email,emp_phone,emp_department,emp_designation,emp_address,emp_ctc])

        db.commit()

        return redirect(url_for("employee"))
    
    # when it is GET then we need to display a template for the user in which we are dynamically sending department(set of options to choose) from the database
    
    dept_data_cursor=db.execute('SELECT deptName FROM department')
    stored_dept=dept_data_cursor.fetchall()
    
    db.commit()

    # sending department details
    return render_template('addEmployee.html',dept_data=stored_dept,current_user=current_user)

@app.route("/delete_Employee/<int:empId>",methods=['GET'])
def delete_Employee(empId):
    '''Function to remove the employee from the database.'''
    current_user=get_current_user()

    if request.method=='GET':
        
        db=get_database()

        # removing both employee data as well password associated to employee in password table

        db.execute('DELETE FROM employee WHERE empId=?',[empId])

        db.execute('DELETE FROM passwordData WHERE empId=?',[empId])

        db.commit()

        return redirect(url_for("employee"))


    return render_template("employee.html",current_user=current_user)

@app.route("/updateEmp1/<int:empId>",methods=['GET','POST'])
def updateEmp(empId=None):
    return render_template('updateDepartment.html')

# route for viewFullProfileOfEmp
@app.route("/viewFullProfileOfEmp/<int:empId>",methods=['GET'])
def viewFullProfileOfEmp(empId):
    '''Function to view a complete profile of an employee.'''

    deptIdIfPresent=''
    current_user=get_current_user()

    # connecting to db
    db=get_database()

    # when user clicks on viewFullProfileOfEmp button the id associated to that employee will be passed to viewFullProfileOfEmp page

    # now retrieve all the details associated with that particular employee

    emp_cursor=db.execute('SELECT * FROM employee WHERE empId=?',[empId])

    stored_emp_complete_details=emp_cursor.fetchone()

    # if employee belongs to any department then the issue is we have stored it in the database as deptId but then we need to display it with deptName

    if stored_emp_complete_details['deptId']!=None:

        # select the name from deptName associated with deptId
        
        emp_cursor=db.execute('SELECT deptName FROM department WHERE deptId=?',[stored_emp_complete_details['deptId']])
    
        temp_emp_dept_name_data=emp_cursor.fetchone()

        temp_emp_dept_name_data=temp_emp_dept_name_data['deptName']
        
        deptIdIfPresent=temp_emp_dept_name_data

    return render_template('viewFullProfile.html',data=stored_emp_complete_details,deptIdIfPresent=deptIdIfPresent,current_user=current_user)

# route for add_salary
@app.route("/add_salary",methods=['GET'])    
def add_salary():

    db=get_database()

    current_user=get_current_user()

    emp_data_cursor=db.execute('SELECT employee.empId,employee.empName,department.deptId,department.deptName FROM employee INNER JOIN department on (employee.deptId=department.deptId)')

    emp_salary_data=emp_data_cursor.fetchall()

    dept_data_cursor=db.execute('SELECT deptId,deptName FROM department')

    emp_dept_data=dept_data_cursor.fetchall()

    dict_of_dept_emp_mapping={}


    for data in emp_dept_data:
        dict_of_dept_emp_mapping[data['deptName']]=[]

    list_of_individual_data=[]

    for data in emp_salary_data:
        list_of_individual_data=list(data)
        dict_of_dept_emp_mapping[data['deptName']].append(list_of_individual_data) 

    
    return render_template('addSalary.html',dept_emp_combined=dict_of_dept_emp_mapping,current_user=current_user)


@app.route("/addEmpSalary/<int:empId>/<string:empName>",methods=['POST','GET'])
def addEmpSalary(empId=None,empName=None):
    current_user=get_current_user()
    
    db=get_database()
        
    if request.method=='POST':
        
        employeeEmpId=empId
        employeeEmpName=empName
        employeeBasicSalary=request.form['basicSalary']
        employeeHra=request.form['hra']
        employeeOtherAllowances=request.form['otherAllowances']
        employeeDate=request.form['date']
        
        employeeDate=employeeDate[:-3]
        
        employeeSalaryCursor=db.execute('SELECT monthYear FROM salary WHERE empId=?',[employeeEmpId])
        employeeSalaryData=employeeSalaryCursor.fetchall()
        
        for data in employeeSalaryData:
            if employeeDate == data['monthYear']:
                date_error=f"Salary for {employeeEmpName} have been paid for {data['monthYear']}!"
                flash(date_error,"error") 
                return redirect(url_for('addEmpSalary',empId=empId,empName=empName))

        db.execute('INSERT INTO salary(basicSalary,hra,otherAllowances,monthYear,empId) VALUES(?,?,?,?,?)',[employeeBasicSalary,employeeHra,employeeOtherAllowances,employeeDate,employeeEmpId])
        
        db.commit()
        
        salaryCreditInfo=f"Salary for {employeeEmpName} have been credited successfully for {employeeDate}!"

        flash(salaryCreditInfo,"info")
        
        return redirect(url_for('add_salary'))
        
    return render_template('addEmpSalary.html',empId=empId,empName=empName,current_user=current_user)
    
@app.route("/salaryHistory/<int:empId>/<string:empName>",methods=['GET'])
def salaryHistory(empId=None,empName=None):
    
    if request.method=='GET':

        current_user=get_current_user()
        
        db=get_database()

        empSalaryDataCursor=db.execute('SELECT salaryId,monthYear,basicSalary,hra,otherAllowances FROM salary WHERE empId=?',[empId])

        empSalaryData=empSalaryDataCursor.fetchall()
        empSalaryDataTemp=[]
        for row in empSalaryData:
            empSalaryDataTemp.append(list(row))
        
        empSalaryData=empSalaryDataTemp

        return render_template('salaryHistory.html',empId=empId,empName=empName,current_user=current_user,empSalaryData=empSalaryData)

# route for employeeDashboard
@app.route("/employeeDashboard",methods=['GET'])
def employeeDashboard():
    return render_template("employeeDashboard.html")

# route for employeeLeaves
@app.route("/employeeLeaves")
def employeeLeaves():
    return render_template("employeeLeaves.html")

@app.route("/logout")
def logout():
    
    logout_display=f"{session['user']} logged out successfully!"

    session.pop('user',None)
    
    flash(logout_display,"info")
    
    return render_template('login.html')

if __name__=="__main__":

    # running Flask instance
    
    app.run(debug=True)