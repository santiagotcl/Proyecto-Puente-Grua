from flask import Flask, render_template, request, url_for, redirect, flash, session, escape, make_response
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests
from bs4 import BeautifulSoup
from datetime import date, datetime
import time
import os
from  flask_weasyprint  import  HTML ,  render_pdf
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

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

class Temp():
    def __init__(self,numero,peso):
        self.numero = numero
        self.peso = peso


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

BigTemp=[]#memoria interna de articulos seleccionados
Camion=[]#guarda los datos del camion donde se estan cargando big bags
i=0
nelim=[]#numeros de big bags eliminados
#hashed_pw = generate_password_hash("1995",method="sha256")
#mysql.execute("INSERT INTO usuarios (username,password,permiso) VALUES (?,?,?)", 
#        ("scuozzo",hashed_pw,"1"))
#mysql.commit()
users=[]
patente=""
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/Ingreso", methods= ["GET","POST"])
def Ingreso():
    #global data
    global BigTemp
    global nelim
    global i
    global Camion
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
        Camion.clear()
        BigTemp.clear()
        nelim.clear()
        i=0
        flash("the current user is " + current_user.name)
        return render_template("buscar.html")
        #else:
        #flash("Debes loguearte primero")
        #return render_template("index.html")


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











##########################################################################
##########################APLICACION DE CAMIONES##########################
########################################################################## 
def get_data(): 
    response = requests.get("http://10.0.0.28")
    response.encoding = "utf-8"
    response = requests.get("http://10.0.0.28")
    soup=BeautifulSoup(response.text,'html.parser')
    hola=soup.find_all("p")
    hola1=[hola[3].contents[0],hola[5].contents[0]]
    #hola1=[300,256]
    return(hola1)

def get_fecha():
    now = datetime.now()
    fecha = now.strftime('%d-%m-%Y')
    return(fecha)

def get_hora():
    now = datetime.now()
    hora = now.strftime('%H:%M')
    return(hora)

def Enviar_Email():
    global BigTemp
    global Camion
    # Iniciamos los parámetros del script
    remitente = 'santiagocuozzo@hotmail.com'
    destinatarios = ['santiagocuozzo2@gmail.com']
    asunto = '[RPI] Correo de prueba'
    cuerpo = 'Este es el contenido del mensaje'
    fecha=get_fecha()
    ruta_adjunto = 'C:/Users/pbertini/Desktop/Proyecto-Puente-Grua/'+Camion[2]+"-"+fecha+'.pdf'
    nombre_adjunto = Camion[2]+"-"+fecha+'.pdf'

    # Creamos el objeto mensaje
    mensaje = MIMEMultipart()
    
    # Establecemos los atributos del mensaje
    mensaje['From'] = remitente
    mensaje['To'] = ", ".join(destinatarios)
    mensaje['Subject'] = asunto
    
    # Agregamos el cuerpo del mensaje como objeto MIME de tipo texto
    mensaje.attach(MIMEText(cuerpo, 'plain'))
    
    # Abrimos el archivo que vamos a adjuntar
    archivo_adjunto = open(ruta_adjunto, 'rb')
    
    # Creamos un objeto MIME base
    adjunto_MIME = MIMEBase('application', 'octet-stream')
    # Y le cargamos el archivo adjunto
    adjunto_MIME.set_payload((archivo_adjunto).read())
    # Codificamos el objeto en BASE64
    encoders.encode_base64(adjunto_MIME)
    # Agregamos una cabecera al objeto
    adjunto_MIME.add_header('Content-Disposition', "attachment; filename= %s" % nombre_adjunto)
    # Y finalmente lo agregamos al mensaje
    mensaje.attach(adjunto_MIME)
    
    # Creamos la conexión con el servidor
    sesion_smtp = smtplib.SMTP('smtp-mail.outlook.com', 587)
    
    # Ciframos la conexión
    sesion_smtp.starttls()

    # Iniciamos sesión en el servidor
    sesion_smtp.login('santiagocuozzo@hotmail.com','Elnote7explota')

    # Convertimos el objeto mensaje a texto
    texto = mensaje.as_string()

    # Enviamos el mensaje
    sesion_smtp.sendmail(remitente, destinatarios, texto)

    # Cerramos la conexión
    sesion_smtp.quit()

    Camion.clear()
    BigTemp.clear()
    nelim.clear()
    i=0
    return render_template("/buscar.html")

