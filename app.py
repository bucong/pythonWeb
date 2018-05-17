# coding=utf-8
from functools import wraps
# wraps和make_response是用来开放接口（跨域）
from flask import Flask,request,render_template,make_response
import json
# 定义开放接口方法，在需要开放的接口名称下添加@allow_cross_domain
def allow_cross_domain(fun):
    @wraps(fun)
    def wrapper_fun(*args, **kwargs):
        rst = make_response(fun(*args, **kwargs))
        rst.headers['Access-Control-Allow-Origin'] = '*'
        rst.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
        allow_headers = "Referer,Accept,Origin,User-Agent"
        rst.headers['Access-Control-Allow-Headers'] = allow_headers
        return rst
    return wrapper_fun
# 定义web服务器
app = Flask(__name__)
# 默认路由
@app.route('/')
def index():
    # 返回html模板文件
    username = ''
    if request.cookies.get('username'):
        username = request.cookies.get('username')
    return render_template('index.html',user=username)
# register路由
@app.route('/register')
def register():
    return render_template('register.html')
# login路由
@app.route('/login')
def login():
    return render_template('login.html')
# home路由 接收参数
@app.route('/home/<string:username>')
def home(username):
    return 'Hello %s' % username
# 接口文档
# 操作数据库方法
def conn_mysql(sql):
    import pymysql
    conn = pymysql.connect(host='bucong1129.mysql.rds.aliyuncs.com',user='root',password='Bucong5733',db='node',charset='utf8')
    cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cur.execute(sql)
    res = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return res
# 注册接口
@app.route('/user/register',methods=['get','post'])
# 开放接口
@allow_cross_domain
def userRegister():
    if request.method == 'POST':
        username = request.form['username']
        userpass = request.form['password']
        sql = 'select * from user where username="%s";' % username
        res = conn_mysql(sql)  # 执行sql
        if res:
            res = {
                "code": 1,
                "msg": "该用户名已存在"
            }
            return json.dumps(res, ensure_ascii=False)
        else:
            sql = 'insert into user(username,userpass) value("%s","%s")' % (username,userpass)
            res = conn_mysql(sql)
            res = {"code": 0}
            return json.dumps(res, ensure_ascii=False)
# 登录接口
@app.route('/user/login',methods=['get','post'])
# 开放接口
@allow_cross_domain
def userLogin():
    if request.method == 'POST':
        username = request.form['username']
        userpass = request.form['password']
        sql = 'select * from user where username="%s" and userpass="%s"' % (username,userpass)
        res = conn_mysql(sql)  # 执行sql
        if res:
            res = {"code": 0}
            response = make_response(json.dumps(res, ensure_ascii=False))
            response.set_cookie('username', username)
            return response
        else:
            res = {"code": 1,"msg": "用户名或密码不正确"}
            return json.dumps(res, ensure_ascii=False)
# 退出登录接口
@app.route('/user/loginOut',methods=['get','post'])
# 开放接口
@allow_cross_domain
def userLoginOut():
    if request.method == 'GET':
        res = {"code": 0}
        response = make_response(json.dumps(res, ensure_ascii=False))
        response.delete_cookie('username')
        return response
# 404Error
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'),404
if __name__ == '__main__':
    app.run(port=8080, debug=True)