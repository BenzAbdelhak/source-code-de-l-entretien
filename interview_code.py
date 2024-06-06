from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///personnes.db'
db = SQLAlchemy(app)

class Personne(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    date_naissance = db.Column(db.DateTime, nullable=False)

    @property
    def age(self):
        today = datetime.today()
        return today.year - self.date_naissance.year - ((today.month, today.day) < (self.date_naissance.month, self.date_naissance.day))

@app.route('/personnes', methods=['GET'])
def get_personnes():
    personnes = Personne.query.order_by(Personne.nom).all()
    personnes_data = []
    for personne in personnes:
        personnes_data.append({
            'id': personne.id,
            'nom': personne.nom,
            'prenom': personne.prenom,
            'age': personne.age
        })
    return jsonify(personnes_data)

@app.route('/personnes', methods=['POST'])
def add_personne():
    data = request.json
    try:
        personne = Personne(
            nom=data['nom'],
            prenom=data['prenom'],
            date_naissance=datetime.strptime(data['date_naissance'], '%Y-%m-%d')
        )
        if personne.age >= 150:
            return jsonify({'error': 'La personne ne peut pas avoir plus de 150 ans.'}), 400
        db.session.add(personne)
        db.session.commit()
        return jsonify({'message': 'Personne ajoutée avec succès!'}), 201
    except KeyError:
        return jsonify({'error': 'Données invalides'}), 400
    except IntegrityError:
        return jsonify({'error': 'La personne existe déjà'}), 400

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
