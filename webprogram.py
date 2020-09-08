# coding:utf-8
from __future__ import print_function
import os
import time
import tensorflow as tf
import model
import reader
from preprocessing import preprocessing_factory
import folder
from my_album import recourse
from flask import Flask,render_template,request,url_for,g,flash,get_flashed_messages,redirect,session,escape
from flask import make_response,send_from_directory
from userInfo import User
import sqlite3
from functools import wraps
from werkzeug.security import generate_password_hash


#这是项目的主程序

app = Flask(__name__)

app.config['SECRET_KEY'] = 'hello world!'
app.config['DATABASE'] = 'database.db'

#UPLOAD_FOLDER = 'static/img/uploads/'
app.config['UPLOAD_FOLDER'] = 'static/feedback/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

folder.create_folder(app.config['UPLOAD_FOLDER'])


#print(os.getcwd())
os.chdir("C:\\styleTransfer")   #配置工程文件

tf.app.flags.DEFINE_string('loss_model', 'vgg_16', 'The name of the architecture to evaluate. '
                                                   'You can view all the support models in nets/nets_factory.py')
tf.app.flags.DEFINE_integer('image_size', 256, 'Image size to train.')
tf.app.flags.DEFINE_string("model_file", "models.ckpt", "")
tf.app.flags.DEFINE_string("image_file", "a.jpg", "")
FLAGS = tf.app.flags.FLAGS

current_User=''

def connect_db():
    db=sqlite3.connect(app.config['DATABASE'])
    return db

def init_db():
    with app.app_context():
        db = connect_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db=connect_db()   #用g.db访问数据库连接

@app.teardown_request
def teardown_request(exception):
    if hasattr(g,'db'):
        g.db.close()   #对象g可以存储一个连接或一个登陆的用户

def insert_user_todb(user) :
    sql_insert= "INSERT INTO users (name,psw,email) VALUES (?,?,?)"
    args=[user.name,user.psw,user.email]
    g.db.execute(sql_insert,args)
    g.db.commit()

def query_user_fromdb():
    users=[]
    sql_select="SELECT * FROM users"
    args=[]
    cur=g.db.execute(sql_select,args)
    for item in cur.fetchall():
        user=User()
        user.name=item[1]
        user.psw=item[2]
        user.email=item[3]
        users.append(user)
    return users

def query_user_byname(user_name):
    sql_select_byname="SELECT * FROM users where name=?"
    args=[user_name]
    cur=g.db.execute(sql_select_byname,args)
    items=cur.fetchall()
    if len(items)<1:
        return None
    first_item=items[0]
    user=User()
    user.name=first_item[1]
    user.psw=first_item[2]
    user.email=first_item[3]
    return user

def delete_user_byname(user_name):
    delete_sql="DELETE FROM users WHERE name=?"
    args=[user_name]
    g.db.execute(delete_sql,args)
    g.db.commit()

def user_login_check(f):      #监测用户是否登录
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if "user_name" not in session:
            flash("请先登录！", category='error')
            return redirect(url_for("user_login",next=request.url))
        return f(*args,**kwargs)
    return decorated_function

@app.route('/')
#@user_login_check
def index():
    print(session)
    resp=make_response(render_template('index.html',title_name = 'welcome'))
    resp.set_cookie("test","xxxxxxxx")
    return resp

@app.route('/user_login',methods=['GET','POST'])
def user_login():    #用户登录实现
    if request.method=="POST":
        username=request.form['user_name']
        userpsw=request.form['user_password']
        user_check = query_user_byname(username)
        if not user_check:
            flash("用户名不存在!", category='error')
            return render_template('user_login.html')
        else:
            if not user_check.check_psw(str(userpsw)):
                flash("密码错误!请重新输入", category='error')
                return render_template('user_login.html')
            else:
                session["user_name"]=user_check.name
                flash("登陆成功", category='ok')


                return render_template('index.html')
    return render_template('user_login.html')

@app.route('/user_center')   #用户中心
def user_center():
    return render_template('user_center.html')


@app.route('/user_logout')   #用户登出
def user_logout():
    # remove the username from the session if it's there
    session.pop('user_name', None)
    return redirect(url_for("index"))


@app.route('/my_album')
@user_login_check
def my_album():
    #filepath = 'E:\webprogram\static\img\generated'
    filepath = 'C:\styleTransfer\static\img\generated/'+session["user_name"]
    print(filepath)
    files = recourse(filepath)
    for item in files:
        print(item)

    print('HTML相册文件已生成在桌面，请查看')
    return render_template('my_album.html',list=files)


@app.route('/user_my_album')   #我的相册
@user_login_check
def user_my_album():
    filepath = 'C:\styleTransfer\static\img\generated/'+session["user_name"]
    files = recourse(filepath)
    html=make_response(render_template('user_my_album.html',list=files))
    return html




@app.route('/show')
def show():
    #print(sys.path)
    print(os.path)
    return render_template('show.html')



@app.route('/image_transfer',methods=['GET','POST'])
@user_login_check
def image_transfer():
    return render_template('image_transfer.html')

@app.route('/image_uploads',methods=['GET','POST'])
@user_login_check
def image_uploads():
    list=[]
    if request.method =="POST":
        fs=request.files["imagefile"]
        if fs.filename!="":
            file_path=os.path.join(app.config["UPLOAD_FOLDER"],fs.filename)
            fs.save(file_path)
            file_url=url_for("static",filename="feedback/"+fs.filename)
            return render_template("image_uploads.html",file_url=file_url)

    return render_template('image_uploads.html',list=list)




