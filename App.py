from flask import Flask, render_template, request, url_for, redirect, flash, session, escape
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app=Flask(__name__)

##MYSQL conexion
#app.config["MYSQL_HOST"] = "localhost"
#app.config["MYSQL_USER"] = "root"
#app.config["MYSQL_PASSWORD"] = "password"
#app.config["MYSQL_DB"] = "bbddlub" #le pido que se conecte a la base de datos prueba flask
##cuando pongo el puerto no anda

class User(UserMixin):
    def __init__(self, id, name, permiso):
        self.id = id
        self.name = name
        self.permiso = permiso



login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    for user in users:
        if user.id == int(user_id):
            return user
    return None

#get envia las peticiones a travez de la barra de direcciones, post no.
#iniciamos sesion(guarda datos en una memoria para luego usarlos)
app.secret_key="mysecretkey"

#en templates guardo todo lo que se ve

suma=[]#memoria interna de articulos seleccionados
total=0.0#total en pesos de la compra

#hashed_pw = generate_password_hash("1995",method="sha256")
#mysql.execute("INSERT INTO usuarios (username,password,permiso) VALUES (?,?,?)", 
#        ("scuozzo",hashed_pw,"1"))
#mysql.commit()
users=[]
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/Ingreso", methods= ["GET","POST"])
def Ingreso():
    global data
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        mysql = sqlite3.connect("./Proyecto.db")
        cur=mysql.cursor()
        cur.execute("SELECT * FROM usuarios WHERE username =?",(username,))
        data = cur.fetchall()
        if len(data) == 0 :
            flash("Usuario inexistente, verifique y vuelva a intentar.")
            return render_template("index.html")
        else:
            data=list(data[0])
            if data[1] == username and check_password_hash(data[2], password):
                user = User(data[0], data[1], data[3])
                users.append(user)
                # Dejamos al usuario logueado
                login_user(user, remember=True)
                flash("the current user is " + current_user.name)
                return render_template("buscar.html")
            else:
                flash("Contraseña INCORRECTA, verifique y vuelva a intentar.")
                return render_template("index.html")
    if request.method == "GET":
        #vuelvo a cargar data con los datos del usuario
        #if "username" in session:
        flash("the current user is " + current_user.name)
        return render_template("buscar.html")
        #else:
        flash("Debes loguearte primero")
        return render_template("index.html")


##########################################################################
#######################REGISTRO DE NUEVO USUARIO##########################
##########################################################################

@app.route("/Registro", methods=["POST"])
def Registro():
    if request.method == "POST":
        return render_template("registro.html")



@app.route("/Registro_usuario", methods= ["POST"])
def Registro_usuario():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_pw = generate_password_hash(password,method="sha256")
        mysql = sqlite3.connect("./Proyecto.db")
        mysql.execute("INSERT INTO usuarios (username,password,permiso) VALUES (?,?,?)", 
                (username,hashed_pw,"5"))
        mysql.commit()
        flash("Usuario Registrado")
        return render_template("index.html")



##########################################################################
#######################Administrar USUARIO################################
##########################################################################

@app.route("/Usuarios", methods= ["GET","POST"])
@login_required
def Usuarios():
    if request.method == "GET":
        mysql = sqlite3.connect("./Proyecto.db")
        cur=mysql.cursor()
        cur.execute("SELECT * FROM usuarios")
        data = cur.fetchall()
        return render_template("Usuarios.html",data=data)


##########################################################################
#######################Cambiar Permiso de USUARIO#########################
##########################################################################

@app.route("/Cambiar/<i>", methods= ["GET","POST"])
def Cambiar(i):
    if request.method == "POST":
        permiso = request.form["permiso"]
        mysql = sqlite3.connect("./Proyecto.db")
        mysql.execute("""
                     UPDATE usuarios
                     SET permiso = ?
                      WHERE id=?
            """,(permiso,i))
        mysql.commit()

        mysql = sqlite3.connect("./Proyecto.db")
        cur=mysql.cursor()
        cur.execute("SELECT * FROM usuarios")
        data = cur.fetchall()
        return render_template("Usuarios.html",data=data)

    if request.method == "GET":

        flash("Debes loguearte primero")
        return render_template("index.html")



##########################################################################
############################ELIMINAR USUARIO##############################
##########################################################################




@app.route("/Eliminar/<string:id>")#recibo un parametro tipo string
def elimclient(id):
    mysql = sqlite3.connect("./Proyecto.db")
    cur = mysql.cursor()
    cur.execute("DELETE FROM usuarios WHERE id = ?", (id,))
    mysql.commit() #guardo los cambios
    flash("Usuario eliminado satifactoriamente") #envia mesajes entre vistas
    mysql.close
    mysql = sqlite3.connect("./Proyecto.db")
    cur=mysql.cursor()
    cur.execute("SELECT * FROM usuarios")
    data = cur.fetchall()
    return render_template("Usuarios.html",data=data)


##########################################################################
##############################CERRAR SESION###############################
##########################################################################


@app.route("/Logout", methods= ["GET"])
def Logout():
    if request.method == "GET":
        logout_user()
        flash("Has cerrado sesion!")
        return render_template("index.html")


if __name__ == "__main__":
    app.run(host= '192.168.0.101', port = 3000, debug = True) #hacemos que se refresque solo
