from flask import Flask, redirect, render_template, request, flash, url_for
import csv
from flask_mysqldb import MySQL, MySQLdb
import os
from scipy.spatial import distance
import matplotlib.pyplot as plt
import bag_of_words_model as bow_model
from search_helper import search_db
import search_helper

# add path. Where to upload csv files
path = f'{os.path.dirname(os.path.abspath(__file__))}\\upload_folder'
app = Flask(__name__)

app.secret_key = 'das83efad6989d7f9ca8c984befdd87134a8b0f' # required for flash() ... i just typed randomly (-.-)

mysql = MySQL(app)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'test'

# creates a directory folder
if not os.path.isdir(f'{os.path.dirname(os.path.abspath(__file__))}\\upload_folder'):
    os.mkdir(f'{os.path.dirname(os.path.abspath(__file__))}\\upload_folder')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')
    elif request.method == 'POST':
        table = []
        file = request.files['db-upload']
        if file.filename != '':
            file.save(f'{path}\\{file.filename}')
            with open(f'{path}\\{file.filename}') as files:
                csvfiles = csv.DictReader(files)
                for row in csvfiles:
                    table.append(row)
            exam_id = str(file.filename)[:-4]
            if upload_to_db(exam_id, table):
                flash('Uploaded to database successfully!', category='message')
            else:
                flash("The exam you selected has already been uploaded", category="error")
            os.remove(f'{path}\\{file.filename}')
            return render_template('upload.html')
        else:
            error = 'Error! No file was uploaded but the submit button was clicked!'
            flash(error, category='error')
            return render_template('upload.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    exam_ids = []
    try: exam_ids = exam_list()
    except MySQLdb.OperationalError:
        flash('Sorry, the server is down at the moment', category='error')
        return render_template('search.html', exam_list=exam_ids)
    if request.method == 'GET':
        if len(exam_ids) == 0:
            flash('Oops! There are no Exams that are uploaded yet. Please upload some first', category='error')
        return render_template('search.html', exam_list=exam_ids)
    elif request.method == 'POST':
        exam_id = request.form.get('exam')
        return redirect(url_for('search_table', exam_id=exam_id))

@app.route('/search/<exam_id>', methods=['GET', 'POST'])
def search_table(exam_id):
    exam_ids = exam_list()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f'''select distinct(`Item No`) from `exams` where `Exam ID`="{exam_id}"''')
    item_numbers = list(cursor.fetchall())
    cursor.execute(f'''select distinct(`Student ID`) from `exams` where `Exam ID`="{exam_id}"''')
    studentIds = list(cursor.fetchall())
    if request.method == 'GET':
        return render_template('search.html', exam_id=exam_id, exam_list=exam_ids, item_numbers=item_numbers, studentIds=studentIds)
    elif request.method == 'POST':
        global table
        global studentId
        global item_number
        studentId = request.form.get('studentId')
        item_number = request.form.get('item_number')
        table = list(search_db(cursor, exam_id, studentId, item_number))
        cursor.close()
        i_selected_vector = []
        for row in table:
            i_selected_vector.append([int(n) for n in row.pop('Vector')])
        bow_model.selected_vectors = i_selected_vector
        if table:
            return render_template('search.html', exam_id=exam_id, exam_list=exam_ids, item_numbers=item_numbers, table=table, studentId=studentId, item_number=item_number, studentIds=studentIds)
        else:
            error = 'The Student ID you gave does not exist, or did not take the exam'
            flash(error, category='error')
            return render_template('search.html', exam_id=exam_id, exam_list=exam_ids, item_numbers=item_numbers, studentIds=studentIds)

