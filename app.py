from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__) # Server
app.config['SQLALCHEMY_DATABASE_URI'] = "C://Users//KorpuZ//Desktop//Projetofinal//database//database.db" # Path to the database
db = SQLAlchemy(app) # Cursor

