CREATE TABLE department(deptId INTEGER,deptName TEXT NOT NULL,PRIMARY KEY(deptId));

CREATE TABLE employee(empId INTEGER,empName TEXT NOT NULL,gender TEXT NOT NULL,dob TEXT,email TEXT NOT NULL,phone TEXT NOT NULL,deptId INTEGER,designation TEXT,empAddress TEXT,ctc INTEGER NOT NULL,adminFlag INTEGER,PRIMARY KEY(empId),FOREIGN KEY(deptId) REFERENCES department(deptId));

CREATE TABLE password_data(empId INTEGER,password TEXT,FOREIGN KEY(empId) REFERENCES employee(empId));

CREATE TABLE salary(salaryId INTEGER,basicSalary REAL NOT NULL,hra REAL,otherAllowances REAL,monthYear TEXT NOT NULL,empId INTEGER,PRIMARY KEY(salaryId),FOREIGN KEY(empId) REFERENCES employee(empId));

CREATE TABLE leaves(leaveId INTEGER,dateFrom TEXT NOT NULL,dateTo TEXT NOT NULL,REASON TEXT,empId TEXT,FOREIGN KEY(empId) REFERENCES employee(empId));