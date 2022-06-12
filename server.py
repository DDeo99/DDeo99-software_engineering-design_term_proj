from flask import Flask, render_template, request, redirect,session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///products.sqlite3'
app.config['SECRET_KEY']="abcdefg anything"
app.config['SQLALCHEMY_BINDS']={
    'users': 'sqlite:///users.sqlite3',
    'products': 'sqlite:///products.sqlite3'
}


db=SQLAlchemy(app) 


class users(db.Model):
    __bind_key__='users'
    id=db.Column(db.Integer,primary_key=True,unique=True, autoincrement = True)
    email=db.Column(db.String(32),unique=True,nullable=False)
    userid=db.Column(db.String(32),unique=True,nullable=False)
    password=db.Column(db.String(8),nullable=False)
  
    def __init__(self, email, userid, password):
          self.email = email
          self.userid = userid
          self.password=password

class products(db.Model):
    __bind_key__='products'
    id = db.Column(db.Integer, primary_key = True, unique=True, autoincrement = True)
    p_title=db.Column(db.String(30))
    p_detail=db.Column(db.String(200))
    p_keyword=db.Column(db.String(30))
    p_state=db.Column(db.String(30))
    p_seller=db.Column(db.String(30))
    p_sellerid=db.Column(db.String(30))
    
    def __init__(self,title,detail,keyword,state,seller,sellerid):
        self.p_title=title
        self.p_detail=detail
        self.p_keyword=keyword
        self.p_state=state
        self.p_seller=seller
        self.p_sellerid=sellerid
    

@app.route('/',methods=['GET','POST'])
def main():
    if not session.get('userid'):  
        return render_template('mainpage.html',products=products.query.all())
    else:		
        userid = session.get('userid') 
        return render_template('mainpage.html', userid=userid, products=products.query.all())
   
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        userid = request.form.get('userid')
        email = request.form.get('email')
        password = request.form.get('password')
        password_2 = request.form.get('password')

        if not userid or not email or not password or not password_2:
            return "입력되지 않은 정보가 있습니다"
        elif password != password_2:
            return "비밀번호가 일치하지 않습니다"
        else:
            usertable=users(request.form['email'],request.form['userid'],request.form['password'])

            db.session.add(usertable)
            db.session.commit()
            flash ('회원가입 성공')
        return redirect('/')
    
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template('login.html')
    else:
        id=request.form['userid']
        pwd=request.form['password']
        try:
            if users.query.filter_by(userid=id,password=pwd).first() is not None:
                session['userid']=id
                return redirect('/')
            else:
                return 'Can not Login'
        except:
            return "Can't login"

@app.route('/logout', methods=['GET'])
def logout():
	session.pop('userid', None)
	return redirect('/')

@app.route('/upload', methods=['GET','POST'])
def upload():
    if 'userid' in session:
        if request.method=='POST':
            if not request.form['p_title'] or not request.form['p_detail'] or not request.form['p_keyword'] or not request.form['p_state']:
                flash('Please enter all the fields','error')
            else:
                product=products(request.form['p_title'], request.form['p_detail'], request.form['p_keyword'], request.form['p_state'],request.form['p_seller'],session['userid'])
                db.session.add(product)
                db.session.commit()
            
                flash('성공적으로 업로드했습니다.')
                return render_template('mainpage.html')
        return render_template('upload.html')
    return "로그인을 하십시오 <br><a href = '/login'></b>"+\
        "로그인</b></a>"

@app.route('/edit/<product_id>',methods=['GET','POST'])
def edit(product_id):
    edit_product=products.query.filter_by(id=product_id).first()
    if request.method=='POST':
        if not request.form['p_title'] or not request.form['p_detail'] or not request.form['p_keyword'] or not request.form['p_state'] or not request.form['p_seller']:
            flash('Please enter all the fields','error')
        else:
            edit_product.p_title=request.form['p_title']
            edit_product.p_detail=request.form['p_detail']
            edit_product.p_keyword=request.form['p_keyword']
            edit_product.p_state=request.form['p_state']
            edit_product.p_seller=request.form['p_seller']
            db.session.commit()
            
            flash('성공적으로 수정했습니다')
            return redirect(url_for('mypage'))
        
    return render_template('edit.html',product=edit_product)

@app.route('/delete/<product_id>')
def delete(product_id):
    product=products.query.filter_by(id=product_id).first()
    db.session.delete(product)
    db.session.commit()
    return render_template('mypage.html',products=products.query.filter_by(p_sellerid=session['userid']).all()) 


@app.route('/mypage')    
def mypage():
    if 'userid' in session:
        return render_template('mypage.html',products=products.query.filter_by(p_sellerid=session['userid']).all()) 
    return "로그인을 하십시오 <br><a href = '/login'></b>"+\
        "로그인</b></a>"

@app.route('/cloth')
def cloth(): 
    return render_template('cloth.html',products=products.query.filter_by(p_keyword='의류').all())

@app.route('/shoe')
def shoe(): 
    return render_template('shoe.html',products=products.query.filter_by(p_keyword='신발').all())

@app.route('/accessory')
def accessory(): 
    return render_template('accessory.html',products=products.query.filter_by(p_keyword='액세서리').all())

@app.route('/sport')
def sport(): 
    return render_template('sport.html',products=products.query.filter_by(p_keyword='스포츠').all())

@app.route('/electronic')
def electronic(): 
    return render_template('electronic.html',products=products.query.filter_by(p_keyword='전자기기').all())

@app.route('/etc')
def etc(): 
    return render_template('etc.html',products=products.query.filter_by(p_keyword='기타').all())

if __name__=='__main__':
    """basedir = os.path.abspath(os.path.dirname(__file__))
    dbfile = os.path.join(basedir, 'db.sqlite')"""


    db.init_app(app) 
    db.app = app 
    db.create_all()
    app.run(debug = True)