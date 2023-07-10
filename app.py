from flask import Flask, render_template, request, url_for, session, redirect
import ibm_db
import re
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


app = Flask(__name__)

app.secret_key = 'a'
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=2f3279a5-73d1-4859-88f0-a6c3e6b4b907.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=30756;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=bsz31189;PWD=KQGVmZ4cgYEg6pHq",'','')
print("connected")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        sql = "SELECT * FROM REGISTER WHERE USERNAME=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.execute(stmt)
        account=ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg="Account already exists !"
            return render_template('home.html',msg=msg)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+',email):
            msg = 'Invalid email address'
            return render_template('home.html',msg=msg)
        elif not re.match(r'[A-Za-z0-9]+',username):
            msg = 'Username must contain only charcters and numbers!'
            return render_template('home.html',msg=msg)
        else:
            insert_sql = "INSERT INTO REGISTER VALUES (?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, username)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, password)
            ibm_db.execute(prep_stmt)
         
            message = Mail(
                from_email='seethagayathri24@gmail.com',
                to_emails=email ,
                subject='Registration Sucessful',
                html_content='Hello '+ username + ',\n\n'+ """\n\nThank you for registering to Inventory Management System.\n We hope you will have a great experience here. """)
            try:   
                sg = SendGridAPIClient('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')
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            except Exception as e:
                print(e.message)

            #trigger_email(email)
            msg='Successfully Registered!'
            return render_template('login.html',msg=msg)
    else:
        return render_template('login.html')

# def trigger_email(email):
#     sender = 'lollavaishnavi12@gmail.com'
#     receivers = email
#     message = ''' Hello User
#     You have registered!'''
#     try:
#         smtpObj = smtplib.SMTP('localhost')
#         smtpObj.sendmail(sender, receivers,message)         
#         print( "Successfully sent email")
#     except smtplib.SMTPException:
#         print ("Error: unable to send email")
        
@app.route('/login', methods=['GET', 'POST'])
def login():
    global Userid
    msg=''

    if request.method =="POST":
        username = request.form ["username"]
        password = request.form ["password"]
        sql="SELECT * FROM REGISTER WHERE USERNAME=? AND PASSWORD=?"
        stmt=ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        # ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account= ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            session['Loggedin']=True
            session["id"]=account['USERNAME']
            Userid=account['USERNAME']
            session['username']=account['USERNAME']
            msg="logged in successfully !"
            return redirect(url_for('supplier'))
        else:
            msg="Incorrect username/password!" 
            return render_template('login.html', msg=msg)


@app.route('/supplier',methods=['GET', 'POST'])
def supplier():
    sql1= "SELECT * FROM SUPPILER ORDER BY SUPID"
    stmt1=ibm_db.prepare(conn, sql1)
    ibm_db.execute(stmt1)
    row = [('SUPNAME','CONTACT','ADDRESS')]
    data = ibm_db.fetch_tuple(stmt1)
    print(type(data))
    
    while data!= False:
        row.append(data)
        data=ibm_db.fetch_tuple(stmt1)
        
    print(row)
    print(len(row))
    if len(row)>0:
        return render_template('supplier.html',data=row)
    else:
        msg = "No supplier details found."
        return render_template('supplier.html', msg = msg)
    
@app.route('/inventory',methods=['GET','POST'])
def inventory():
    sql1= "SELECT * FROM PRODUCTS ORDER BY PROID"
    stmt1=ibm_db.prepare(conn, sql1)
    ibm_db.execute(stmt1)
    row = []
    data = ibm_db.fetch_tuple(stmt1)
    print(type(data))
   
    while data!= False:
        row.append(data)
        data=ibm_db.fetch_tuple(stmt1)
    total2=0    
    print(row)
    for i in row:
        #print(i[3])
        total2+=int(i[3])
      
            
    print(total2)
        
    total1=len(row)
    print(total1)
    if len(row)>0:
        return render_template('inventory.html',data=row,total1=total1,total2=total2)
    else:
        msg = "No Products details found."
        return render_template('inventory.html', msg = msg)
    #return render_template('inventory.html')

@app.route('/checkout')
def checkout():
    sql2="SELECT * FROM PRODUCTS"
    stmt2=ibm_db.prepare(conn, sql2)
    ibm_db.execute(stmt2)
    data = ibm_db.fetch_tuple(stmt2)
    print(type(data))
    row=[]
    while data!= False:
        row.append(data)
        data=ibm_db.fetch_tuple(stmt2)
    print(row)

    sql1="SELECT * FROM CART"
    stmt1=ibm_db.prepare(conn, sql1)
    ibm_db.execute(stmt1)
    data1 = ibm_db.fetch_tuple(stmt1)
    print(data1)
    print(type(data1))
    row1=[]
    while data1!= False:
        row1.append(data1)
        data1=ibm_db.fetch_tuple(stmt1)
    print(row1)
    return render_template('checkout.html',proddata=row,cartdata=row1)

