from flask import Flask,render_template,request,redirect,url_for,session
from logging import FileHandler, WARNING

import sqlite3

app = Flask(__name__)

app.secret_key = 'hello'
file_handler = FileHandler('errorlog.txt')
file_handler.setLevel(WARNING)

@app.route("/")
def index():
        database = "food.db"
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        records = cur.execute("select * from category")
        categories = records.fetchall()
        return render_template("index.html",categories=categories)       

@app.route("/register",methods=["GET","POST"])
def register():
        if(request.method=="GET"):
                return render_template("register.html")
        else:
                uname = request.form["uname"]
                email = request.form["email"]
                pass1 = request.form["pass"]
                database = "food.db"
                conn = sqlite3.connect(database)
                cur = conn.cursor()
                records = cur.execute("select count(*) from login where name='"+uname+"'")
                users = records.fetchall()
                if(int(users[0][0] ) >=1):
                        return "User already present"
                else:
                        sql = "insert into login values ('"+uname+"','"+email+"','"+pass1+"')"
                        conn.execute(sql)
                        conn.commit()
                        conn.close()
                        return redirect(url_for("usrLogin"))

@app.route("/admin")
def admin():
    return render_template("adminLogin.html")

@app.route("/usrLogin")
def usrLogin():
    return render_template("LoginAndSign.html")

@app.route("/adminLogin",methods=['GET','POST'])
def adminLogin():
    return redirect(url_for("showData"))

@app.route("/LoginNew")
def login():
    return render_template("adminLogin.html")


@app.route("/ValidateData",methods=["GET","POST"])
def ValidateData():
    if(request.method == "POST"):
        name = request.form["name"]
        email = request.form["email"]
        database = "food.db"
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        sql = "select count(*) from login where name='"+name+"' and email='"+email+"'"
        print(sql)
        rows = cur.execute(sql)
        count = rows.fetchall()
        if(int(count[0][0] == 1)):
                session["uname"] = name
                return  redirect(url_for("index"))  
        
@app.route('/logout')
def logout():
        session.pop('uname', None)
        return redirect(url_for("index"))

@app.route("/makePayment")
def payment():
    return render_template("payment.html")

@app.route("/ValidatePayment",methods=["GET","POST"])
def ValidatePayment():
        if(request.method == "POST"):
                card_no = request.form["card_no"]
                cvv = request.form["cvv"]
                database = "food.db"
                conn = sqlite3.connect(database)
                sql = "select count(*) from card where card_no="+card_no+" and cvv="+cvv
                records = conn.execute(sql)
                count = records.fetchall()
                print(sql)
                if(count[0][0]==1):
                        #Make Payment
                        sql1 = "update card set amount = amount -"+str(session["totalPrice"])+" where card_no="+str(card_no)
                        sql2 = "update card set amount = amount +"+str(session["totalPrice"])+" where card_no="+str(111)
                        sql3 = "delete from shoppingcart where userid = '"+session["uname"]+"'"

                        conn.execute(sql1)
                        conn.execute(sql2)
                        conn.execute(sql3)
                        conn.commit()
                        conn.close()
                        
                        return "Payment success"
                else :
                        return "Failed"
                
                #return redirect(url_for("payment"))
        
        #####user part
@app.route('/showfood/<cat_id>')
def showfood(cat_id):
        database = "food.db"
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        records = cur.execute("select * from food_item where cat_id="+cat_id)
        food = records.fetchall()
        return render_template("showFood.html",food=food) 

@app.route("/addtocart",methods=["GET","POST"])
def addtocart():
        if(request.method=="POST"):
                try:
                        id = request.form["id"]
                        pnm = request.form["pname"]
                        price = request.form["price"]
                        qty = request.form["qty"]                        
                        database = "food.db"
                        conn = sqlite3.connect(database)
                        sql = "insert into shoppingcart (productid,userid,pname,price,quantity) values ("+str(id)+",'"+str(session["uname"])+"','"+pnm+"',"+str(price)+","+str(qty)+")"
                        print(sql)
                        conn.execute(sql)
                        conn.commit()
                        conn.close()
                        return redirect(url_for("showallcartitems"))
                except:
                        try:
                                session["uname"]
                                return "Already Added"
                        except:
                                return redirect(url_for("usrLogin"))


