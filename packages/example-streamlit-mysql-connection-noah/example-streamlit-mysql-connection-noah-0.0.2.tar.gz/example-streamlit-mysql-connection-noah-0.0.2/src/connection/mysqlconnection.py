import pymysql
import streamlit as st

def mysql_test(hostname,user,dbpassword,dbname, table_name): #method
    #Step1 Define URL Parameters
    query_params = st.experimental_get_query_params()
    usernames = query_params['usernames']
    names = query_params['names']
    password = query_params['password']
    role = query_params['role']
    view = query_params['view']

    #Step2 Connect with MySQL Database(where user inform)
    conn = pymysql.connect(host=hostname, user=user,password=dbpassword, db=dbname, charset='utf8')
    cur = conn.cursor()

    #Step3 Query
    sql = 'select * from '+dbname+'.'+table_name+' where username =%s and name =%s and password =%s'
    vals = (usernames, names, password)
    cur.execute(sql, vals)
    #4Step4 Output
    rows = cur.fetchall()
    if len(rows) == 1:
        #st.write('CONNECTION SUCCESS')
        #method
        return '1',role, view
        conn.close()
    else:

        #st.write('CONNECTION ERROR')
        return '0'
        conn.close()