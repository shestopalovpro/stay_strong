from flask import Flask, render_template, request, redirect
import sqlite3
import datetime

app = Flask(__name__,template_folder='templates')

def get_db_connection():
    conn = sqlite3.connect('trainings.db')
    
    return conn

# создание базы данных и таблицы
conn = get_db_connection()
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS exercises
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT)''')
conn.commit()

conn = get_db_connection()
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS plan
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              done INTEGER, date TEXT, exercise TEXT, quantity INTEGER)''')
conn.commit()

@app.route('/')
def index():
    # получение всех записей из таблицы trainings
    conn = get_db_connection()
    c = conn.cursor()
    current_date = datetime.date.today()
    c.execute("SELECT id, exercise, quantity FROM plan WHERE done = 0 AND date = ?",(current_date,))
    exercises = c.fetchall()
    return render_template('index.html', exercises=exercises)

@app.route('/update_plan', methods=['POST'])
def update_plan():
 # Получение данных из формы
    plan_id = request.form['id']
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE plan SET done=? WHERE id=?", (int(1), plan_id,))
    conn.commit()
    return redirect('/')



@app.route('/trains')
def trains():
    # получение всех записей из таблицы trainings
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM exercises")
    rows = c.fetchall()
    return render_template('exercises.html', rows=rows)

@app.route('/add_ex', methods=['POST'])
def add_exercises():
    # получение данных из формы и запись в базу данных
    conn = get_db_connection()
    c = conn.cursor()
    
    exercise = request.form['exercise']
    
    c.execute('INSERT INTO exercises (name) VALUES (?)',(exercise,))
    conn.commit()
    return redirect('/trains')

@app.route('/add_plan', methods=['POST'])
def add_plan():
    # получение данных из формы и запись в базу данных
    conn = get_db_connection()
    c = conn.cursor()
    
    dateplan = request.form['date']
    exercise = request.form['exercise']
    quantity = request.form['quantity']
    
    c.execute('INSERT INTO plan (done, date, exercise, quantity) VALUES (?,?,?,?)',(int(0),dateplan,exercise,quantity,))
    conn.commit()
    return redirect('/plan')

@app.route('/plan')
def select_ex():
    # получение всех записей из таблицы exercises
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM exercises")
    rows = c.fetchall()
    # создание списка для выпадающего списка
    options = []
    for row in rows:
        options.append(row[1]) # добавление названия упражнения в список
    c.execute("SELECT * FROM plan WHERE done = 0")
    rows = c.fetchall()
    return render_template('plan.html', options=options,rows=rows)
   
    

    

if __name__ == '__main__':
    app.run(debug=True)