@app.route('/user_register',methods=['GET','POST'])
def user_register():
    if request.method=="POST":
        print(request.form)
        user=User()
        user.name=request.form["user_name"]
        user.psw=generate_password_hash(request.form["user_password"])
        user.email=request.form["email"]
        user_check=query_user_byname(user.name)
        if user_check:
            flash("用户名已经存在，请重新输入",category='error')
            return render_template('user_register.html')

        insert_user_todb(user)
        flash("用户注册成功,请登录", category='ok')

        return redirect(url_for("user_login",username=user.name))

    return render_template('user_register.html')

@app.route('/userInfo_change',methods=['GET','POST'])
@user_login_check
def userInfo_change():
    user=User()
    user=query_user_byname(session.get("user_name"))
    if request.method=="POST":
        user.name=request.form["user_name"]
        user.psw=generate_password_hash(request.form["user_password"])
        user.email=request.form["email"]
        user_check=query_user_byname(user.name)
        #session["user_name"]=user.name
        insert_user_todb(user)
        flash("用户信息修改成功，请重新登录", category='new')
        user_logout()
    return render_template('userInfo_change.html',user=user)


@app.route('/userInfo_delete',methods=['GET','POST'])
@user_login_check
def userInfo_delete():
    if request.method=="POST":
        delete_user_byname(session.get("user.name"))
        return redirect(url_for("user_logout"))
    return render_template("userInfo_delete.html")



@app.errorhandler(404)
def page_not_found(error):
    resp = make_response(render_template('page_not_found.html'), 404)
    resp.headers['X-Something'] = 'A value'
    return resp

@app.template_test('current_link')
def is_current_link(link):
    return link == request.path

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/transform', methods=['GET', 'POST'])
def transform():
    models_dict = {'星月夜': 'starry.ckpt-done',
                   '金属风': 'cubist.ckpt-done',
                   '阴郁风': 'scream.ckpt-done',
                   '海浪': 'wave.ckpt-done',
                   '秋季田野': 'painting.ckpt-done',
                   '水墨画':'landscape.ckpt-done',
                   '紫色风': 'purple.ckpt-done',
                   '油画':'country.ckpt-done',
                   '海上日出':'sunset.ckpt-done',
                   '素描画':'sketch.ckpt-done',
				   '向日葵':'flower.ckpt-done',
				   'sun':'sun.ckpt-done',
                   'night': 'night.ckpt-done',
				   'mountain_vgg16': 'mountain_vgg16.ckpt-done',
				   'mountain_vgg19': 'mountain_vgg19.ckpt-done',
                   }
    if request.method == 'POST':
        file = request.files['pic']

        style = request.form['style']
        if file and allowed_file(file.filename):
            if os.path.exists('/styleTransfer/static/img/uploads/') is False:
                os.makedirs('/styleTransfer/static/img/uploads/')
            file.save(os.path.join('/styleTransfer/static/img/uploads/', file.filename))
            model_file = 'wave.ckpt-done'
            if style != '':
                if models_dict[style] != '':
                    model_file = models_dict[style]
            style_transform(style, '/styleTransfer/models/' + model_file, os.path.join('/styleTransfer/static/img/uploads/') + file.filename,
                            style + '_res_' + file.filename)
            return render_template('transformed.html', style='img/style/' + style + '.jpg',
                                   upload='img/uploads/' + file.filename,
                                   transformed='img/generated/'+session["user_name"]+'/' + style + '_res_' + file.filename)
        return 'transform error:file format error'
    return 'transform error:method not post'

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('/styleTransfer/static/img/generated/', filename)




def style_transform(style, model_file, img_file, result_file):
    height = 0
    width = 0
    with open(img_file, 'rb') as img:
        with tf.Session().as_default() as sess:
            if img_file.lower().endswith('png'):
                image = sess.run(tf.image.decode_png(img.read()))
            else:
                image = sess.run(tf.image.decode_jpeg(img.read()))
            height = image.shape[0]
            width = image.shape[1]
    print('Image size: %dx%d' % (width, height))

    with tf.Graph().as_default():
        with tf.Session().as_default() as sess:
            image_preprocessing_fn, _ = preprocessing_factory.get_preprocessing(
                FLAGS.loss_model,
                is_training=False)
            image = reader.get_image(img_file, height, width, image_preprocessing_fn)
            image = tf.expand_dims(image, 0)
            generated = model.transform_network(image, training=False)
            generated = tf.squeeze(generated, [0])
            saver = tf.train.Saver(tf.global_variables())
            sess.run([tf.global_variables_initializer(), tf.local_variables_initializer()])
            FLAGS.model_file = os.path.abspath(model_file)
            saver.restore(sess, FLAGS.model_file)

            start_time = time.time()
            generated = sess.run(generated)
            generated = tf.cast(generated, tf.uint8)
            end_time = time.time()
            print('Elapsed time: %fs' % (end_time - start_time))
            if os.path.exists('/styleTransfer/static/img/generated' +'/' +session["user_name"]) is False:
                os.makedirs('/styleTransfer/static/img/generated'+'/' + session["user_name"])

            generated_file = '/styleTransfer/static/img/generated/' + session["user_name"] + '/' + result_file

            with open(generated_file, 'wb') as img:
                img.write(sess.run(tf.image.encode_jpeg(generated)))
                print('Done. Please check %s.' % generated_file)


if __name__ == '__main__':
    #init_db()
    app.run(debug=True)
