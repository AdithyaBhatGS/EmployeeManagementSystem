from flask import g 

import sqlite3

def connect_to_db():

    sql=sqlite3.connect("C:/Users/ADITHYA GS/OneDrive/Documents/Programs/employeeManagementSystem1/employeeDB.db")

    sql.row_factory=sqlite3.Row

    return sql 

def get_database():
    
    if not hasattr(g,'employeeDB_var'):

        g.employeeDB_var=connect_to_db()

    return g.employeeDB_var