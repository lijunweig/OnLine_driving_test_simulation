from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
import bleach
from flask import current_app, request
from flask_login import UserMixin, AnonymousUserMixin
from . import db


# using binary system and bitwise, for future modify
class Permission:
    TEST = 1
    WRITE = 2
    GRADE = 4
    MODERATE = 8
    ADMIN = 16


class Question_type:
    SUBJECT_1 = 1
    SUBJECT_2 = 2


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.TEST, Permission.GRADE],
            'Administrator': [Permission.WRITE, Permission.GRADE,
                              Permission.MODERATE, Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    answer_papers = db.relationship('Answer_paper', backref='user')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Answer_paper(db.Model):
    __tablename__ = 'answer_papers'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    exam_paper_id = db.Column(db.Integer, db.ForeignKey('exam_papers.id'))
    answer = db.Column(db.String(128))


registration = db.Table('registrations',
                        db.Column('question_id', db.Integer, db.ForeignKey('questions.id')),
                        db.Column('exam_paper_id', db.Integer, db.ForeignKey('exam_papers.id')))


class Exam_paper(db.Model):
    __tablename__ = 'exam_papers'
    id = db.Column(db.Integer, primary_key=True)
    question_type = db.Column(db.Integer)
    duration = db.Column(db.Integer)


class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    question_type = db.Column(db.Integer, index=True)
    text = db.Column(db.Text)
    answer = db.Column(db.String(16), index=True)
    analysis = db.Column(db.Text)
    expose_times = (db.Integer)
    right_times = (db.Integer)
    wrong_times = (db.Integer)
    exam_papers = db.relationship('Exam_paper',
                                  secondary=registration,
                                  backref=db.backref('questions', lazy='dynamic'),
                                  lazy='dynamic')
