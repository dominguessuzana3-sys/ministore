from flask import Flask
from dashboard.routes import dashboard_bp
from clientes.routes import clientes_bp
from categorias.routes import categorias_bp
from produtos.routes import produtos_bp
from vendas.routes import vendas_bp

app = Flask(__name__)
app.secret_key = 'chave_secreta_para_mensagens_flash'

app.register_blueprint(dashboard_bp)
app.register_blueprint(clientes_bp)
app.register_blueprint(categorias_bp)
app.register_blueprint(produtos_bp)
app.register_blueprint(vendas_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)