def filtro(data):
    n=0
    fecha=[]
    temp=list(data[0])
    fecha.append(temp[4])
    i=len(data)
    print(i)
    j=0
    while(j<i):
        temp=list(data[j])
        print(temp)
        if(fecha[n]!=temp[4]):
            fecha.append(temp[4])
            n=n+1
        j=j+1
    print(fecha)
    return (fecha)

##########################################################################
##########################Fn principal####################################
########################################################################## 

@app.route("/CargaBigBags", methods=['POST','GET'])
@login_required
def CargaBigBags():
    global BigTemp
    global Camion
    global i
    if request.method == "POST":
        nombre = request.form["nombre"]
        modelo = request.form["modelo"]
        patente = request.form["patente"]
        Camion.append(nombre)
        Camion.append(modelo)
        Camion.append(patente)
        i=0
        peso=get_data()
        mysql = sqlite3.connect("./Proyecto.db")
        cur=mysql.cursor()
        cur.execute("SELECT * FROM camiones WHERE patente = ? AND fecha = ? ORDER BY n DESC", (Camion[2],get_fecha()))#busco si ese camion ya tiene registros ese dia para retomar carga en caso de algun problema
        ntemp = cur.fetchall()
        #verifico si tengo registros y si es asi busco el ultimo n de bigbags para continuar con la carga
        if(len(ntemp)>0):    
            ntemp = list(ntemp[0])
            i=ntemp[6]
            mysql = sqlite3.connect("./Proyecto.db")
            cur=mysql.cursor()
            cur.execute("SELECT * FROM camiones WHERE patente = ? AND fecha = ? ORDER BY n DESC ", (Camion[2],get_fecha()))
            BigTemp = cur.fetchall()
            mysql.close
        flash("Puedes Comenzar!")    
        return render_template("/CargaBigBags.html",bigtemp=BigTemp,peso=peso)   
    if request.method == "GET":
        peso=get_data()
        mysql = sqlite3.connect("./Proyecto.db")
        cur=mysql.cursor()
        cur.execute("SELECT * FROM camiones WHERE patente = ? AND fecha = ? ORDER BY n DESC ", (Camion[2],get_fecha()))
        BigTemp = cur.fetchall()
        mysql.close
        flash("Puedes Comenzar!")
        return render_template("/CargaBigBags.html",bigtemp=BigTemp,peso=peso) 


##########################################################################
##################pagina de carga de datos del camion#####################
########################################################################## 

@app.route("/Nuevocamion", methods=['GET'])
@login_required
def Nuevocamion():
    return render_template("/Nuevocamion.html")    


##########################################################################
######################Carga de big-Bag en la BDD##########################
########################################################################## 

