import os
import sys
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_connection
import mysql.connector

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

vendas_bp = Blueprint('vendas', __name__, url_prefix='/vendas', template_folder='templates')


@vendas_bp.route('/')
def listar_vendas():
    conn = None
    cursor = None
    vendas = []
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        # Busca apenas as colunas existentes em vendas e junta com clientes
        query = """
            SELECT v.id, v.data_venda, v.total AS valor_total, c.nome AS cliente_nome
            FROM vendas v
            LEFT JOIN clientes c ON v.id_cliente = c.id
            ORDER BY v.id DESC
        """
        cursor.execute(query)
        vendas = cursor.fetchall()
    except Exception as e:
        flash(f'Erro ao procurar vendas: {e}', 'danger')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return render_template('lista_vendas.html', vendas=vendas)


@vendas_bp.route('/nova', methods=['GET', 'POST'])
def nova_venda():
    conn = None
    cursor = None
    if request.method == 'POST':
        id_cliente = request.form.get('id_cliente')
        data_venda = request.form.get('data_venda') or date.today()
        valor_total = request.form.get('total') or request.form.get('valor_total') or 0

        produtos_ids = request.form.getlist('produto_id[]')
        quantidades = request.form.getlist('quantidade[]')
        precos = request.form.getlist('preco_unit[]')

        if not id_cliente:
            flash('Selecione um cliente obrigatório.', 'warning')
            return redirect(url_for('vendas.nova_venda'))

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Grava cabeçalho da venda (sem v.id_produto)
            query_venda = """
                INSERT INTO vendas (id_cliente, data_venda, total)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query_venda, (id_cliente, data_venda, valor_total))
            venda_id = cursor.lastrowid

            # Grava os itens na tabela itens_venda
            if produtos_ids:
                query_item = """
                    INSERT INTO itens_venda (id_venda, id_produto, quantidade, preco_unitario)
                    VALUES (%s, %s, %s, %s)
                """
                for prod_id, qtd, preco in zip(produtos_ids, quantidades, precos):
                    if prod_id:
                        cursor.execute(query_item, (venda_id, prod_id, qtd, preco))

            conn.commit()
            flash('Venda registrada com sucesso!', 'success')
            return redirect(url_for('vendas.listar_vendas'))
        except Exception as e:
            if conn:
                conn.rollback()
            flash(f'Erro ao registrar venda: {e}', 'danger')
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # GET: Carrega clientes e produtos
    clientes = []
    produtos = []
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id, nome FROM clientes ORDER BY nome')
        clientes = cursor.fetchall()
        cursor.execute('SELECT id, nome, preco, codigo FROM produtos ORDER BY nome')
        produtos = cursor.fetchall()
    except Exception as e:
        flash(f'Erro ao carregar dados: {e}', 'danger')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('form_vendas.html', clientes=clientes, produtos=produtos)


@vendas_bp.route('/<int:id>')
def detalhe_venda(id):
    conn = None
    cursor = None
    venda = None
    itens = []
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Cabeçalho da venda
        query_venda = """
            SELECT v.id, v.data_venda, v.total AS valor_total, c.nome AS cliente_nome
            FROM vendas v
            LEFT JOIN clientes c ON v.id_cliente = c.id
            WHERE v.id = %s
        """
        cursor.execute(query_venda, (id,))
        venda = cursor.fetchone()

        if not venda:
            flash('Venda não encontrada.', 'danger')
            return redirect(url_for('vendas.listar_vendas'))

        # Itens associados na tabela itens_venda
        query_itens = """
            SELECT iv.quantidade, iv.preco_unitario, p.nome AS produto_nome, p.codigo AS codigo_barras
            FROM itens_venda iv
            LEFT JOIN produtos p ON iv.id_produto = p.id
            WHERE iv.id_venda = %s
        """
        cursor.execute(query_itens, (id,))
        itens = cursor.fetchall()

    except Exception as e:
        flash(f'Erro ao carregar detalhes da venda: {e}', 'danger')
        return redirect(url_for('vendas.listar_vendas'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('detalhe_venda.html', venda=venda, itens=itens)


@vendas_bp.route('/<int:id>/excluir', methods=['POST'])
def excluir_venda(id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM itens_venda WHERE id_venda = %s', (id,))
        cursor.execute('DELETE FROM vendas WHERE id = %s', (id,))
        conn.commit()
        flash('Venda excluída com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir venda: {e}', 'danger')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return redirect(url_for('vendas.listar_vendas'))