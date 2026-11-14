# clientes/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_connection
import mysql.connector

clientes_bp = Blueprint('clientes', __name__, template_folder='templates')


@clientes_bp.route('/clientes')
def listar():
    conn = None
    cursor = None
    clientes = []
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM clientes ORDER BY nome')
        clientes = cursor.fetchall()
    except mysql.connector.Error as e:
        flash(f'Erro ao buscar clientes: {e}', 'danger')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    # CORRIGIDO: nome real do arquivo em clientes/templates/
    return render_template('lista_cliente.html', clientes=clientes)


@clientes_bp.route('/clientes/novo', methods=['GET', 'POST'])
def novo():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        # Campos vazios viram NULL (evita conflito se email/cpf forem UNIQUE)
        email = request.form.get('email', '').strip() or None
        telefone = request.form.get('telefone', '').strip() or None
        cpf = request.form.get('cpf', '').strip() or None

        if not nome:
            flash('O nome é obrigatório.', 'danger')
            return render_template('form_cliente.html', cliente=request.form)

        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = '''INSERT INTO clientes (nome, email, telefone, cpf)
                     VALUES (%s, %s, %s, %s)'''
            cursor.execute(sql, (nome, email, telefone, cpf))
            conn.commit()
            flash('Cliente cadastrado com sucesso!', 'success')
            return redirect(url_for('clientes.listar'))
        except mysql.connector.Error as e:
            flash(f'Erro ao cadastrar cliente: {e}', 'danger')
            # Mantém o que o usuário digitou no formulário
            return render_template('form_cliente.html', cliente=request.form)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('form_cliente.html', cliente=None)


@clientes_bp.route('/clientes/<int:id>/editar', methods=['GET', 'POST'])
def editar(id):
    conn = None
    cursor = None
    cliente = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':
            nome = request.form.get('nome', '').strip()
            email = request.form.get('email', '').strip() or None
            telefone = request.form.get('telefone', '').strip() or None
            cpf = request.form.get('cpf', '').strip() or None

            if not nome:
                flash('O nome é obrigatório.', 'danger')
                return redirect(url_for('clientes.editar', id=id))

            sql = '''UPDATE clientes
                     SET nome=%s, email=%s, telefone=%s, cpf=%s
                     WHERE id=%s'''
            cursor.execute(sql, (nome, email, telefone, cpf, id))
            conn.commit()
            flash('Cliente atualizado com sucesso!', 'success')
            return redirect(url_for('clientes.listar'))

        # Se não for POST é GET: busca o registro para o formulário
        cursor.execute('SELECT * FROM clientes WHERE id = %s', (id,))
        cliente = cursor.fetchone()

        if not cliente:
            flash('Cliente não encontrado.', 'danger')
            return redirect(url_for('clientes.listar'))

    except mysql.connector.Error as e:
        flash(f'Erro: {e}', 'danger')
        return redirect(url_for('clientes.listar'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # CORRIGIDO: render_templates -> render_template, e nome real do arquivo
    return render_template('form_cliente.html', cliente=cliente)


@clientes_bp.route('/clientes/<int:id>/excluir', methods=['POST'])
def excluir(id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM clientes WHERE id = %s', (id,))
        conn.commit()
        flash('Cliente excluído com sucesso!', 'success')
    except mysql.connector.Error as e:
        flash(f'Erro ao excluir cliente: {e}', 'danger')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return redirect(url_for('clientes.listar'))