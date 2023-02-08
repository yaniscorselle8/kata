from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy.exc import SQLAlchemyError
from datetime import date

app = Flask(__name__)

if __name__ == '__main__':
  app.run(debug=True)
  
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)

class BankAccount(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  type = db.Column(db.String(20), unique=False, nullable=False)
  surname = db.Column(db.String(20), unique=False, nullable=False)
  creationDate = db.Column(db.String(20), unique=False, nullable=False)
  modificationDate = db.Column(db.String(20), unique=False, nullable=False)
  userId = db.Column(db.Integer, unique=False, nullable=False)
  amount = db.Column(db.Integer, unique=False, nullable=False)

  def __init__(self, type, surname, creationDate, modificationDate, userId, amount):
    self.type = type
    self.surname = surname
    self.creationDate = creationDate
    self.modificationDate = modificationDate
    self.userId = userId
    self.amount = amount

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  cin = db.Column(db.Integer, unique=False, nullable=False)
  name = db.Column(db.String(20), unique=False, nullable=False)
  surname = db.Column(db.String(20), unique=False, nullable=False)
  dateOfBirth = db.Column(db.String(20), unique=False, nullable=False)
  creationDate = db.Column(db.String(20), unique=False, nullable=False)
  modificationDate = db.Column(db.String(20), unique=False, nullable=False)
  jobTitle = db.Column(db.String(20), unique=False, nullable=False)

  def __init__(self, cin, name, surname, dateOfBirth, creationDate, modificationDate, jobTitle):
    self.cin = cin
    self.name = name
    self.surname = surname
    self.dateOfBirth = dateOfBirth
    self.creationDate = creationDate
    self.modificationDate = modificationDate
    self.jobTitle = jobTitle

class Operation(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  type = db.Column(db.String(20), unique=False, nullable=False)
  amount = db.Column(db.Integer, unique=False, nullable=False)
  executionDate = db.Column(db.String(20), unique=False, nullable=False)
  realDate = db.Column(db.String(20), unique=False, nullable=False)
  userFrom = db.Column(db.Integer, unique=False, nullable=False)
  accountFrom = db.Column(db.Integer, unique=False, nullable=False)

  def __init__(self, type, amount, executionDate, realDate, userFrom, accountFrom):
    self.type = type
    self.amount = amount
    self.executionDate = executionDate
    self.realDate = realDate
    self.userFrom = userFrom
    self.accountFrom = accountFrom

db.create_all()

@app.route('/api/v1/deposit', methods=['PUT'])
def deposit():
  body = request.get_json()
  modificationDate = date.today()
  amount = int(get_amount(body['account_id'])) + int(body['deposit'])
  try:   
    db.session.query(BankAccount).filter_by(id=body['account_id']).update(
      dict(modificationDate=modificationDate, amount=amount))
    db.session.commit()
    new_operation("deposit", amount, body['user_id'], body['account_id'])
    return "The deposit have been done"
  except SQLAlchemyError as e:
    error = str(e.__dict__['orig'])
    return error

@app.route('/api/v1/withdrawal', methods=['PUT'])
def withdrawal():
  body = request.get_json()
  modificationDate = date.today()
  amount = int(get_amount(body['account_id'])) - int(body['deposit']) 
  account = BankAccount.query.filter_by(id=body['account_id']).first()
  if not account:
      return 'Account not found', 404
  if account.amount > amount:
    try:   
      db.session.query(BankAccount).filter_by(id=body['account_id']).update(
        dict(modificationDate=modificationDate, amount=amount))
      db.session.commit()
      new_operation("withdrawal", amount, body['user_id'], body['account_id'])
      return "The withdrawal have been done"
    except SQLAlchemyError as e:
      error = str(e.__dict__['orig'])
      return error
  else:
    return "You doesn't have enough monet", 400

@app.route('/api/v1/history/<id>', methods=['GET'])
def history():
  try:
    operation = Operation.query.get(id)
    del operation.__dict__['_sa_instance_state'] #TypeError: Object of type 'InstanceState' is not JSON serializable
    return jsonify(operation.__dict__)
  except SQLAlchemyError as e:
    error = str(e.__dict__['orig'])
    return error
  
@app.route('/api/v1/create-user', methods=['POST'])
def create_user():
  body = request.get_json()
  creationDate = date.today()
  modificationDate = date.today()
  try:   
    db.session.add(User(body['cin'], body['name'], body['surname'], body['dateOfBirth'], creationDate, modificationDate, body['jobTitle']))
    db.session.commit()
    return "User created"
  except SQLAlchemyError as e:
    error = str(e.__dict__['orig'])
    return error
  
@app.route('/api/v1/create-account', methods=['POST'])
def create_account():
  body = request.get_json()
  creationDate = date.today()
  modificationDate = date.today()
  try:   
    db.session.add(BankAccount(body['type'], body['surname'], creationDate, modificationDate, body['userId'], body['amount']))
    db.session.commit()
    return "Account created"
  except SQLAlchemyError as e:
    error = str(e.__dict__['orig'])
    return error

def get_amount(id):
  try:
    bankAccount = BankAccount.query.get(id)
    return bankAccount.__dict__['amount']
  except SQLAlchemyError as e:
    error = str(e.__dict__['orig'])
    return error

def new_operation(type, amount, userFrom, accountFrom):
  executionDate = date.today()
  realDate = date.today()
  try:   
    db.session.add(Operation(type, amount, executionDate, realDate, userFrom, accountFrom))
    db.session.commit()
    return "Operation created"
  except SQLAlchemyError as e:
    error = str(e.__dict__['orig'])
    return error
  
@app.route('/api/v1/accounts', methods=['GET'])
def get_accounts():
  bankAccounts = []
  try:
    for bankAccount in db.session.query(BankAccount).all():
      del bankAccount.__dict__['_sa_instance_state'] #TypeError: Object of type 'InstanceState' is not JSON serializable
      bankAccounts.append(bankAccount.__dict__)
    return jsonify(bankAccounts)
  except SQLAlchemyError as e:
    error = str(e.__dict__['orig'])
    return error
  
@app.route('/api/v1/users', methods=['GET'])
def get_users():
  users = []
  try:
    for user in db.session.query(User).all():
      del user.__dict__['_sa_instance_state'] #TypeError: Object of type 'InstanceState' is not JSON serializable
      users.append(user.__dict__)
    return jsonify(users)
  except SQLAlchemyError as e:
    error = str(e.__dict__['orig'])
    return error