@app.route("/removecart",methods=["GET","POST"])
def removeFromCart():
    if(request.method == "POST"):
        pid = request.form["pid"]
        database = "food.db"
        conn = sqlite3.connect(database)
        sql = "delete from shoppingcart where productid="+pid +" and userid='"+str(session["uname"])+"'"
        print(sql)
        conn.execute(sql)
        conn.commit()
        conn.close()
        return redirect(url_for("showallcartitems"))

@app.route("/showallcartitems")
def showallcartitems():
        try:
                totalPrice = 0
                database = "food.db"
                conn = sqlite3.connect(database)
                cur = conn.cursor()     
                sql="select * from shoppingcart where userid='"+session['uname']+"'"
                records = cur.execute(sql)
                rows = records.fetchall()                
                count = 0
                for price in rows:
                        count = count+1
                        totalPrice = totalPrice + (float(price[3])) * (float(price[4]))
                        session["totalPrice"] = totalPrice 
                if(count == 0):
                        session["totalPrice"] = totalPrice
                return render_template("ShowAllCartItems.html",rows=rows,totalPrice= totalPrice)
        except:
                return redirect(url_for("usrLogin"))

@app.route("/ValidateAdmin",methods=["GET","POST"])
def Validateadmin():
    if(request.method == "POST"):
        name = request.form["name"]
        email = request.form["email"]
        pwd = request.form["pwd"]
        if(name == "Ashutosh" and email == "ash@gmail.com" and pwd == "123456"):
                session["name"] = name
                return render_template("adminSelect.html")
        else:
            return redirect(url_for("login"))

@app.route('/logoutAdmin')
def logoutadmin():
        session.pop('name', None)
        return redirect(url_for("login"))
                                #admin PArt

@app.route("/showCategory")
def showCat():
    database = "food.db"
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    records = cur.execute("select * from category")
    food = records.fetchall()
    return render_template("category.html",food=food)

@app.route("/showCategory")
def showCategory():
    database = "food.db"
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    records = cur.execute("select * from category")
    food = records.fetchall()
    return render_template("category.html",food=food)

                                #AddCategory
@app.route("/addCat")
def addCat():
    database = "food.db"
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    records = cur.execute("select * from category")
    food = records.fetchall()
    return render_template("addCat.html",food=food)  

@app.route("/saveCategory",methods=['GET','POST'])
def saveCat():    
    if(request.method=="POST"):
        database = "food.db"
        conn = sqlite3.connect(database)
        cat_id = request.form["cat_id"]
        cat_name = request.form["cat_name"]
        cat_veg = request.form["cat_veg"]
        sql = "insert into category values ("+cat_id+",'"+cat_name+"','"+cat_veg+"')"
        conn.execute(sql)
        conn.commit()
        conn.close()
        return redirect(url_for("showCat"))
                                #deteteCategory
@app.route("/DeleteCategory/<cat_id>")
def deleteCatConfirm(cat_id):    
    return render_template("deleteCategory.html",cat_id=cat_id)

@app.route("/deleteCategory",methods=['GET','POST'])
def deleteCategory():
    if(request.method=="POST"):
        action = request.form["action"]
        cat_id  = request.form["cat_id"]
        if(action == "confirm"):
            database = "food.db"
            conn = sqlite3.connect(database)
            sql = "delete from category where cat_id ="+cat_id
            print(sql)
            conn.execute(sql)
            conn.commit()
            conn.close()
    return redirect(url_for("showCategory"))
                                        #EditCategory
