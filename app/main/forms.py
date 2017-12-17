from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, \
    SubmitField, FileField, RadioField,HiddenField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError
from flask_pagedown.fields import PageDownField
from ..models import Role, User
from flask_wtf.file import FileField, FileRequired, FileAllowed
from .. import photos



class PostForm(FlaskForm):
    title = StringField('Title', validators=[Length(0, 64)])
    body = PageDownField('Edit Post', validators=[DataRequired()])
    post_type = SelectField('Select Post Type', validators=[DataRequired()],
                            choices=[('0', 'Sub2 Tip'), ('1', 'Sub3 Tip'), ('2', 'News')])
    submit = SubmitField('Submit')


class QuestionForm(FlaskForm):
    question_type = SelectField('Select Question Type', validators=[DataRequired()],
                                choices=[('0', 'Sub1'), ('1', 'Sub4')])
    question_text = PageDownField('Edit Question', validators=[DataRequired()])
    option_A = PageDownField('A:', validators=[DataRequired()])
    option_B = PageDownField('B:', validators=[DataRequired()])
    option_C = PageDownField('C:', validators=[DataRequired()])
    option_D = PageDownField('D:', validators=[DataRequired()])
    answer = RadioField('answer', choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
                        validators=[DataRequired()])
    analysis = PageDownField('analysis:', validators=[DataRequired()])
    image = FileField(validators=[FileAllowed(photos)])
    submit = SubmitField('Submit')


class SubmitForm(FlaskForm):
    ans = HiddenField('test')
    submit = SubmitField('Submit')
