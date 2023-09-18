import bag_of_words_model as bow_model

search_constraints = ''
item_count = 0
items_searched_Student = []
items_left = []
student_ids = []


def search_db(cursor, exam_id, studentId, item_number):
    bow_model.selected_vectors = []
    bow_model.all_vectors = []
    global search_constraints
    match(studentId == '', item_number == 'ALL'):
        case True, True:
            search_constraints = 'all'
            cursor.execute(f'''select * from `exams` where `Exam ID`="{exam_id}"''')
        case True, False:
            search_constraints = 'one_item_all_students'
            cursor.execute(f'''select `Student ID`, `Vector` FROM `exams` WHERE `Item No`="{item_number}" and `Exam ID`="{exam_id}"''')
            global student_ids
            student_ids = list(cursor.fetchall())
            cursor.execute(f'''select * from `exams` where `Item No`="{item_number}" and `Exam ID`="{exam_id}"''')
        case False, True:
            search_constraints = 'one_student_all_items'
            cursor.execute(f'''select `Item No` from `exams` where `Student ID`="{studentId}" and `Exam ID`="{exam_id}"''')
            global items_searched_Student
            items_searched_Student = list(cursor.fetchall())
            global item_count
            item_count = len(items_searched_Student)
            cursor.execute(f'''SELECT `Student ID`, `Item No`, `Vector` FROM `exams` WHERE `Student ID`!="{studentId}" and `Exam ID`="{exam_id}"''')
            i_all_vectors = []
            global items_left
            items_left = list(cursor.fetchall())
            for row in items_left:
                i_all_vectors.append([int(n) for n in row.pop('Vector')])
            bow_model.all_vectors = i_all_vectors
            cursor.execute(f'''select * from `exams` where `Student ID`="{studentId}" and `Exam ID`="{exam_id}"''')
        case False, False:
            search_constraints = 'one_student_one_item'
            cursor.execute(f'''select `Student ID`, `Vector` FROM `exams` WHERE `Item No`="{item_number}" and `Exam ID`="{exam_id}" and `Student ID`!="{studentId}"''')
            student_ids = list(cursor.fetchall())
            i_all_vectors = []
            for row in student_ids:
                i_all_vectors.append([int(n) for n in row.pop('Vector')])
            bow_model.all_vectors = i_all_vectors
            cursor.execute(f'''select * from `exams` where `Student ID`="{studentId}" and `Item No`="{item_number}" and `Exam ID`="{exam_id}"''')
    return cursor.fetchall()
    