@app.route('/tender/<string:total>', methods = ['POST', 'GET'])
def tender(total):
    c = 0
    if request.method == 'POST':
        t = request.form['tender']
        c = int(t) - int(total)
    return redirect(url_for('checkout', ch = c, tend = t))

@app.route('/add_to_cart/<string:prodid>', methods = ['GET', 'POST'])
def add_to_cart(prodid):

    sql="SELECT * FROM PRODUCTS WHERE PROID ="+prodid
    stmt=ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    data=ibm_db.fetch_tuple(stmt)
    print(data)
    if request.method == 'POST':
        cusname = request.form['cust']
        quantity = request.form['req_quantity']
        if int(quantity) > int(data[2]):
            qmsg = "Value for quantity exceeded the limit!"
            return render_template('addcart.html',a = data[0], b = data[2], c = data[4], d =data[6], qmsg = qmsg)

        sql2 = "SELECT count(*) FROM CART"
        stmt2 = ibm_db.prepare(conn,sql2)
        ibm_db.execute(stmt2)
        length=ibm_db.fetch_assoc(stmt2)
        print(length)
        insert_sql = "INSERT INTO CART VALUES (?,?,?,?,?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, cusname)
        ibm_db.bind_param(prep_stmt, 2, data[1])
        ibm_db.bind_param(prep_stmt, 3, quantity)
        ibm_db.bind_param(prep_stmt, 4, data[4])
        ibm_db.bind_param(prep_stmt, 5, length['1']+1)
        ibm_db.execute(prep_stmt)
        return redirect(url_for('checkout'))
    
    return render_template('addcart.html', a = data[1], b = data[2], c = data[4], d =data[6])
    


@app.route('/transaction')
def transactions():
    sql1="SELECT * FROM CART"
    stmt1=ibm_db.prepare(conn, sql1)
    ibm_db.execute(stmt1)
    data1 = ibm_db.fetch_tuple(stmt1)
    print(data1)
    print(type(data1))
    row1=[]
    while data1!= False:
        row1.append(data1)
        data1=ibm_db.fetch_tuple(stmt1)
    print(row1)
    return render_template('transcation.html',data1=row1)

@app.route('/addsup',methods=['POST','GET'])
def addsup():
    if request.method == 'POST':
        supname = request.form['name']
        contact = request.form['contact']
        address = request.form['address']
        sql2 = "SELECT * FROM SUPPILER WHERE SUPNAME=?"
        stmt2 = ibm_db.prepare(conn,sql2)
        ibm_db.bind_param(stmt2,1,supname)
        ibm_db.execute(stmt2)
        account=ibm_db.fetch_assoc(stmt2)
        if account:
            msg='Suppiler already exist!'
            return redirect(url_for('addsup'))
        else:
            insert_sql1= "INSERT INTO SUPPILER VALUES(?,?,?,?)"
            sql2 = "SELECT count(*) FROM SUPPILER"
            stmt2 = ibm_db.prepare(conn,sql2)
            ibm_db.execute(stmt2)
            length=ibm_db.fetch_assoc(stmt2)
            print(length)
            prep_stmt1 = ibm_db.prepare(conn, insert_sql1)
            
            ibm_db.bind_param(prep_stmt1, 1, supname)
            ibm_db.bind_param(prep_stmt1, 2, contact)
            ibm_db.bind_param(prep_stmt1, 3, address)
            ibm_db.bind_param(prep_stmt1, 4, length['1']+1)
            ibm_db.execute(prep_stmt1)
            msg='Added supplier details'
            return redirect(url_for('supplier',msg=msg))
    return render_template('addsup.html')

@app.route('/editsupplier/<string:SUPID>', methods= ['GET', 'POST'])
def editsupplier(SUPID):
    sql3= "SELECT * FROM SUPPILER WHERE SUPID = ?"
    stmt3 = ibm_db.prepare(conn, sql3)
    SUPID=str(SUPID)
    ibm_db.bind_param(stmt3, 1, SUPID)
    ibm_db.execute(stmt3)
    account = ibm_db.fetch_assoc(stmt3)
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        address = request.form['address']
        sql4="UPDATE SUPPILER SET SUPNAME = ?, CONTACT =?,ADDRESS = ? WHERE SUPID = ?"
        stmt4=ibm_db.prepare(conn, sql4)
        ibm_db.bind_param(stmt4, 1, name)
        ibm_db.bind_param(stmt4, 2, contact)
        ibm_db.bind_param(stmt4, 3, address)
        ibm_db.bind_param(stmt4, 4, SUPID)
        ibm_db.execute(stmt4)
        return redirect(url_for('supplier'))
    
    return render_template('editsup.html',SUPID=SUPID)

