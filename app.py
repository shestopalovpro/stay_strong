from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import datetime
import matplotlib.pyplot as plt
import io

app = Flask(__name__,template_folder='templates')

def get_db_connection():
    conn = sqlite3.connect('trainings.db')
    
    return conn


conn = get_db_connection()
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS exercises
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT, ratio REAL)''')
conn.commit()

conn = get_db_connection()
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS plan
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              done INTEGER, date TEXT, exercise TEXT, quantity INTEGER, weight REAL)''')
conn.commit()

@app.route('/')
def index():
    conn = get_db_connection()
    c = conn.cursor()
    current_date = datetime.date.today()
    c.execute("SELECT id, exercise, quantity, weight FROM plan WHERE done = 0 AND date = ?",(current_date,))
    exercises = c.fetchall()
    return render_template('index.html', exercises=exercises)

@app.route('/update_plan', methods=['POST'])
def update_plan():
 
    plan_id = request.form['id']
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE plan SET done=? WHERE id=?", (int(1), plan_id,))
    conn.commit()
    return redirect('/')

@app.route('/trains')
def trains():
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM exercises")
    rows = c.fetchall()
    return render_template('exercises.html', rows=rows)

@app.route('/add_ex', methods=['POST'])
def add_exercises():
    
    conn = get_db_connection()
    c = conn.cursor()
    
    exercise = request.form['exercise']
    ratio = request.form['ratio']
    c.execute('INSERT INTO exercises (name, ratio) VALUES (?,?)',(exercise,ratio,))
    conn.commit()
    return redirect('/trains')

@app.route('/add_plan', methods=['POST'])
def add_plan():
    
    conn = get_db_connection()
    c = conn.cursor()
    
    dateplan = request.form['date']
    exercise = request.form['exercise']
    quantity = request.form['quantity']
    weight   = request.form['weight']

    c.execute('INSERT INTO plan (done, date, exercise, quantity, weight) VALUES (?,?,?,?,?)',(int(0),dateplan,exercise,quantity,weight,))
    conn.commit()
    return redirect('/plan')

@app.route('/plan')
def select_ex():
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM exercises")
    rows = c.fetchall()
    
    options = []
    for row in rows:
        options.append(row[1]) 
    c.execute("SELECT * FROM plan WHERE done = 0")
    rows = c.fetchall()
    return render_template('plan.html', options=options,rows=rows)

@app.route('/stat')
def graph():
    conn = get_db_connection()
    c = conn.cursor()

    c.execute("SELECT date, quantity FROM plan WHERE exercise=?", ('Отжимания',))
    rows = c.fetchall()

    dates = [row[0] for row in rows]
    quantities = [row[1] for row in rows]

    buf = io.BytesIO()
    
    buf.close()
    plt.plot(dates, quantities)
    plt.xlabel('Дата')
    plt.ylabel('Количество повторений')
    plt.title('График выполнения упражнения "Отжимания"')

    # Сохраняем график в буфер
    buf = io.BytesIO()
    
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Выводим график на страницу
    return send_file(buf, mimetype='image/png')
    

if __name__ == '__main__':
    app.run(host='0.0.0.0')