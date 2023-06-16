from flask import Flask, render_template, request, redirect
import sqlite3

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
    return render_template('plan.html', options=options)

if __name__ == '__main__':
    app.run(debug=True)