@app.route("/EditCategory/<cat_id>")
def editCategory(cat_id):
    database = "food.db"
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    records = cur.execute("select * from category where cat_id ="+cat_id)
    categories = records.fetchall()    
    return render_template("editCategory.html",categories=categories[0])

@app.route("/UpdateCategory",methods=['GET','POST'])
def updateCategory():
    if(request.method=="POST"):
        database = "food.db"
        conn = sqlite3.connect(database)
        cat_id = request.form["cat_id"]
        cat_name = request.form["cat_name"]
        cat_veg = request.form["cat_veg"]
        sql = "update category set cat_name = '"+cat_name+"',cat_veg = '"+cat_veg+"' where cat_id="+cat_id
        print (sql)
        conn.execute(sql)
        conn.commit()
        conn.close()
        return redirect(url_for("showCat"))                                        

                                        #foodItem
@app.route("/showFoodItem")
def showData():
    database = "food.db"
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    records = cur.execute("select * from food_item")
    food = records.fetchall()
    return render_template("admin.html",food=food)

@app.route("/addItem")
def addrecord():
    database = "food.db"
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    records = cur.execute("select * from category")
    food = records.fetchall()
    return render_template("addItem.html",food=food)   

@app.route("/SaveFood",methods=['GET','POST'])
def saveRecord():
        try:
                if(request.method=="POST"):
                        database = "food.db"
                        conn = sqlite3.connect(database)
                        item_no = request.form["itemNo"]
                        item_name = request.form["itemName"]
                        item_price = request.form["itemPrice"]
                        item_descr = request.form["itemDescr"]
                        item_image = request.form["itemImage"]
                        cat_id = request.form["cat_id"]
                        cat_veg =request.form["cat_veg"]
                        sql = "insert into food_item values ("+item_no+",'"+item_name+"',"+item_price+",'"+item_descr+"','"+item_image+"',"+cat_id+",'"+cat_veg+"')"
                        conn.execute(sql)
                        conn.commit()
                        conn.close()
                        return redirect(url_for("showData"))
        except:
                return "Cannot Add Same ID Again"
                                    #deleteFoodItem
@app.route("/DeleteFood/<item_no>")
def deleteConfirm(item_no):    
    return render_template("deleteConfirm.html",item_no=item_no)

@app.route("/deleteRecord",methods=['GET','POST'])
def deleteRecord():
    if(request.method=="POST"):
        action = request.form["action"]
        item_no  = request.form["item_no"]
        if(action == "confirm"):
            database = "food.db"
            conn = sqlite3.connect(database)
            sql = "delete from food_item where item_no ="+item_no
            print(sql)
            conn.execute(sql)
            conn.commit()
            conn.close()
    return redirect(url_for("showData"))
                                    #EditFoodItem
@app.route("/EditFood/<item_no>")
def editRecord(item_no):
    database = "food.db"
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    records = cur.execute("select * from food_item where item_no ="+item_no)
    food = records.fetchall()    
    return render_template("editFood.html",food=food[0])

@app.route("/UpdateFood",methods=['GET','POST'])
def updateFood():
    if(request.method=="POST"):
        database = "food.db"
        conn = sqlite3.connect(database)
        item_no = request.form["item_no"]
        item_name = request.form["item_name"]
        item_price = request.form["item_price"]
        item_descr = request.form["item_descr"]
        item_image = request.form["item_image"]
        cat_id = request.form["cat_id"]
        cat_veg = request.form["cat_veg"]
        sql = "update food_item set item_name = '"+item_name+"',item_price = "+item_price+",item_descr = '"+item_descr+"',item_image = '"+item_image+"',cat_id = '"+cat_id+"',cat_veg = '"+cat_veg+"' where item_no="+item_no
        print (sql)
        conn.execute(sql)
        conn.commit()
        conn.close()
        return redirect(url_for("showData"))

if(__name__ == "__main__"):       
    app.run(debug =True)
