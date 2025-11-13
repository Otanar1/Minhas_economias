from flask import Blueprint, render_template, session, redirect, url_for, flash

analysis_bp = Blueprint('analysis', __name__, template_folder='../templates')

@analysis_bp.route('/')
def index():
    """
    Renderiza a página principal de análise.
    """
    if 'user_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('auth.login'))

    return render_template('analysis/index.html')
