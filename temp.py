'''if request.method=='POST':
        
        updatedName=request.form['newempname']
        updatedGender=request.form['gender']
        updatedDob=request.form['dob']
        updatedEmail=request.form['email']
        updatedPhone=request.form['phone']
        updatedDepartment=request.form['department']
        updatedDesignation=equest.form['designation']
        updatedAddress=request.form['address']
        updatedCtc=request.form['ctc']

        retrive_emp_name=db.execute('SELECT * FROM employee where empId=?',[empId])

        if not retrive_emp_name:

            error=f'Employee {updatedName} not present!Kindly add the details in addEmployee Section!'

            flash(error,"error")

            return render_template('updateEmployee.html',empId=empId,current_user=current_user)
            
        list_of_updated_data=[updatedName,updatedGender,updatedDob,updatedEmail,updatedPhone,updatedDepartment,updatedDesignation,updatedAddress,updatedCtc]

        
        list_of_columns=['empName','gender','dob','email','phone','deptId','designation','empAddress','ctc']

        column_to_value={}

        for data in range(len(list_of_updated_data)):
            if data:
                column_to_value[list_of_columns[data]]=list_of_updated_data[data]

        string_to_hold_query=''

        for key,value in column_to_value.items():
            string_to_hold_query+=f'SET {key}=?,'

        string_to_hold_query=string_to_hold_query[:-1]

        str_of_values_for_param_query=''

        for data in list_of_updated_data:
            
            if data:

                str_of_values_for_param_query=str(data)+' '    
        
        list_of_updated_data=str_of_values_for_param_query.split()

        list_of_updated_data.append(empId)
        db.execute(f'UPDATE EMPLOYEE {string_to_hold_query} WHERE empId=?',list_of_updated_data)

        db.commit()

        return redirect(url_for('employee'))
    
    dept_data_cur=db.execute('SELECT deptName FROM department')
    stored_dept=dept_data_cur.fetchall()

    db.commit()
    return render_template('updateEmployee.html',stored_dept=stored_dept,current_user=current_user,empId=empId)'''