@app.route("/anadirbigbag/<peso0>/<peso1>")
@login_required
def anadirbigbag(peso0,peso1):
    global Camion
    global BigTemp
    global i
    #obtengo hora y fecha actuales
    now = datetime.now()
    fecha = now.strftime('%d-%m-%Y')
    hora = now.strftime('%H:%M')
    #me conecto con la BDD
    mysql = sqlite3.connect("./Proyecto.db")
    
    if(len(nelim)>0):#verifico que no se hayan eliminado bigbags previamente
        mysql.execute("INSERT INTO camiones (nombre,modelo,patente,fecha,hora,n,peso,Salida) VALUES (?,?,?,?,?,?,?,?)", 
        (Camion[0],Camion[1],Camion[2],fecha,hora,nelim[0],peso0,0))
        mysql.commit()
        mysql.execute("INSERT INTO camiones (nombre,modelo,patente,fecha,hora,n,peso,Salida) VALUES (?,?,?,?,?,?,?,?)", 
        (Camion[0],Camion[1],Camion[2],fecha,hora,nelim[1],peso1,0))
        mysql.commit()
        nelim.clear()
    else:
        i=i+1
        #guardo BigBag de balanza 1 en la BDD
        mysql.execute("INSERT INTO camiones (nombre,modelo,patente,fecha,hora,n,peso,Salida) VALUES (?,?,?,?,?,?,?,?)", 
            (Camion[0],Camion[1],Camion[2],fecha,hora,i,peso0,0))
        mysql.commit()
        #repito el proceso
        i=i+1
        mysql.execute("INSERT INTO camiones (nombre,modelo,patente,fecha,hora,n,peso,Salida) VALUES (?,?,?,?,?,?,?,?)", 
            (Camion[0],Camion[1],Camion[2],fecha,hora,i,peso1,0))
        mysql.commit()
    cur=mysql.cursor()
    cur.execute("SELECT * FROM camiones WHERE patente = ? AND fecha = ? ORDER BY n DESC ", (Camion[2],get_fecha()))
    BigTemp = cur.fetchall()
    peso=get_data()
    return render_template("/CargaBigBags.html",bigtemp=BigTemp,peso=peso)

##########################################################################
######################Eliminar Big Bag de la BDD##########################
##########################################################################
@app.route("/Eliminarbigbag/<string:id>/<int:n>")#recibo un parametro tipo string
@login_required
def eliminarbigbag(id,n):
    global BigTemp
    global nelim
    mysql = sqlite3.connect("./Proyecto.db")
    #elimino de a pares, ya que la balanza siempre pesa de a 2
    nelim.append(n)
    nelim.append(n+1)
    cur = mysql.cursor()
    #borro de a pares
    cur.execute("DELETE FROM camiones WHERE id = ?", (id,))
    mysql.commit() #guardo los cambios
    cur.execute("DELETE FROM camiones WHERE id = ?", ((int(id)+1),))
    mysql.commit() #guardo los cambios
    #cargo BigTemp
    cur.execute("SELECT * FROM camiones WHERE patente = ? AND fecha = ? ORDER BY n DESC ", (Camion[2],get_fecha()))
    BigTemp = cur.fetchall()
    flash("BigBag eliminado satifactoriamente") #envia mesajes entre vistas
    mysql.close
    return render_template("/CargaBigBags.html",bigtemp=BigTemp,peso=get_data())




@app.route("/ingresarcamion")
@login_required
def ingresarcamion():
    global BigTemp
    global nelim
    global i
    global Camion
    fecha=get_fecha()
    rendered = render_template("/pdf.html",bigtemp=BigTemp,camion=Camion)
    HTML ( string = rendered ).write_pdf('./'+Camion[2]+"-"+fecha+'.pdf')
    Enviar_Email()
    return render_template("/buscar.html")
    #return render_pdf ( HTML ( string = rendered ), download_filename = hola)
    #return render_template("/buscar.html")
    


@app.route("/buscarcamion")
@login_required
def Buscarcamion():
    return render_template("/buscarbigbag.html")

@app.route("/Buscarporpatente", methods= ["POST"])
@login_required
def Buscarporpatente():
    global patente
    if request.method == "POST":
        patente = request.form["patente"]
        mysql = sqlite3.connect("./Proyecto.db")
        cur=mysql.cursor()
        cur.execute("SELECT * FROM camiones WHERE patente = ?",(patente,))
        data = cur.fetchall()
        mysql.close
        data=filtro(data)
        return render_template("/buscarbigbag.html",bigtemp=data)


@app.route("/abririnforme/<string:fecha>", methods= ["GET"])
@login_required
def abririnfrome(fecha):
    global patente
    os.startfile('C:/Users/pbertini/Desktop/Proyecto-Puente-Grua/'+patente+"-"+fecha+'.pdf')
    patente=""
    return render_template("/buscar.html",)
        
        







if __name__ == "__main__":
    app.run(port = 3000, debug = True) #hacemos que se refresque solo
