from flask import Flask,request,render_template,redirect,url_for,session,flash
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import secrets

app = Flask(__name__)

conn = pymysql.connect(host='localhost',user='admin',passwd='admin',db='sucursal')

app.config['SECRET_KEY'] = secrets.token_urlsafe(10)

@app.route('/')
def inicio():    
    if not session.get('logged_in'):
        return login()
    else:
        return render_template('index.html')    

@app.route('/signup',methods=['POST','GET'])
def SignUp():
    if request.method == 'POST':
        nombre = str(request.form['user'])
        email = str(request.form['email'])
        password = generate_password_hash(str(request.form['password']))
        cursor = conn.cursor()
        cursor.execute("SELECT nombre,email FROM usuarios WHERE email = %s ",(email))
        usuario = cursor.fetchone()
        if usuario is not None:           
            flash("Correo ya Existe")
            return render_template('usuario/reg_usuario.html')
        else:
            cursor.execute("INSERT INTO usuarios (nombre,email,password)values(%s,%s,%s)",(nombre,email,password))
            conn.commit()            
            return redirect(url_for('login'))
    else:
        return render_template('usuario/reg_usuario.html')

@app.route('/login')
def login():
    return render_template('usuario/login.html')

@app.route('/usuario',methods=['POST','GET'])    
def usuario():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            nombre = str(request.form['user'])
            print(request.form['email'])
            email = str(request.form['email'])
            password = generate_password_hash(str(request.form['password']))
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET nombre = %s,password = %s WHERE email = %s ",(nombre,password,email))
            conn.commit()
            session['logged_in'] = False
            session['nombre'] =  ''
            session['email'] =  '' 
            return redirect(url_for('login'))
        else:
            cursor = conn.cursor()
            cursor.execute("SELECT nombre,email FROM usuarios WHERE email = %s ",(session['email']))
            usuario = cursor.fetchone()
            contexto = {"nombre":usuario[0],"email":usuario[1]}
            if usuario is not None:
                return render_template('usuario/edi_usuario.html',form=contexto)
        

@app.route('/check',methods=['POST'])
def check():
    email = str(request.form['email'])
    password = str(request.form['password'])
    cursor = conn.cursor()
    cursor.execute("SELECT nombre,password FROM usuarios WHERE email = %s ",(email))
    usuario = cursor.fetchone()    
    if usuario is not None:
        session['logged_in'] = check_password_hash(usuario[1], password)
        if session['logged_in'] == False:
            session['nombre'] =  ''
            session['email'] =  ''            
            flash("Email o Password Incorrectos")
        else:
            session['nombre'] =  usuario[0]
            session['email'] =  email           
        return redirect(url_for('inicio'))
    else:
        flash("Email o Password Incorrectos")
        session['logged_in'] = False
        session['nombre'] =  ''
        session['email'] =  ''
        return redirect(url_for('inicio'))

@app.route('/salir')
def cerrar():
    session['logged_in'] = False
    session['nombre'] =  ''
    session['email'] =  ''     
    return inicio()

if __name__ == '__main__':
    app.run(port=3000,debug=True)