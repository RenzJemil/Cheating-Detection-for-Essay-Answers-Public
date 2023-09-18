from logging import error
from flask import Flask, redirect, render_template, request, flash, url_for
import csv
from flask_mysqldb import MySQL, MySQLdb
import os

# add path. Where to upload csv files
path = f'{os.path.dirname(os.path.abspath(__file__))}\\upload_folder'
app = Flask(__name__)

app.secret_key = 'das83efad6989d7f9c' # required for flash() ... i just typed randomly (-.-)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'test'

mysql = MySQL(app)

if not os.path.isdir('upload_folder'):  # creates a directory folder
    os.mkdir('upload_folder')

# make sure you install xaamp first. Download it here: https://www.apachefriends.org/download.html
# run it and click start on apache and MySQL
# type http://127.0.0.1:5000/database-upload in url/address bar of browser after you run this file
@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')
    elif request.method == 'POST':
        table = []
        file = request.files['db-upload']

        if file.filename != '':
            file.save(f'{path}\\{file.filename}')
            with open(f'{path}\\{file.filename}') as files:
                csvfiles = csv.DictReader(files)  # reverted to DictReader()
                for row in csvfiles:
                    table.append(row)
            table_name = str(file.filename)[:-4]
            upload_to_db(table_name, table)
            flash('Uploaded to database successfully!', category='message')
            return render_template('upload.html')
        else:  # if submit button is clicked without selecting a file
            error = 'Error! No file was uploaded but the submit button was clicked!'
            flash(error, category='error')
            return render_template('upload.html')  # added a span message

#SEARCH PAGE [COPIED CODES FROM DATABASE UPLOAD]
@app.route('/search', methods=['GET', 'POST'])
def search():
    cursor = mysql.connection.cursor()
    cursor.execute(f'''show tables''')
    if request.method == 'GET':
        if len(cursor.fetchall()) == 0:
            error = 'Oops! There are no Exams that are uploaded yet. Please upload some first'
            flash(error, category='warning')
        return render_template('search.html')
    elif request.method == 'POST':
        table_name = request.form.get('exam')
        cursor.execute(f'''show tables like "{table_name}"''')
        if len(cursor.fetchall()) == 0:
            error = 'The Exam you are looking for has not been uploaded yet'
            flash(error, category='error')
            return render_template('search.html')
        else:
            cursor.close()
            return redirect(url_for('search_table', table_name=table_name))

@app.route('/search/<table_name>', methods=['GET', 'POST'])
def search_table(table_name):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'GET':
        cursor.execute(f'''show columns from `{table_name}`;''')
        return render_template('search.html', table_name=table_name, item_numbers=cursor.fetchall()[1:])
    elif request.method == 'POST':
        table = []
        studentId = request.form.get('studentId')
        item_number = request.form.get('item_number')
        for item in search_db(cursor, table_name, studentId, item_number):
            table.append(item)
        return render_template('search.html', headers=table[0].keys(), table=table)

# this will create a new table named the same as the file name uploaded in the form inside the database instance named "test"
# then will create columns inside that table named as the items in the first row of the csv file
def upload_to_db(table_name, table):
    cursor = mysql.connection.cursor()
    cursor.execute(f'''drop table if exists `{table_name}`;''')
    cursor.execute(
        f'''create table if not exists `{table_name}`(`{next(iter(table[0].keys()))}` varchar(255));''')  # create the table and the first column. It's required to have at least one column on table create
    for key in table[0].keys():  # add the remaining columns
        cursor.execute(f'''alter table `{table_name}` add column if not exists `{key}` varchar(255);''')

    # this adds the contents of the csv file to the sql table
    cursor.execute(f'''load data local infile 'upload_folder/{table_name}.csv' into table `{table_name}` fields terminated by ',' lines terminated by '\n' ignore 1 rows;''')

    mysql.connection.commit()
    cursor.close()


# Still figuring out how to solve the problem of too many if statements
def search_db(cursor, table_name, studentId, item_number):
    table = []
    cursor.execute(f'''select * from `{table_name}`''')
    for item in cursor.fetchall():
        table.append(item)
    cursor.close()
    return render_template('sql_table.html', headers=table[0].keys(), table=table)

#SEARCH PAGE [COPIED CODES FROM DATABASE UPLOAD]
@app.route('/search-db', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return render_template('search.html')
    elif request.method == 'POST':
        table = []
        file = request.files['db-upload']

        if file.filename != '':
            file.save(f'{path}\\{file.filename}')
            with open(f'{path}\\{file.filename}') as files:
                csvfiles = csv.DictReader(files)  # reverted to DictReader()
                for row in csvfiles:
                    table.append(row)
            table_name = str(file.filename)[:-4]
            upload_to_db(table_name, table)
            #added another connection cursor to display the itemNo in dropdown
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) #Added dictcursor
            cursor.execute(f'''select * from essay_answers group by ItemNo''')
            ItemNo = cursor.fetchall()
            flash('Uploaded to database successfully!', category='message')
            return render_template('search.html', table_name=table_name, ItemNo=ItemNo)
        else:  # if submit button is clicked without selecting a file
            error = 'Error! No file was uploaded but the submit button was clicked!'
            flash(error, category='error')
            return render_template('search.html')  # added a span message

#ALMOST THE SAME FROM DATABASE UPLOAD
# N-O-T-E !!! THIS FUNCTION ONLY WORKS ON ESSAY_ANSWERS.CSV FILE SINCE IT IS A SUGGESTED TEMPLATE
@app.route('/search-db/<table_name>', methods=['GET', 'POST'])
def table_search(table_name):
    table = []
    studentID = request.form['studentID'] #GET THE TEXT INPUT FROM SEARCH.HTML
    itemNo = request.form['examID'] #GET THE SELECT INPUT FROM SEARCH.HTML
    cursor = mysql.connection.cursor()
    cursor.execute(f'''show columns from `{table_name}`;''')
    cols = []
    for item in cursor.fetchall():
        cols.append(item[0])
    table.append(tuple(cols))

    #SO MANY IF STATEMENTS
    if studentID == '' and itemNo == '': #CHECKING IF TEXT IS EMPTY OR NOT
        cursor.execute(f'''select * from {table_name}''')
    elif studentID != '' and itemNo == '':
        cursor.execute(f'''select * from {table_name} where studentID={studentID}''')
    elif studentID == '' and itemNo != '':
        cursor.execute(f'''select * from {table_name} where itemNo={itemNo}''')
    else:
        cursor.execute(f'''select * from {table_name} where studentID={studentID} and itemNo={itemNo} ''')

    for item in cursor.fetchall():
        table.append(item)
    cursor.close()
    return render_template('search.html', table=table)

if __name__ == "__main__":
    app.run(debug=True)
