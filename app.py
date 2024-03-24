from flask import Flask, render_template, request, redirect
import sqlite3
import datetime

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


    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT plan.date,SUM((exercises.ratio*plan.quantity+exercises.ratio*plan.weight)*10) FROM plan JOIN exercises ON plan.exercise = exercises.name WHERE done = 1 GROUP BY plan.date")
    indexss = c.fetchall()
    indexavg = []
    for inss in indexss:
      indexavg.append(round(inss[1],3))
    counttrains = len(indexavg)
    indexssv=round(sum(indexavg)/len(indexavg),3)
    indexmax=max(indexavg)
    
    return render_template('index.html', exercises=exercises,indexss=indexssv,indexmax=indexmax,counttrains=counttrains)

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
    c.execute("SELECT * FROM plan WHERE done = 0 AND date >= DATE('now') ORDER BY plan.date")
    rows = c.fetchall()
    return render_template('plan.html', options=options,rows=rows)

@app.route('/stat')
def stat():
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT plan.date,SUM((exercises.ratio*plan.quantity+exercises.ratio*plan.weight)*10) FROM plan JOIN exercises ON plan.exercise = exercises.name WHERE done = 1 GROUP BY plan.date")
    
    results = c.fetchall()

    labels = [r[0] for r in results]
    data = [r[1] for r in results]
    
 
    # Return the components to the HTML template 
    return render_template(
        template_name_or_list='stat.html',
        data=data,
        labels=labels,
    )
    

if __name__ == '__main__':
    app.run(host='0.0.0.0')
