from flask import Flask, redirect, url_for, request, render_template, jsonify, render_template_string, send_file
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import datetime 
from enum import Enum
import base64
import smtplib
from email.message import EmailMessage
from sqlalchemy.orm import validates

# Configurações
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lw.db"
app.config["SECRET_KEY"] = os.urandom(24)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "/login"

# Função que limita a categoria dos veiculos ao criar os mesmos
class Categoria_Enum(Enum):
    eletrico = "Elétrico"
    prestige = "Prestige"
    descapotavel = "Descapotável"
    hypersport = "Hypersport"
    suv = "SUV"
    hyperluxury = "HyperLuxury"
    unique = "Único"
    hatchback = "Hatchback"
    hybrid = "Hybrid"
    limusine = "Limusine"
    autocaravana = "Autocaravana"
    todos = "Todos"

class Categoria_motos_Enum(Enum):
    eletrico = "Elétrico"
    prestige = "Prestige"
    chooper = "Chopper"
    naked = "Naked"
    super_sport = "Super Sport"
    tourer = "Tourer"
    atv = "ATV"
    jet_ski = "Jet Ski"
    motocross = "Motocross"
    todos = "Todos"

# Função para codificar a imagem  em Base64
def encode_image(image_binary):
    if image_binary:
        encoded_image = base64.b64encode(image_binary).decode("utf-8")
        return f"data:image/jpeg;base64,{encoded_image}"
    else:
        return None

# Base de dados "MODELOS"
class Utilizador(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(20))
    email = db.Column(db.String)
    telefone = db.Column(db.String)
    logged_in = db.Column(db.Boolean, default=False)
    data_registo = db.Column(db.DateTime, default=datetime.now)
    tipo_user = db.Column(db.String(50), default = "cliente")
    nome_cartao = db.Column(db.String(100))
    validade_cartao = db.Column(db.String(100))
    cvc = db.Column(db.String(100))
    nr_cartao = db.Column(db.String(100))
    nif = db.Column(db.String(100))
    carteira_cripto = db.Column(db.String(100)) 
    

    def __init__(self, nome, username, password, email, telefone, tipo_user, nr_cartao, nif, validade_cartao, cvc, carteira_cripto, nome_cartao):
        self.nome = nome
        self.username = username
        self.password = password
        self.email = email
        self.telefone = telefone
        self.tipo_user = tipo_user
        self.nome_cartao = nome_cartao
        self.nr_cartao = nr_cartao
        self.validade_cartao = validade_cartao
        self.cvc = cvc
        self.nif = nif
        self.carteira_cripto = carteira_cripto

