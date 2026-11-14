# dashboard/routes.py
from flask import Blueprint, render_template, flash
from database import get_connection
import mysql.connector

dashboard_bp = Blueprint('dashboard', __name__, template_folder='templates')

TABELAS = {
    'clientes': 'clientes',
    'categorias': 'categorias',
    'produtos': 'produtos',
    'vendas': 'vendas',
}


@dashboard_bp.route('/')
def index():
    conn = None
    cursor = None
    totais = {chave: 0 for chave in TABELAS}
    try:
        conn = get_connection()
        cursor = conn.cursor()
        for chave, tabela in TABELAS.items():
            cursor.execute(f'SELECT COUNT(*) FROM {tabela}')
            totais[chave] = cursor.fetchone()[0]
    except mysql.connector.Error as e:
        flash(f'Erro ao carregar dashboard: {e}', 'danger')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('index.html', totais=totais)