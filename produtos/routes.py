import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import get_connection
from flask import Blueprint, flash, redirect, render_template, request, url_for
import mysql.connector

produtos_bp = Blueprint(
    'produtos', __name__, url_prefix='/produtos', template_folder='templates'
)


def buscar_categorias():
  conn = None
  cursor = None
  categorias = []
  try:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, nome FROM categorias ORDER BY nome')
    categorias = cursor.fetchall()
  except mysql.connector.Error as e:
    flash(f'Erro ao carregar categorias: {e}', 'danger')
  finally:
    if cursor:
      cursor.close()
    if conn:
      conn.close()
  return categorias


@produtos_bp.route('/')
def listar():
  conn = None
  cursor = None
  produtos = []
  try:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    sql = """
            SELECT p.*, c.nome AS categoria_nome
            FROM produtos p
            LEFT JOIN categorias c ON p.id_categoria = c.id
            ORDER BY p.nome
        """
    cursor.execute(sql)
    produtos = cursor.fetchall()
  except mysql.connector.Error as e:
    flash(f'Erro ao procurar produtos: {e}', 'danger')
  finally:
    if cursor:
      cursor.close()
    if conn:
      conn.close()
  return render_template('lista_produtos.html', produtos=produtos)


@produtos_bp.route('/novo', methods=['GET', 'POST'])
def novo():
  if request.method == 'POST':
    codigo = request.form.get('codigo') or None
    nome = request.form.get('nome')
    preco = request.form.get('preco') or 0.00
    id_categoria = request.form.get('id_categoria') or None

    conn = None
    cursor = None
    try:
      conn = get_connection()
      cursor = conn.cursor()
      sql = """
                INSERT INTO produtos (codigo, nome, preco, id_categoria)
                VALUES (%s, %s, %s, %s)
            """
      cursor.execute(sql, (codigo, nome, preco, id_categoria))
      conn.commit()
      flash('Produto cadastrado com sucesso!', 'success')
      return redirect(url_for('produtos.listar'))
    except mysql.connector.Error as e:
      flash(f'Erro ao cadastrar produto: {e}', 'danger')
    finally:
      if cursor:
        cursor.close()
      if conn:
        conn.close()

  return render_template(
      'form_produtos.html', produto=None, categorias=buscar_categorias()
  )


@produtos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
def editar(id):
  conn = None
  cursor = None
  try:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
      codigo = request.form.get('codigo') or None
      nome = request.form.get('nome')
      preco = request.form.get('preco') or 0.00
      id_categoria = request.form.get('id_categoria') or None

      sql = """
                UPDATE produtos
                SET codigo=%s, nome=%s, preco=%s, id_categoria=%s
                WHERE id=%s
            """
      cursor.execute(sql, (codigo, nome, preco, id_categoria, id))
      conn.commit()
      flash('Produto atualizado com sucesso!', 'success')
      return redirect(url_for('produtos.listar'))

    cursor.execute('SELECT * FROM produtos WHERE id = %s', (id,))
    produto = cursor.fetchone()

    if not produto:
      flash('Produto não encontrado.', 'danger')
      return redirect(url_for('produtos.listar'))

  except mysql.connector.Error as e:
    flash(f'Erro: {e}', 'danger')
    return redirect(url_for('produtos.listar'))
  finally:
    if cursor:
      cursor.close()
    if conn:
      conn.close()

  return render_template(
      'form_produtos.html', produto=produto, categorias=buscar_categorias()
  )


@produtos_bp.route('/<int:id>/excluir', methods=['POST'])
def excluir(id):
  conn = None
  cursor = None
  try:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM produtos WHERE id = %s', (id,))
    conn.commit()
    flash('Produto excluído com sucesso!', 'success')
  except mysql.connector.Error as e:
    flash(f'Erro ao excluir produto: {e}', 'danger')
  finally:
    if cursor:
      cursor.close()
    if conn:
      conn.close()
  return redirect(url_for('produtos.listar'))