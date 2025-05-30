import sys
sys.path.insert(0, '.')
from src.main import app, db, User
from werkzeug.security import generate_password_hash
import datetime

with app.app_context():
    # Verificar se já existe o usuário
    user = User.query.filter_by(email='renatolelias@gmail.com').first()
    if not user:
        # Criar usuário de teste
        test_user = User(
            name='Usuário de Teste',
            email='renatolelias@gmail.com',
            password=generate_password_hash('teste123'),
            created_at=datetime.datetime.utcnow()
        )
        db.session.add(test_user)
        db.session.commit()
        print("Usuário criado com sucesso!")
    else:
        print("Usuário já existe!")