@app.route('/delsup/<string:SUPID>', methods=['GET', 'POST'])
def delsup(SUPID):
    sql4= "DELETE FROM SUPPILER WHERE SUPID=?"
    stmt4 = ibm_db.prepare(conn, sql4)
    ibm_db.bind_param(stmt4, 1, SUPID)
    ibm_db.execute(stmt4)
    return redirect(url_for('supplier'))

@app.route('/addpro', methods=['POST', 'GET'])
def addpro():
    sql1= "SELECT SUPNAME FROM SUPPILER ORDER BY SUPNAME"
    stmt1=ibm_db.prepare(conn, sql1)
    ibm_db.execute(stmt1)
    data = ibm_db.fetch_tuple(stmt1)
    print(type(data))
    sup=[]
    print(data)
    while data!= False:
        sup.append(data)
        data=ibm_db.fetch_tuple(stmt1)
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        cp = request.form['cprice']
        profit = request.form['profit']
        supplier = request.form['supplier']
        print(supplier,profit,cp)
        sp = int(cp) + int(profit)
        insert_sql2= "INSERT INTO PRODUCTS VALUES(?,?,?,?,?,?,?)"
        sql2 = "SELECT count(*) FROM PRODUCTS"
        stmt2 = ibm_db.prepare(conn,sql2)
        ibm_db.execute(stmt2)
        length=ibm_db.fetch_assoc(stmt2)
        print(length)
        stmt2=ibm_db.prepare(conn, insert_sql2)
        ibm_db.bind_param(stmt2, 1, length['1']+1)
        ibm_db.bind_param(stmt2, 2, name)
        ibm_db.bind_param(stmt2, 3, quantity)
        ibm_db.bind_param(stmt2, 4, cp)
        ibm_db.bind_param(stmt2, 5, sp)
        ibm_db.bind_param(stmt2, 6, profit)
        ibm_db.bind_param(stmt2, 7, supplier)
        ibm_db.execute(stmt2)
        return redirect(url_for('inventory'))
        
    
    return render_template('addpro.html',sup=sup)

@app.route('/editproduct/<string:PROID>', methods= ['GET', 'POST'])
def editproduct(PROID):
    sql3= "SELECT * FROM PRODUCTS WHERE PROID = ?"
    stmt3 = ibm_db.prepare(conn, sql3)
    PROID=str(PROID)
    ibm_db.bind_param(stmt3, 1, PROID)
    ibm_db.execute(stmt3)
    account = ibm_db.fetch_assoc(stmt3)
    sql1= "SELECT SUPNAME FROM SUPPILER ORDER BY SUPNAME"
    stmt1=ibm_db.prepare(conn, sql1)
    ibm_db.execute(stmt1)
    data = ibm_db.fetch_tuple(stmt1)
    print(type(data))
    sup1=[]
    print(data)
    while data!= False:
        sup1.append(data)
        data=ibm_db.fetch_tuple(stmt1)
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        cp = request.form['cprice']
        profit = request.form['profit']
        supplier = request.form['supplier']
        print(supplier,profit,cp)
        sp = int(cp) + int(profit)
        sql4="UPDATE PRODUCTS SET PRONAME = ?, QUANTITY =?, CP = ?, SP=?, PROFIT=?, SUPPLIER=? WHERE PROID = ?"
        stmt4=ibm_db.prepare(conn, sql4)
        ibm_db.bind_param(stmt4, 1, PROID)
        ibm_db.bind_param(stmt4, 2, name)
        ibm_db.bind_param(stmt4, 3, quantity)
        ibm_db.bind_param(stmt4, 4, cp)
        ibm_db.bind_param(stmt4, 5, sp)
        ibm_db.bind_param(stmt4, 6, profit)
        ibm_db.bind_param(stmt4, 7, supplier)
        ibm_db.execute(stmt4)
        return redirect(url_for('inventory'))
    
    return render_template('editpro.html',PROID=PROID)

@app.route('/delpro/<string:PROID>', methods=['GET', 'POST'])
def delpro(PROID):
    sql4= "DELETE FROM PRODUCTS WHERE PROID=?"
    stmt4 = ibm_db.prepare(conn, sql4)
    ibm_db.bind_param(stmt4, 1, PROID)
    ibm_db.execute(stmt4)
    return redirect(url_for('inventory'))

@app.route('/delete_cart_product/<string:cartid>', methods = ['POST'])
def delete_cart_product(cartid):
    sql4= "DELETE FROM CART WHERE CARTID=?"
    stmt4 = ibm_db.prepare(conn, sql4)
    ibm_db.bind_param(stmt4, 1, cartid)
    ibm_db.execute(stmt4)
    return redirect(url_for('checkout'))
    
if __name__==('__main__'):
    app.run(debug=True, host='0.0.0.0')

