from . import main
from flask import render_template, redirect, url_for, abort, flash, request, \
    current_app, make_response, session
from flask_login import login_required, current_user
from ..decorators import admin_required, permission_required
from .forms import PostForm, QuestionForm, SubmitForm
from ..models import Post, Permission, Question, Answer_paper
from .. import db, photos
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from  sqlalchemy.sql.expression import func


@main.route('/')
def index():
    posts = Post.query.filter_by(post_type=2).order_by(Post.timestamp.desc()).all()
    return render_template('index.html', posts=posts)


@main.route('/dashboard')
@login_required
@admin_required
def dashboard():
    return render_template('dashboard.html')


@main.route('/edit_posts', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_posts():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,
                    body=form.body.data,
                    post_type=form.post_type.data)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.edit_posts'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('edit_posts.html', form=form, posts=posts)


@main.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.post_type = form.post_type.data
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated.')
        return redirect(url_for('.edit_posts'))
    form.title.data = post.title
    form.body.data = post.body
    form.post_type.data = post.post_type
    return render_template('edit_posts.html', form=form)


@main.route('/delete_post/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('.edit_posts'))


@main.route('/edit_questions', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_questions():
    form = QuestionForm()
    if form.validate_on_submit():
        question_text = "{'question':'"+form.question_text.data+"',\
                         'A':'" + form.option_A.data + "',\
                         'B': '" + form.option_B.data + "',\
                         'C': '" + form.option_C.data + "',\
                         'D': '" + form.option_D.data + "'}"
        if form.image.data is None:
            file_url = None
        else:
            filename = photos.save(form.image.data, folder='drivingtest')
            file_url = photos.url(filename)
        question = Question(question_type=form.question_type.data,
                            text=question_text.replace(' ', ''),
                            answer=form.answer.data,
                            analysis=form.analysis.data,
                            image=file_url)
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('.edit_questions'))
    questions = Question.query.all()
    question_t = {}
    for question in questions:
        question_id = question.id
        question_text = question.text
        question_t[question_id] = eval(question_text.replace(' ', ''))

    return render_template('manage_questions.html', form=form, questions=questions, question_t=question_t)


@main.route('/edit_question/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_question(id):
    question = Question.query.get_or_404(id)
    form = QuestionForm()
    if form.validate_on_submit():
        question_text = "{'question':'"+form.question_text.data+"',\
                         'A':'" + form.option_A.data + "',\
                         'B': '" + form.option_B.data + "',\
                         'C': '" + form.option_C.data + "',\
                         'D': '" + form.option_D.data + "'}"
        if form.image.data is not None:
            filename = photos.save(form.image.data, folder='drivingtest')
            file_url = photos.url(filename)
            question.image = file_url
        question.text = question_text
        question.question_type = form.question_type.data
        question.answer = form.answer.data
        question.analysis = form.analysis.data
        db.session.add(question)
        db.session.commit()
        flash('The question has been updated.')
        return redirect(url_for('.edit_questions'))
    question_text = question.text
    question_text = eval(question_text)
    form.question_type.data = question.question_type
    form.question_text.data = question_text['question']
    form.option_A.data = question_text['A']
    form.option_B.data = question_text['B']
    form.option_C.data = question_text['C']
    form.option_D.data = question_text['D']
    form.answer.data = question.answer
    form.analysis.data = question.analysis
    form.image.data = question.image
    return render_template('edit_questions.html', form=form, question=question)


@main.route('/delete_question/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_question(id):
    question = Question.query.get_or_404(id)
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('.edit_questions'))


@main.route('/posts/sub24/<post_type>')
def sub24_posts(post_type):
    posts = Post.query.filter_by(post_type=post_type).order_by(Post.timestamp.desc()).all()
    return render_template('tips.html', posts=posts, t=post_type)


@main.route('/posts/<int:id>')
def show_post(id):
    post = Post.query.get_or_404(id)
    return render_template('show_post.html', post=post)


@main.route('/practice/<question_type>/<int:id>')
def practice(question_type, id):
    questions = Question.query.filter_by(question_type=question_type).all()
    question = questions[id]
    question_t= eval(question.text.replace(' ', ''))
    # for question in questions:
    #     question_id = question.id
    #     question_text = question.text
    #     question_t[question_id] = eval(question_text.replace(' ', ''))
    return render_template('practice.html',
                           question=question,
                           question_t=question_t,
                           question_num=len(questions),
                           question_type=question_type,
                           id=id)


@main.route('/test/<type>/<int:id>')
@login_required
def test(type, id):
    form = SubmitForm()
    answer_paper = Answer_paper()
    if 'test' not in session:
        question_id_list = ''
        questions = Question.query.filter_by(question_type=type).order_by(func.random()).limit(5).all()
        for q in questions:
            question_id_list = question_id_list + str(q.id) + ' '
        print (question_id_list)
        session['test'] = question_id_list
    question_list = session['test'].split()
    question = Question.query.filter_by(id=question_list[id]).first()
    question_t = eval(question.text.replace(' ', ''))
    return render_template('test.html',
                           id=id,
                           question_type=type,
                           question=question,
                           question_t=question_t,
                           question_num=len(question_list),
                           form=form)


@main.route('/save/<ans>')
@login_required
def save(ans):
    print(ans)