class Carro(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo_de_veiculo = db.Column(db.String)
    matricula = db.Column(db.String(6), unique=True)
    marca = db.Column(db.String)
    modelo = db.Column(db.String)
    ano = db.Column(db.Integer)
    gps = db.Column(db.String(5))
    locacao = db.Column(db.Integer)
    tipo_de_caixa = db.Column(db.String)
    ac = db.Column(db.String(5))
    idade_minima = db.Column(db.Integer)
    numero_de_portas = db.Column(db.Integer)
    potencia = db.Column(db.String(10))
    autonomia = db.Column(db.String(10))
    foto_1 = db.Column(db.LargeBinary)
    foto_2 = db.Column(db.LargeBinary)
    foto_3 = db.Column(db.LargeBinary)
    foto_4 = db.Column(db.LargeBinary)
    foto_5 = db.Column(db.LargeBinary)
    foto_6 = db.Column(db.LargeBinary)
    disponivel = db.Column(db.Boolean, default=True)
    categoria = db.Column(db.Enum(Categoria_Enum, default ="todos"))
    valor_diario = db.Column(db.Float)
    data_inicio = db.Column(db.String)
    data_fim = db.Column(db.String)
    sobre = db.Column(db.String)
    servicos_adicionais = db.Column(db.String)

    def __init__(self, matricula, tipo_de_veiculo, marca, data_inicio, data_fim, modelo, ano, gps, locacao, tipo_de_caixa, ac, idade_minima, numero_de_portas, potencia, autonomia, valor_diario, sobre, servicos_adicionais, foto_1=None, foto_2=None, foto_3=None, foto_4=None, foto_5=None, foto_6=None, categoria=None):
        self.tipo_de_veiculo = tipo_de_veiculo
        self.matricula = matricula.upper()
        self.marca = marca.title()
        self.modelo = modelo.title()
        self.ano = ano
        self.gps = gps.title()
        self.locacao = locacao
        self.tipo_de_caixa = tipo_de_caixa.title()
        self.ac = ac.title()
        self.idade_minima = idade_minima
        self.numero_de_portas = numero_de_portas
        self.potencia = potencia.upper()
        self.autonomia = autonomia.upper()
        self.foto_1 = foto_1
        self.foto_2 = foto_2
        self.foto_3 = foto_3
        self.foto_4 = foto_4
        self.foto_5 = foto_5
        self.foto_6 = foto_6
        self.categoria = categoria
        self.valor_diario = valor_diario
        self.sobre = sobre
        self.servicos_adicionais = servicos_adicionais.title()
        self.data_inicio = data_inicio
        self.data_fim = data_fim

class Mota(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    tipo_de_veiculo = db.Column(db.String)
    categoria = db.Column(db.String(50))
    matricula = db.Column(db.String(6), unique = True)
    marca = db.Column(db.String)
    modelo = db.Column(db.String)
    ano = db.Column(db.Integer)
    gps = db.Column(db.String(5))
    tipo_de_caixa = db.Column(db.String)
    idade_minima = db.Column(db.Integer)
    potencia = db.Column(db.String(10))
    autonomia = db.Column(db.String(10))
    foto_1 = db.Column(db.LargeBinary)
    foto_2 = db.Column(db.LargeBinary)
    foto_3 = db.Column(db.LargeBinary)
    foto_4 = db.Column(db.LargeBinary)
    foto_5 = db.Column(db.LargeBinary)
    foto_6 = db.Column(db.LargeBinary)
    disponivel = db.Column(db.Boolean, default = True)
    categoria = db.Column(db.Enum(Categoria_motos_Enum, default ="todos"))
    data_inicio = db.Column(db.String)
    data_fim = db.Column(db.String)
    valor_diario = db.Column(db.Float)
    sobre = db.Column(db.String)
    servicos_adicionais = db.Column(db.String)

    def __init__(self, matricula, modelo,  tipo_de_veiculo, marca, data_inicio, data_fim, ano, gps, tipo_de_caixa, idade_minima, potencia, autonomia, valor_diario, sobre, servicos_adicionais, foto_1=None, foto_2=None, foto_3=None, foto_4=None, foto_5=None, foto_6=None, categoria=None):
        self.tipo_de_veiculo = tipo_de_veiculo
        self.matricula = matricula
        self.marca = marca
        self.modelo = modelo.title()
        self.ano = ano
        self.gps = gps
        self.tipo_de_caixa = tipo_de_caixa
        self.idade_minima = idade_minima
        self.potencia = potencia
        self.autonomia = autonomia
        self.valor_diario = valor_diario
        self.sobre = sobre
        self.servicos_adicionais = servicos_adicionais
        self.foto_1 = foto_1
        self.foto_2 = foto_2
        self.foto_3 = foto_3
        self.foto_4 = foto_4
        self.foto_5 = foto_5
        self.foto_6 = foto_6
        self.categoria = categoria
        self.data_inicio = data_inicio
        self.data_fim = data_fim

class Gerenciamento(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ref = db.Column(db.Integer)
    data = db.Column(db.String(10)) 
    hora = db.Column(db.String(5))
    dias_alugados = db.Column(db.Integer)
    estabelecimento_entrega = db.Column(db.String)
    estabelecimento_devolucao = db.Column(db.String)
    valor_total = db.Column(db.Float)
    matricula = db.Column(db.String)
    email = db.Column(db.String)
    nome = db.Column(db.String)

    def __init__(self, ref, data, hora, dias_alugados, estabelecimento_entrega, estabelecimento_devolucao, valor_total, matricula, email, nome):
        self.ref = ref
        self.data = data
        self.hora = hora
        self.dias_alugados = dias_alugados
        self.estabelecimento_entrega = estabelecimento_entrega
        self.estabelecimento_devolucao = estabelecimento_devolucao
        self.valor_total = valor_total
        self.matricula = matricula
        self.email = email
        self.nome = nome

# Rotas

# Carrega um usuário com base no ID fornecido pelo Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Utilizador.query.get(int(user_id))

# Valida o tipo de usuário antes de atribuí-lo ao objeto
@validates("tipo_user")
def validate_tipo_user(self, key, tipo_user):
    tipos_permitidos = ["administrador", "proprietario", "colaborador", "cliente"]
    assert tipo_user in tipos_permitidos
    return tipo_user

# Define uma rota para a raiz da aplicação
@app.route("/")
def normal():
    return redirect(url_for("home"))

# Carrega a pagina Home
@app.route("/home", methods=["GET"])
def home():
        utilizador = current_user if current_user.is_authenticated else None
        return render_template("home.html", utilizador=utilizador)

# Rota onde mostra os dados do utilizador e onde podemos alterar os dados e gravar
@app.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    if request.method == "POST":
        if "atualizar" in request.form:
            user = Utilizador.query.get(current_user.id)
            
            if request.form["nome"] != user.nome:
                user.nome = request.form["nome"]
            if request.form["nif"] != user.nif:
                user.nif = request.form["nif"]
            if request.form["email"] != user.email:
                user.email = request.form["email"]
            if request.form["contacto"] != user.telefone:
                user.telefone = request.form["contacto"]
            if request.form["password"]:
                user.password = request.form["password"]
            if db.session.dirty:
                db.session.commit()
            
            return redirect(url_for("perfil"))

    else:
        utilizador = current_user if current_user.is_authenticated else None
        return render_template("perfil.html", utilizador=utilizador)

# Aqui sõ temos o metodo POST que verifica os dados de pagamento no formulario e caso sejam diferentes guarda os novos na base de dados
@app.route("/detalhes_pagamento", methods=["POST"])
@login_required
def detalhes_pagamento():
    if request.method == "POST":
        if "detalhes_pagamento" in request.form:
            user = Utilizador.query.get(current_user.id)
            
            if request.form["nome_cartao"] != user.nome_cartao: 
                user.nome_cartao = request.form["nome_cartao"]
            if request.form["nr_cartao"] != user.nr_cartao:
                user.nr_cartao = request.form["nr_cartao"]
            if request.form["validade_cartao"] != user.validade_cartao:
                user.validade_cartao = request.form["validade_cartao"]
            if request.form["cvc"] != user.cvc:
                user.cvc = request.form["cvc"]
            if request.form["carteira_cripto"] != user.carteira_cripto:
                user.carteira_cripto = request.form["carteira_cripto"]
            if db.session.dirty:
                db.session.commit()
            
            return redirect(url_for("perfil"))

# Rota que verifica os dados de login e compara na base de dados
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
    
        user = Utilizador.query.filter_by(username=username).first()
        
        if user and user.password == password:
            login_user(user)
            user.logged_in = True
            db.session.commit()
            return redirect(url_for("home"))
        else:
            error = "Nome de usuário ou senha inválidos"
            return render_template("login.html", error=error)
        
    utilizador = current_user if current_user.is_authenticated else None
    return render_template("login.html", error="", utilizador=utilizador)

# Rota que guarda novos utilizadores na base de dados
@app.route("/registar", methods=["GET", "POST"])
def registar_usuario():
    if request.method == "POST":
        
        if "registar" in request.form:
            nome = request.form["nome"]
            email = request.form["email"]
            telefone = request.form["telefone"]
            novo_username = request.form["username"]
            nova_password = request.form["password"]
            tipo_user = request.form["tipo_user"]
            nome_cartao = request.form["nome_cartao"]
            validade_cartao = request.form["validade_cartao"]
            cvc = request.form["cvc"]
            nif = request.form["nif"]
            carteira_cripto = request.form["carteira_cripto"]
            nr_cartao = request.form["nr_cartao"]
            


            novo_utilizador = Utilizador(
                nome=nome,
                username=novo_username,
                password=nova_password,
                email=email,
                telefone=telefone,
                tipo_user="cliente",
                nome_cartao=nome_cartao,
                validade_cartao=validade_cartao,
                cvc=cvc,
                nr_cartao=nr_cartao,
                nif=nif,
                carteira_cripto=carteira_cripto
            )

            db.session.add(novo_utilizador)
            db.session.commit()

            try:
                servidor_smtp = "smtp-mail.outlook.com"
                porta_smtp = 587
                email_origem = "luxurywheels.pf@hotmail.com"  
                senha = "Alandiego1@"  
                assunto = "Confirmação de Registro"
                mensagem = f"""
                Olá {nome},

                Obrigado por se registrar em nosso site. Seus detalhes de registro foram recebidos com sucesso.

                Deixamos abaixo as suas credenciais:

                Usuario: {novo_username}
                Password: {nova_password}

                Atenciosamente,
                Sua equipe de Luxury Wheels
                """
                msg = EmailMessage()
                msg["From"] = email_origem
                msg["To"] = email
                msg["Subject"] = assunto
                msg.set_content(mensagem)
                with smtplib.SMTP(servidor_smtp, porta_smtp) as servidor:
                    servidor.starttls()
                    servidor.login(email_origem, senha)
                    servidor.send_message(msg)

            except Exception as e:
                print("Erro ao enviar email de confirmação:", str(e))

            return redirect(url_for("home"))

    else:
        utilizador = current_user if current_user.is_authenticated else None
        return render_template("registar.html", utilizador=utilizador)

# Rota que retorna todos os dados das tabelas Carro e Mota para o depois ser utilizado no front end
@app.route("/dados_veiculos")
def obter_dados_veiculos():
    carros = Carro.query.all()
    motos = Mota.query.all()
    dados_veiculos = []

    for carro in carros:
        dados_veiculos.append({
            "id": carro.id,
            "tipo_de_veiculo": "carro",
            "marca": carro.marca,
            "modelo": carro.modelo,
            "locacao": carro.locacao,
            "valor": carro.valor_diario,
            "potencia": carro.potencia,
            "ano": carro.ano,
            "idade_minima": carro.idade_minima,
            "numero_de_portas": carro.numero_de_portas,
            "disponivel": carro.disponivel,
            "categoria": carro.categoria.value,
            "data_inicio": carro.data_inicio,
            "data_fim": carro.data_fim,
        })

        for moto in motos:
            dados_veiculos.append({
                "id": moto.id,
                "tipo_de_veiculo": "moto",
                "marca": moto.marca,
                "modelo": moto.modelo,
                "valor": moto.valor_diario,
                "potencia": moto.potencia,
                "ano": moto.ano,
                "idade_minima": moto.idade_minima,
                "disponivel": moto.disponivel,
                "categoria": moto.categoria.value,
                "data_inicio": moto.data_inicio,
                "data_fim": moto.data_fim,
            })

    return jsonify(dados_veiculos)

# Rota que basicamente faz varios filtros na base de dados e carrega a rota Cars
@app.route("/cars", methods=["GET", "POST"])
def cars():
    if request.method == "POST":
        tipo_veiculo = request.form.get("tipo_veiculo")
        marca = request.form.get("marca")  

        if tipo_veiculo == "carro":
            carros_filtrados = Carro.query
            motos_filtradas = None
        elif tipo_veiculo == "moto":
            carros_filtrados = None
            motos_filtradas = Mota.query
        else:  
            carros_filtrados = Carro.query
            motos_filtradas = Mota.query

        if marca and marca != "todas":
            carros_filtrados = carros_filtrados.filter_by(marca=marca)
            motos_filtradas = motos_filtradas.filter_by(marca=marca)


        if categoria and categoria != "todas":
            carros_filtrados = carros_filtrados.filter_by(categoria=categoria)
            motos_filtradas = motos_filtradas.filter_by(categoria=categoria)

        carros_filtrados = carros_filtrados.order_by(Carro.marca).all() if carros_filtrados else []
        motos_filtradas = motos_filtradas.order_by(Mota.marca).all() if motos_filtradas else []

        return render_template("cars.html", carros=carros_filtrados, motos=motos_filtradas, encode_image=encode_image)
    else:
        categoria = request.args.get("categoria")

        if categoria and categoria != "todas":
            carros = Carro.query.filter(or_(Carro.categoria == categoria, Carro.categoria == None)).order_by(Carro.marca).all()
            motos = Mota.query.filter(or_(Mota.categoria == categoria, Mota.categoria == None)).order_by(Mota.marca).all()
        else:
            carros = Carro.query.filter(Carro.marca != None).order_by(Carro.marca).all()
            motos = Mota.query.filter(Mota.marca != None).order_by(Mota.marca).all()
            
        utilizador = current_user if current_user.is_authenticated else None
        return render_template("cars.html", carros=carros, motos=motos, encode_image=encode_image, utilizador=utilizador)

# Rota que carrega a pagina sobre-nos 
@app.route("/sobre-nos", methods=["GET"])
def sobrenos():
    utilizador = current_user if current_user.is_authenticated else None
    return render_template("sobrenos.html", utilizador=utilizador)

# Rota que  carrega a pagina de contacto, e tem um formulario que ao colocar os dados envia um email com os mesmos
@app.route("/contactos", methods=["GET", "POST"])
def contactos():
    if request.method == "POST":
        nome = request.form["nome"]
        email_destino = "luxurywheels.pf@hotmail.com"  
        assunto = "Mensagem do formulário de contato"
        mensagem = f"""
        Nome: {nome}
        E-mail: {request.form["email"]}
        Assunto: {request.form["assunto"]}
        Mensagem:
        {request.form["mensagem"]}
        """
        try:
            servidor_smtp = "smtp-mail.outlook.com"
            porta_smtp = 587
            email_origem = "luxurywheels.pf@hotmail.com"  
            senha = "Alandiego1@"  
            msg = EmailMessage()
            msg["From"] = email_origem
            msg["To"] = email_destino
            msg["Subject"] = assunto
            msg.set_content(mensagem)
            with smtplib.SMTP(servidor_smtp, porta_smtp) as servidor:
                servidor.starttls()
                servidor.login(email_origem, senha)
                servidor.send_message(msg)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
    else:
        utilizador = current_user if current_user.is_authenticated else None
        return render_template("contactos.html", utilizador=utilizador)

# Rota que faz logout dos utilizadores
@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        current_user.logged_in = False
        db.session.commit()
        logout_user()
    
    return redirect(url_for("home"))

# Rota que guarda novos veiculos na base de dados
@app.route("/guardar", methods=["GET", "POST"])
@login_required
def guardar():
    if request.method == "POST":
        tipo_veiculo = request.form["tipo_veiculo"]
        matricula = request.form["matricula"]
        marca = request.form["marca"]
        modelo = request.form["modelo"]
        ano = request.form["ano"]
        gps = request.form["gps"]
        locacao = request.form["locacao"]
        tipo_de_caixa = request.form["tipo_de_caixa"]
        ac = request.form["ac"]
        idade_minima = request.form["idade_minima"]
        numero_de_portas = request.form["numero_de_portas"]
        potencia = request.form["potencia"]
        autonomia = request.form["autonomia"]
        valor_diario = request.form["valor_diario"]
        data_inicio = request.form["data_inicio"]
        data_fim = request.form["data_fim"]
        sobre = request.form["sobre"]
        servicos_adicionais = request.form["servicos_adicionais"]

        categoria = request.form.get("categoria", "todos")

        if tipo_veiculo == "carro":
            fotos = []
            for i in range(1, 7):
                foto = request.files.get(f"foto_{i}")
                if foto:
                    foto_binaria = foto.read()
                    fotos.append(foto_binaria)
                else:
                    fotos.append(None)

            novo_carro = Carro(
                matricula=matricula,
                tipo_de_veiculo=tipo_veiculo,
                marca=marca,
                modelo=modelo,
                ano=ano,
                gps=gps,
                locacao=locacao,
                tipo_de_caixa=tipo_de_caixa,
                ac=ac,
                idade_minima=idade_minima,
                numero_de_portas=numero_de_portas,
                potencia=potencia,
                autonomia=autonomia,
                valor_diario=valor_diario,
                data_inicio=data_inicio,
                data_fim=data_fim,
                sobre=sobre,
                servicos_adicionais=servicos_adicionais,
                categoria=categoria,
                foto_1=fotos[0],
                foto_2=fotos[1],
                foto_3=fotos[2],
                foto_4=fotos[3],
                foto_5=fotos[4],
                foto_6=fotos[5],
            )
            db.session.add(novo_carro)
            db.session.commit()
        elif tipo_veiculo == "moto":
            fotos = []
            for i in range(1, 7):
                foto = request.files.get(f"foto_{i}")
                if foto:
                    foto_binaria = foto.read()
                    fotos.append(foto_binaria)
                else:
                    fotos.append(None)

            nova_mota = Mota(
                tipo_de_veiculo=tipo_veiculo,
                marca=marca,
                matricula=matricula,
                modelo=modelo,
                ano=ano,
                gps=gps,
                tipo_de_caixa=tipo_de_caixa,
                idade_minima=idade_minima,
                potencia=potencia,
                autonomia=autonomia,
                valor_diario=valor_diario,
                data_inicio=data_inicio,
                data_fim=data_fim,
                sobre=sobre,
                servicos_adicionais=servicos_adicionais,
                categoria=categoria,
                foto_1=fotos[0],
                foto_2=fotos[1],
                foto_3=fotos[2],
                foto_4=fotos[3],
                foto_5=fotos[4],
                foto_6=fotos[5],
            )
            db.session.add(nova_mota)
            db.session.commit()

        return redirect(url_for("home"))
    
    utilizador = current_user if current_user.is_authenticated else None
    return render_template("guardar.html", utilizador=utilizador)

# Rota que recebe dados do formulario de pagamento e os envia para a rota recibo
@app.route("/alugar", methods=["GET", "POST"])
def alugar_veiculo():
    if request.method == "POST":
        marca = request.form["marca"]
        modelo = request.form["modelo"]
        ano = request.form["ano"]
        potencia = request.form["potencia"]
        matricula = request.form["matricula"]
        estabelecimento_entrega = request.form["estabelecimento_entrega"]
        estabelecimento_devolucao = request.form["estabelecimento_devolucao"]
        data_inicio = request.form["dataInicio"]
        data_fim = request.form["dataFim"]
        valor_diario = request.form["valorDiario"]
        valor_total = calcular_valor_total(data_inicio, data_fim, valor_diario)
        tipo_pagamento = request.form["tipo-pagamento"]
        nome_cartao = request.form["nome_cartao"]
        nr_cartao = request.form["nr_cartao"]
        validade_cartao = request.form["validade_cartao"]
        cvc = request.form["cvc"]
        carteira_cripto = request.form["carteira_cripto"]
        network_cripto = request.form["network_cripto"]

        utilizador = current_user if current_user.is_authenticated else None
        return redirect(url_for("recibo", data_inicio=data_inicio, data_fim=data_fim, valor_diario=valor_diario, tipo_pagamento=tipo_pagamento, nome_cartao=nome_cartao, nr_cartao=nr_cartao, validade_cartao=validade_cartao, cvc=cvc, carteira_cripto=carteira_cripto, network_cripto=network_cripto, marca=marca, modelo=modelo, ano=ano, potencia=potencia, estabelecimento_devolucao=estabelecimento_devolucao, matricula=matricula, valor_total=valor_total, estabelecimento_entrega=estabelecimento_entrega, utilizador=utilizador))
    else:
        veiculo_id = request.args.get("id")   

        veiculo_carro = Carro.query.filter_by(id=veiculo_id).first()
        if veiculo_carro:
            fotos = [veiculo_carro.foto_1, veiculo_carro.foto_2, veiculo_carro.foto_3, veiculo_carro.foto_4, veiculo_carro.foto_5, veiculo_carro.foto_6]
            fotos = [foto for foto in fotos if foto]  
            utilizador = current_user if current_user.is_authenticated else None
            return render_template("alugar.html", veiculo=veiculo_carro, fotos=fotos, encode_image=encode_image, utilizador=utilizador, veiculo_id=veiculo_id)

        veiculo_mota = Mota.query.filter_by(id=veiculo_id).first()
        if veiculo_mota:
            fotos = [veiculo_mota.foto_1, veiculo_mota.foto_2, veiculo_mota.foto_3, veiculo_mota.foto_4, veiculo_mota.foto_5, veiculo_mota.foto_6]
            fotos = [foto for foto in fotos if foto] 
            utilizador = current_user if current_user.is_authenticated else None 
            return render_template("alugar.html", veiculo=veiculo_mota, fotos=fotos, encode_image=encode_image, utilizador=utilizador, veiculo_id=veiculo_id)

        return "Veículo não encontrado", 404

# Rota onde mostra os dados adiquiridos no formualario e ao confirmar os dados envia um email personalizado com os dados do recibo e uma referencia unica, e ao confirmar tambem guarda os dados na base de dados
@app.route("/recibo", methods=["GET", "POST"])
@login_required
def recibo():
    novo_registo = None

    if  request.method == "POST":
        email = request.form.get("email")
        ref = request.form.get("ref")
        data_inicio_str = request.form.get("data_inicio")
        data_fim_str = request.form.get("data_fim")
        estabelecimento_entrega = request.form.get("estabelecimento_entrega")
        estabelecimento_devolucao = request.form.get("estabelecimento_devolucao")
        valor_total = request.form.get("valor_total")
        marca = request.form.get("marca")
        modelo = request.form.get("modelo")
        matricula = request.form.get("matricula")
        ano = request.form.get("ano")
        potencia = request.form.get("potencia")
        valor_diario = request.form.get("valor_diario")
        tipo_pagamento = request.form.get("tipo_pagamento")
        nome_cartao = request.form.get("nome_cartao")
        nr_cartao = request.form.get("nr_cartao")
        validade_cartao = request.form.get("validade_cartao")
        carteira_cripto = request.form.get("carteira_cripto")
        nome = request.form.get("nome")
        nif = request.form.get("nif")
        

        data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d")
        data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d")
        dias_alugados = (data_fim - data_inicio).days
        data_atual = datetime.now()
        hora_atual = datetime.now().strftime("%H:%M")

        
        novo_registo = Gerenciamento(
            ref = ref,
            estabelecimento_entrega = estabelecimento_entrega,
            estabelecimento_devolucao = estabelecimento_devolucao,
            data=data_atual.strftime("%Y-%m-%d"),
            hora=hora_atual,
            dias_alugados = dias_alugados,
            valor_total = valor_total,
            nome = nome,
            matricula = matricula,
            email = email,
        )

        try:
            servidor_smtp = "smtp-mail.outlook.com"
            porta_smtp = 587
            email_origem = "luxurywheels.pf@hotmail.com"
            senha = "Alandiego1@" 
            assunto = "Confirmação de Reserva"
            mensagem = f"""
        <!DOCTYPE html>
<html lang="PT-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <title>Reserva Automóvel</title>
</head>
<body style="font-family: Arial, sans-serif;margin: 0;padding: 0;">
    <header style="border-bottom: #d6b884 solid 4px;padding: 20px;text-align: center;">
        <img style="max-width: 200px;display: flex;margin-left: auto;" src="https://i.postimg.cc/RVp0FwZ5/logo2.png" alt="Logo da Empresa">
    </header>
    
    <div class="container" style="max-width: 800px;margin: 20px auto;padding: 20px;">
        <h1 style="font-size: 1.7rem; color: #d6b884;">Obrigado {request.form["nome"]}! A reserva da dua viatura de sonho está confirmada.</h1>
        <p><span style="color: rgb(20, 230, 20); margin-right: 10px;font-size: 24px;font-weight: bold;" >&#10003;</span><strong>{request.form["marca"]} {request.form["modelo"]}</strong> espera por si a <strong>{request.form["data_inicio"]}.</strong></p>
        <p><span style="color: rgb(20, 230, 20); margin-right: 10px;font-size: 24px;font-weight: bold;" >&#10003;</span> Cancelamento <strong>gratuito</strong> até <strong>3 dias</strong> antes da data de recolha.</p>
        <p><span style="color: rgb(20, 230, 20); margin-right: 10px;font-size: 24px;font-weight: bold;" >&#10003;</span> Utilize o link abaixo para <strong>alterar ou cancelar</strong> facilmente a sua reserva.</p>
        <p><span style="font-size: 20px;margin-right: 10px; ">&#128274;</span>Por favor mantenha a sua <strong>referência</strong> cofidencial,  com ela é possível alterar ou cancelar a sua reserva</p>
        <h2 style="font-size: 1.2rem; margin-top: 5%; color: #d6b884;">Detalhes da sua reserva:</h2>
        <table style="width: 100%;border-collapse: collapse;margin-top: 5%;">
            <tbody>
                <tr style="background-color: #fff; color: #333;">
                    <td>Referência da Reserva:</td>
                    <td>{request.form["ref"]}</td>
                </tr>
                <tr style="background-color: #d6b884; color: #fff;">
                    <td>Data de Início:</td>
                    <td>{request.form["data_inicio"]}</td>
                </tr>
                <tr style="background-color: #fff; color: #333;">
                    <td>Data de Fim:</td>
                    <td>{request.form["data_fim"]}</td>
                </tr>
                <tr style="background-color: #d6b884; color: #fff;">
                    <td>Estabelecimento de Entrega:</td>
                    <td>{request.form["estabelecimento_entrega"]}</td>
                </tr>
                <tr style="background-color: #fff; color: #333;">
                    <td>Estabelecimento de Devolução:</td>
                    <td>{request.form["estabelecimento_devolucao"]}</td>
                </tr>
            </tbody>
        </table>
        <h2 style="font-size: 1.2rem; margin-top: 5%; color: #d6b884;">Detalhes da viatura:</h2>
        <table style="width: 100%;border-collapse: collapse;margin-top: 5%;">
            <tbody>
                <tr style="background-color: #fff; color: #333;">
                    <td>Marca:</td>
                    <td>{request.form["marca"]}</td>
                </tr>
                <tr style="background-color: #d6b884; color: #fff;">
                    <td>Modelo:</td>
                    <td>{request.form["modelo"]}</td>
                </tr>
                <tr style="background-color: #fff; color: #333;">
                    <td>Matrícula:</td>
                    <td>{request.form["matricula"]}</td>
                </tr>
                <tr style="background-color: #d6b884; color: #fff;">
                    <td>Potência:</td>
                    <td>{request.form["potencia"]}Hp</td>
                </tr>
                <tr style="background-color: #fff; color: #333;">
                    <td>Ano de Matrícula:</td>
                    <td>{request.form["ano"]}</td>
                </tr>
            </tbody>
        </table>
        <h2 style="font-size: 1.2rem; margin-top: 5%; color: #d6b884;">Dados de pagamento:</h2>
        <table style="width: 100%;border-collapse: collapse;margin-top: 5%;">
            <tbody>
                <tr style="background-color: #fff; color: #333;">
                    <td>Nome:</td>
                    <td>{request.form["nome"]}</td>
                </tr>
                <tr style="background-color: #d6b884; color: #fff;">
                    <td>NIF:</td>
                    <td>{request.form["nif"]}</td>
                </tr>
                <tr style="background-color: #fff; color: #333;">
                    <td>Método de Pagamento:</td>
                    <td>{request.form["tipo_pagamento"]}</td>
                </tr>
            </tbody>
        </table>
        <h2 style="font-size: 1.2rem; margin-top: 5%; color: #d6b884;">Detalhes do preço:</h2>
        <table style="width: 100%;border-collapse: collapse;margin-top: 5%;">
            <tbody>
                <tr style="background-color: #fff; color: #333;">
                    <td>Valor diário:</td>
                    <td>{request.form["valor_diario"]}</td>
                </tr>
                <tr style="background-color: #d6b884; color: #fff;">
                    <td>Dias alugados:</td>
                    <td>{ dias_alugados }</td>
                </tr>
                <tr style="background-color: #fff; color: #333;">
                    <td>Valor total:</td>
                    <td>{request.form["valor_total"]}</td>
                </tr>
            </tbody>
        </table>
        <p style="font-size: 1.2rem; color: #d6b884;"><i style="margin-top: 5%; margin-right: 1%; color: #631726;" class="fas fa-info-circle"></i>Informações Importantes:</p>
        <p style="font-size: 0.9rem;">• A viatura está restrita à condução exclusiva do cliente que a aluga.</p>
        <p style="font-size: 0.9rem;">• Para cancelamentos realizados após o período de três dias antes da data de início do aluguer, será aplicada uma taxa equivalente a 30% do valor diário multiplicado pela metade dos dias originalmente contratados.</p>
        <a style="text-decoration: none;color: #0071c2; font-size: 0.9rem; font-weight: 600;" href="http://127.0.0.1:5000//termos-condicoes">• Para mais informações por favor acesse ao nosso site</a>
        <h2 style="font-size: 1.1rem; color: #d6b884; margin-top: 5%;">Faça alterações na sua reserva</h2>
        <div style="display: flex; align-items: center;">
            <p style="font-size: 0.9rem; display: flex; align-items: center;">
                <img style="width: 50px; margin-right: 2%;" src="https://i.postimg.cc/yxKQq1Wj/calendar.png" alt="calendario">
                É simples alterar ou cancelar a sua reserva. Dependendo das condições da reserva efetuada, podem aplicar-se custos de cancelamento.
            </p>
        </div>
        <a style="text-decoration: none;color: #0071c2; font-size: 0.9rem; font-weight: 600; display: flex; justify-content: center; " href="http://127.0.0.1:5000//alterar-reserva">Alterar ou cancelar a sua reserva »</a>        
        <h2 style="font-size: 1.1rem; color: #d6b884; margin-top: 5%;">Entre em contacto</h2>
        <div style="display: flex; align-items: center;">
            <p style="font-size: 0.9rem; display: flex; align-items: center;">
                <img style="width: 50px; margin-right: 2%; height: 50px;" src="https://i.postimg.cc/kXQtnLy2/chat.png" alt="chat">
                Tem uma questão ou pedido especial? Por favor contacnos pelos nossos meios de comunicação.<br>
                <br>
                • Telefone: +351 xxx xxx xxx
            </p>
        </div>
        <a style="text-decoration: none;color: #0071c2; font-size: 0.9rem; font-weight: 600; display: flex; justify-content: center; " href="http://127.0.0.1:5000//contactos">Formulário de contacto »</a>  
    </div>
    
    <footer style="background-color: #fff;color: #631726;padding: 20px;border-top: #d6b884 solid 4px;font-size: 0.9rem;">
        <div style="display: flex; justify-content: center; align-items: center; gap: 150px;margin-right: 100px;">
            <div>
                <img src="https://i.postimg.cc/RVp0FwZ5/logo2.png" alt="Logotipo">
                <p style="font-size: 1.2rem; color: #631726; font-weight: bold;">Copyright &copy; 2024 Luxury Wheels</p>
                <div style="margin-right: 10px;">
                    <a style="margin-right: 15%;" href="https://www.facebook.com" id="facebook" ><img src="https://i.postimg.cc/rs9yRfzj/face.png" alt="Facebook logo" class="rede-social"></a>
                    <a style="margin-right: 15%;" href="https://www.instagram.com" id="instagram"><img src="https://i.postimg.cc/Z5np8MpC/insta.png" alt="Instagram logo" class="rede-social"></a>
                    <a style="margin-right: 15%;" href="https://www.youtube.com" id="youtube"><img src="https://i.postimg.cc/vmv82QWh/youtube.png" alt="Youtube logo" class="rede-social"></a>
                </div>
            </div>
            <div style="margin-top: 40px;  margin-left: auto;">
                <p>Para mais informações, entre em contato:</p>
                <p>Sua referência: {request.form["ref"]}</p>
                <p>Email: Luxurywheels.pf@hotmail.com</p>
                <p>Website: www.luxurywheels.com</p>
            </div>
        </div>
    </footer>
</body>
</html>
"""
            
            destinatario_adicional = "luxurywheels.pf@hotmail.com"
            msg = EmailMessage()
            msg["From"] = email_origem
            msg["To"] = ", ".join([email, destinatario_adicional])
            msg["Subject"] = assunto
            msg.add_alternative(mensagem, subtype="html")  
            with smtplib.SMTP(servidor_smtp, porta_smtp) as servidor:
                servidor.starttls()
                servidor.login(email_origem, senha)
                servidor.send_message(msg)

            db.session.add(novo_registo)
            db.session.commit()

            carro = Carro.query.filter_by(matricula = matricula).first()
            if carro:
                carro.data_inicio = data_inicio_str
                carro.data_fim = data_fim_str
                db.session.commit()
            else:
                mota = Mota.query.filter_by(matricula = matricula).first()
                if mota:
                    mota.data_inicio = data_inicio_str
                    mota.data_fim = data_fim_str
                    db.session.commit()

            return redirect(url_for("home"))
        
        except Exception as e:
            print("Erro ao processar o pedido:", str(e))

    else:
        marca = request.args.get("marca")
        modelo = request.args.get("modelo")
        ano = request.args.get("ano")
        potencia = request.args.get("potencia")
        matricula = request.args.get("matricula")
        estabelecimento_entrega = request.args.get("estabelecimento_entrega")
        estabelecimento_devolucao = request.args.get("estabelecimento_devolucao")
        data_inicio = request.args.get("data_inicio")
        data_fim = request.args.get("data_fim")
        valor_diario = request.args.get("valor_diario")
        tipo_pagamento = request.args.get("tipo_pagamento")
        nome_cartao = request.args.get("nome_cartao")
        nr_cartao = request.args.get("nr_cartao")
        validade_cartao = request.args.get("validade_cartao")
        cvc = request.args.get("cvc")
        carteira_cripto = request.args.get("carteira_cripto")
        network_cripto = request.args.get("network_cripto")
        valor_total = request.args.get("valor_total")

        return render_template("recibo.html", novo_registo=novo_registo, data_inicio=data_inicio, data_fim=data_fim, valor_diario=valor_diario, tipo_pagamento=tipo_pagamento, nome_cartao=nome_cartao, nr_cartao=nr_cartao, validade_cartao=validade_cartao, cvc=cvc, carteira_cripto=carteira_cripto, network_cripto=network_cripto, marca=marca, modelo=modelo, ano=ano, potencia=potencia, estabelecimento_devolucao=estabelecimento_devolucao, matricula=matricula, valor_total=valor_total, estabelecimento_entrega=estabelecimento_entrega, utilizador=current_user)

# Rota que permite pesquisa pela referencia colocado no formualario do front end
@app.route("/alterar-reserva", methods=["GET", "POST"])
@login_required
def alterar_reserva():
    if request.method == "POST":
        ref = request.form.get("ref")
        gerenciamento = Gerenciamento.query.filter(Gerenciamento.ref == ref).first()

    utilizador = current_user if current_user.is_authenticated else None
    return render_template("alterar_reserva.html", utilizador=utilizador)

# Rota que compara a referencia  do formulario com os dados da base de dados e caso exista envia dados para o front end
@app.route("/verificar-reserva", methods=["POST"])
def verificar_reserva():
    ref = request.json.get("ref")
    gerenciamento = Gerenciamento.query.filter(Gerenciamento.ref == ref).first()
    if gerenciamento:
        return jsonify({
            "ref": gerenciamento.ref,
            "matricula": gerenciamento.matricula,
        })
    else:
        return jsonify(None)

# Rota que ao encontrar a referencia pesquisa pela matricula que esta associada a mesma e mostra dados especificos da base de dados
@app.route("/buscar-veiculo", methods=["POST"])
def buscar_veiculo():
    ref = request.json.get("ref")
    gerenciamento = Gerenciamento.query.filter(Gerenciamento.ref == ref).first()
    
    if gerenciamento:
        carro = Carro.query.filter_by(matricula=gerenciamento.matricula).first()
        mota = Mota.query.filter_by(matricula=gerenciamento.matricula).first()

        if carro:
            return jsonify({
                "tipo": "carro",
                "marca": carro.marca,
                "modelo": carro.modelo,
                "ref": gerenciamento.ref,
                "matricula": gerenciamento.matricula,
                "data_inicio": carro.data_inicio,
                "data_fim": carro.data_fim,
            })
        elif mota:
            return jsonify({
                "tipo": "mota",
                "marca": mota.marca,
                "modelo": mota.modelo,
                "ref": gerenciamento.ref,
                "matricula": gerenciamento.matricula,
                "data_inicio": mota.data_inicio,
                "data_fim": mota.data_fim,
            })

    return jsonify(None)

# Rota que atualiza as datas da reserva e pode cancelar as mesmas
@app.route("/atualizar-reserva", methods=["POST"])
def atualizar_reserva():
    ref = request.form.get("ref")
    matricula = request.form.get("matricula")
    nova_data_inicio = request.form.get("novaDataInicio")
    nova_data_fim = request.form.get("novaDataFim")

    carro = Carro.query.filter_by(matricula=matricula).first()
    if carro:
        carro.data_inicio = nova_data_inicio
        carro.data_fim = nova_data_fim
        db.session.commit()
        return redirect(url_for("home"))
    else:
        mota = Mota.query.filter_by(matricula=matricula).first()
        if mota:
            mota.data_inicio = nova_data_inicio
            mota.data_fim = nova_data_fim
            db.session.commit()
            return redirect(url_for("home"))
        else:
            return jsonify({"error": "Veículo não encontrado."}), 404

# Rota que carrega a pagina termos e condicoes
@app.route("/termos-condicoes", methods=["GET"])
def termos_condicoes():
    utilizador = current_user if current_user.is_authenticated else None
    return render_template("termos_condicoes.html", utilizador=utilizador)

# Rota que carrega a pagina politicas de privacidade
@app.route("/politicas-de-privacidade", methods=["GET"])
def politicas():
    utilizador = current_user if current_user.is_authenticated else None
    return render_template("politicas.html", utilizador=utilizador)

# Rota que carrega a pagina de servicos e extras
@app.route("/servicos-extras", methods=["GET"])
def servicos_extras():
    utilizador = current_user if current_user.is_authenticated else None
    return render_template("servicos_extras.html", utilizador=utilizador)

# Rota que carrega a pagina de como funicona o programa
@app.route("/como-funciona", methods=[ "GET"])
def como_funciona():
    utilizador = current_user if current_user.is_authenticated else None
    return render_template("ajuda.html", utilizador=utilizador)

# Rota que calcula a diferenca de dias entre o inicio e o fim da reserva e faz o calculo total da reserva
def calcular_valor_total(data_inicio, data_fim, valor_diario):
    data_inicio_obj = datetime.strptime(data_inicio, "%Y-%m-%d")
    data_fim_obj = datetime.strptime(data_fim, "%Y-%m-%d")
    diferenca_dias = (data_fim_obj - data_inicio_obj).days
    valor_total = float(valor_diario) * diferenca_dias
    
    return valor_total

# Rota que cria um utilizador do tipo administrador
def criar_usuario_administrador():
    admin_existente = Utilizador.query.filter_by(username="admin").first()
    print("Administrador, já existe.")
    if not admin_existente:
        novo_admin = Utilizador(
            nome="Administrador",
            username="admin",
            password="admin",
            email="",  
            telefone="",  
            tipo_user="administrador",
            nr_cartao="",  
            nif="",  
            validade_cartao="",  
            cvc="",  
            carteira_cripto="",
            nome_cartao = ""    
        )
        db.session.add(novo_admin)
        db.session.commit()
        print("Administrador, criado com sucesso.")

# Rota que cria um utilizador do tipo proprietario
def criar_usuario_proprietario():
    prop_existente = Utilizador.query.filter_by(username="prop").first()
    print("Proprietário, já existe.")
    if not prop_existente:
        novo_prop = Utilizador(
            nome="Proprietário",
            username="prop",
            password="prop",
            email="",  
            telefone="",  
            tipo_user="proprietario",
            nr_cartao="",  
            nif="",  
            validade_cartao="",  
            cvc="",  
            carteira_cripto="",
            nome_cartao = ""  
        )
        db.session.add(novo_prop)
        db.session.commit()
        print("Proprietário, criado com sucesso.")

# Codigo Run
if __name__ == "__main__":
    with app.app_context():
        criar_usuario_administrador()
        criar_usuario_proprietario()
    app.run(host="0.0.0.0", port=5000, debug=True)  