@app.route('/plot/<exam_id>', methods=['GET'])
def plot(exam_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if search_helper.search_constraints == 'all':
        result_euclideans = distance.cdist(bow_model.selected_vectors, bow_model.selected_vectors, 'euclidean')
        cursor.execute(f'''select `Student ID`, `Item No`, `Essay Answers` from exams where `Exam ID`="{exam_id}"''')
        compare_table = list(cursor.fetchall())
        print(compare_table)
        plt.plot(result_euclideans)
        plt.show()
        return render_template('plot_all.html', exam_id=exam_id, table=table, compare_table=compare_table, selected_vectors=bow_model.selected_vectors, result_euclideans=result_euclideans)
    elif search_helper.search_constraints == 'one_item_all_students':
        result_euclideans = distance.cdist(bow_model.selected_vectors, bow_model.selected_vectors, 'euclidean')
        cursor.execute(f'''select `Student ID`, `Item No`, `Essay Answers` from exams where `Exam ID`="{exam_id}" and `Item No`="{item_number}"''')
        compare_table = list(cursor.fetchall())
        plt.plot(result_euclideans)
        plt.show()
        return render_template('plot_one_item_all_students.html', exam_id=exam_id, compare_table=compare_table, selected_vectors=bow_model.selected_vectors, result_euclideans=result_euclideans, student_ids=search_helper.student_ids)
    elif search_helper.search_constraints == 'one_student_all_items':
        result_euclideans = distance.cdist(bow_model.all_vectors, bow_model.selected_vectors, 'euclidean')
        cursor.execute(f'''select `Student ID`, `Item No`, `Essay Answers` from exams where `Exam ID`="{exam_id}"''')
        compare_table = list(cursor.fetchall())
        plt.plot(result_euclideans)
        plt.show()
        return render_template('plot_one_student_all_items.html', exam_id=exam_id, compare_table=compare_table, selected_vectors=bow_model.selected_vectors, result_euclideans=result_euclideans, items_left=search_helper.items_left, item_count=search_helper.item_count, items=search_helper.items_searched_Student, studentId=studentId)
    elif search_helper.search_constraints == 'one_student_one_item':
        result_euclideans = distance.cdist(bow_model.all_vectors, bow_model.selected_vectors, 'euclidean')
        cursor.execute(f'''select `Student ID`, `Item No`, `Essay Answers` from exams where `Exam ID`="{exam_id}" and `Item No`="{item_number}"''')
        compare_table = list(cursor.fetchall())
        plt.plot(result_euclideans)
        plt.show()
        return render_template('plot_one_student_one_item.html', exam_id=exam_id, compare_table=compare_table, selected_vectors=bow_model.selected_vectors, result_euclideans=result_euclideans, student_ids=search_helper.student_ids, studentId=studentId)

def upload_to_db(exam_id, table) -> bool:
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f'''create table if not exists `exams`(`Student ID` varchar(64), `Exam ID` varchar(64), `Item No` varchar(64), `Essay Answers` longtext, `Vector` longtext)''')
    cursor.execute(f'''select distinct(`Exam ID`) from `exams`''')
    exam_ids = list(cursor.fetchall())
    exam_list = []
    answer_list = []
    student_ids = []

    for ids in exam_ids:
        exam_list.append(ids['Exam ID'])
    if exam_id in exam_list:
        return False
    else:
        for row in table:
            student_ids.append(row.pop('Student ID'))
            for itemNum in row.keys():
                answer_list.append(row[itemNum])
        vocab = bow_model.get_vocab(answer_list)
        i_student_id = 0
        i_answers = 0
        for row in table:
            for itemNum in row.keys():
                vec_str = ''
                i_vector = bow_model.vectorize(vocab, answer_list[i_answers])
                for num in i_vector:
                    vec_str += str(num)           
                cursor.execute(f"""insert into `exams`(`Exam ID`, `Student ID`, `Item No`, `Essay Answers`, `Vector`) values (%s, %s, %s, %s, %s)""", (exam_id, student_ids[i_student_id], itemNum, row[itemNum], vec_str))
                i_answers += 1
            i_student_id += 1

    mysql.connection.commit()
    cursor.close()
    return True

# create a list of exams for exam dropdown in web app
def exam_list() -> list:
    exam_list = []
    cursor = mysql.connection.cursor()
    cursor.execute(f'''select distinct(`Exam ID`) from `exams`''')
    for item in cursor.fetchall():
        exam_list.append(item[0])
    cursor.close()
    return exam_list

if __name__ == "__main__":
    app.run(debug=True)
