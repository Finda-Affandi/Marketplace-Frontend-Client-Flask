import os
import re
import uuid

from flask import Flask, render_template, url_for, redirect, request, session, flash
import requests
import datetime
import encryptor
from PIL import Image


app = Flask(__name__)

app.secret_key = 'abcd1234'

# apiUrl = 'http://127.0.0.1:5000'

apiUrl = 'https://backend-fandi-5zn7xh2gqq-et.a.run.app/'

productsApi = apiUrl + '/products'
usersApi = apiUrl + '/users'
stockApi = apiUrl + '/stocks'
cartApi = apiUrl + '/carts'
orderApi = apiUrl + '/orders'
opApi = apiUrl + '/ordered-products'
imageApi = apiUrl + '/images'


@app.route("/", methods=['GET'])
def index():
    if 'user' in session:
        username = session['user']
    else:
        username = ' '

    respProducts = requests.get(productsApi)
    products = respProducts.json()

    respImage = requests.get(imageApi)
    images = respImage.json()

    productList = list()

    for pro in products:
        if pro['status'] == 'Publish':
            image = str()
            for img in images:
                if pro['products_id'] == img['products_id']:
                    image = img['image_url']

            prod = {
                'products_id': pro['products_id'],
                'name': pro['name'],
                'brand': pro['brand'],
                'price': f"{int(pro['price']):,}",
                'description': pro['description'][0:105] + "...",
                'image': image
            }

            productList.append(prod)

    return render_template("main.html", productList=productList, username=username)


@app.route("/admin-home", methods=['GET'])
def adminHome():
    if "user" in session:
        # Ambil data dari API
        respCart = requests.get(cartApi)
        carts = respCart.json()
        cart = int()
        for cr in carts:
            if cr['cart_status'] != 'Checked Out':
                cart+=1

        respOrder = requests.get(orderApi)
        orders = respOrder.json()
        order = len(orders)

        respOp = requests.get(opApi)
        ops = respOp.json()
        op = len(ops)

        return render_template("index.html", user=session["user"], order=order, cart=cart, op=op)
    else:
        return redirect(url_for('login'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Ambil data dari API
        try:
            users = requests.get(usersApi)
        except Exception as e:
            print("ERROR | Get products data |", e)

        for user in users.json():
            if user["username"] == username:
                print(encryptor.decrypt(user['password']))
                if password == encryptor.decrypt(user['password'].encode('utf-8')):
                    if user['role'] == 'Admin':
                        session["user"] = user["username"]
                        session["role"] = user["role"]
                        return redirect(url_for('adminHome'))
                    elif user['role'] == 'User':
                        session["user"] = user["username"]
                        return redirect(url_for('index'))
                    else:
                        return redirect(url_for('login'))
                else:
                    flash("Login failed", category='error')
            else:
                flash('Username not registered', category='error')
    return render_template('login.html')


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for('login'))


@app.route("/home")
def home():
    respCart = requests.get(cartApi)
    carts = respCart.json()
    cart = int()
    for cr in carts:
        if cr['cart_status'] != 'Checked Out':
            cart+=1

    respOrder = requests.get(orderApi)
    orders = respOrder.json()
    order = len(orders)

    respOp = requests.get(opApi)
    ops = respOp.json()
    op = len(ops)

    return render_template('home.html', cart=cart, order=order, op=op)


@app.route("/products", methods=['GET'])
def products():
    if "user" in session:

        # Get data from rest API
        resp = requests.get(productsApi)
        products = resp.json()

        # Make set for brand category
        brand = set()
        for prod in resp.json():
            brand.add(prod['brand'])
        return render_template('products.html', products=products, brand=brand)
    else:
        return redirect(url_for('login'))


@app.route("/add-product")
def addProduct():
    return render_template('add-product.html')


@app.route("/post-product", methods=['GET', 'POST'])
def postProduct():
    if "user" in session:
        if request.method == 'POST':
            if "id" in session:
                session.pop("id", None)

            # Post products

            # Set price
            getPrice = request.form['price']
            price = int

            if getPrice != "":
                price = int(getPrice[4:].replace(".", ""))

            products_id = uuid.uuid4()
            # Create new products from html form
            newProduct = {
                'products_id': str(products_id),
                'name': request.form['name'],
                'brand': request.form['brand'],
                'description': request.form['description'],
                'price': price,
                'status': request.form['status']
            }

            products_response = requests.post(productsApi, json=newProduct)
            if products_response.status_code == 201:
                print('Product posted successfully to Falcon API!')

                # Post stocks

                getsize = request.form.getlist('size')
                size = [x for x in getsize if x != '']
                getstock = request.form.getlist('stock')
                stock = [x for x in getstock if x != '']

                current_date = datetime.datetime.now().date()
                updated_date = current_date.strftime('%Y-%m-%d')

                for x, y in zip(size, stock):
                    stocks_id = uuid.uuid4()
                    new_stock = {
                        'stocks_id': str(stocks_id),
                        'size': x,
                        'stock': y,
                        'products_id': str(products_id),
                        'last_updated': updated_date
                    }
                    stocks_response = requests.post(stockApi, json=new_stock)
                    if stocks_response.status_code == 201:
                        print('Stocks posted successfully to Falcon API!')

                    else:
                        print('Failed to post stocks to Falcon API : ' + str(stocks_response.status_code))

                # Post Images
                images = request.files.getlist('images')

                for i in images:
                    print(i)
                    imgName = str(uuid.uuid4())
                    ext = os.path.splitext(i.filename)[1]
                    img = Image.open(i)
                    filename = f"static/asset/sneakers/{imgName}{ext}"
                    img.save(filename)

                    new_image = {
                        'image_url': filename,
                        'products_id': str(products_id)
                    }

                    respImage = requests.post(imageApi, new_image)


            else:
                print('Failed to post product to Falcon API.')
        return redirect(url_for('products'))
    else:
        return redirect(url_for('login'))


@app.route("/product-edit/<products_id>")
def productEdit(products_id):
    if "user" in session:
        resp = requests.get(productsApi)
        products = resp.json()

        current_product = dict()

        for i in products:
            if i['products_id'] == products_id:
                current_product = i

        return render_template('product-edit.html', current_product=current_product)
    else:
        return redirect(url_for('login'))


@app.route("/update-product/<products_id>", methods=['GET', 'POST', 'PUT'])
def updateProduct(products_id):
    if "user" in session:
        getPrice = request.form['price']
        price = int

        if getPrice != "":
            price = int(getPrice[4:].replace(".", ""))

        updated_product = {
            'products_id': str(products_id),
            'name': request.form['name'],
            'brand': request.form['brand'],
            'description': request.form['description'],
            'price': price,
            'status': request.form['status']
        }

        response = requests.put(productsApi, json=updated_product)

        if response.status_code == 200:
            print('Product put successfully to Falcon API!')
        else:
            print('Failed to put products to Falcon API : ' + str(response.status_code))

        return redirect(url_for('productDetail', products_id=products_id))
    else:
        return redirect(url_for('login'))


@app.route("/stock-edit/<products_id>")
def stockEdit(products_id):
    if "user" in session:
        resp = requests.get(stockApi)
        stock = resp.json()

        products_stock = list()

        for i in stock:
            if i['products_id'] == products_id:
                products_stock.append(i)

        return render_template('stock-edit.html', products_stock=products_stock, products_id=products_id)
    else:
        return redirect(url_for('login'))


@app.route("/update-stock/<products_id>", methods=['GET', 'POST', 'PUT'])
def updateStock(products_id):
    if "user" in session:
        resp = requests.get(stockApi)
        stock = resp.json()

        products_stock = list()

        for i in stock:
            if i['products_id'] == products_id:
                products_stock.append(i)

        getSize = request.form.getlist('size')
        getStock = request.form.getlist('stock')

        current_date = datetime.datetime.now().date()
        updated_date = current_date.strftime('%Y-%m-%d')

        for x, y, z in zip(getSize, getStock, products_stock):
            updated_stock = {
                'stocks_id': z['stocks_id'],
                'size': x,
                'stock': y,
                'last_updated': updated_date
            }

            respStock = requests.put(stockApi, json=updated_stock)
            if respStock.status_code == 200:
                print('Product put successfully to Falcon API!')
            else:
                print('Failed to put products to Falcon API : ' + str(respStock.status_code))

        return redirect(url_for('productDetail', products_id=products_id))
    else:
        return redirect(url_for('login'))


@app.route("/add-stocks/<products_id>")
def addStocks(products_id):
    if "user" in session:

        return render_template('add-stocks.html', products_id=products_id)
    else:
        return redirect(url_for('login'))


@app.route("/post-stock/<products_id>", methods=['GET', 'POST', 'PUT'])
def postStock(products_id):
    if "user" in session:
        # Get products
        resp = requests.get(stockApi)
        stock = resp.json()

        # Filter products and size by products_id
        products_stock = list()
        sizeList = list()

        for i in stock:
            if i['products_id'] == products_id:
                products_stock.append(i)
                sizeList.append(i['size'])

        # Get size and stock from input
        getsize = request.form.getlist('size')
        size = [x for x in getsize if x != '']
        getstock = request.form.getlist('stock')
        stock = [x for x in getstock if x != '']

        # Get current date
        current_date = datetime.datetime.now().date()
        updated_date = current_date.strftime('%Y-%m-%d')

        # Check input size is in database or not
        for x, y in zip(size, stock):
            if x not in sizeList:

                # If the input is not in database, create new stock
                stocks_id = uuid.uuid4()
                new_stock = {
                    'stocks_id': str(stocks_id),
                    'size': x,
                    'stock': y,
                    'products_id': str(products_id),
                    'last_updated': updated_date
                }
                stocks_response = requests.post(stockApi, json=new_stock)
                if stocks_response.status_code == 201:
                    print('Stocks posted successfully to Falcon API!')
                else:
                    print('Failed to post stocks to Falcon API : ' + str(stocks_response.status_code))
            else:

                # If input is in database, add old stock with new stock
                for i in products_stock:
                    if x == i['size']:
                        intStock = int(y)
                        intOldStck = int(i['stock'])
                        newStock = intStock + intOldStck
                        updatedStock = {
                            'stocks_id': i['stocks_id'],
                            'size': i['size'],
                            'stock': newStock,
                            'last_updated': updated_date
                        }

                        print(updatedStock)

                        respStock = requests.put(stockApi, json=updatedStock)
                        if respStock.status_code == 200:
                            print('Product put successfully to Falcon API!')
                        else:
                            print('Failed to put products to Falcon API : ' + str(respStock.status_code))

        return redirect(url_for('productDetail', products_id=products_id))
    else:
        return redirect(url_for('login'))


@app.route("/delete-products/<products_id>", methods=['POST', 'DELETE'])
def deleteProducts(products_id):
    if "user" in session:
        delete_products = {
            'products_id': products_id
        }

        respImg = requests.get(imageApi)
        images = respImg.json()
        imageList = list()
        for img in images:
            if img['products_id'] == products_id:
                imageList.append(img)

        for im in imageList:
            filename = im['image_url']
            os.remove(filename)


        delImg = requests.delete(imageApi, json=delete_products)
        if delImg.status_code == 204:
            print('Deletion image successful.')
        else:
            print('Deletion failed.')


        delStock = requests.delete(stockApi, json=delete_products)
        if delStock.status_code == 204:
            print('Deletion successful.')
            delProd = requests.delete(productsApi, json=delete_products)
            if delProd.status_code == 204:
                print('Deletion successful.')
            else:
                print('Deletion failed.')
        else:
            print('Deletion failed.')
        return redirect(url_for('products'))
    else:
        return redirect(url_for('login'))


@app.route("/product-detail/<products_id>", methods=['GET'])
def productDetail(products_id):
    if "user" in session:
        # Get products from database
        resp = requests.get(productsApi)
        products = resp.json()

        current_product = dict()

        for i in products:
            if i['products_id'] == products_id:
                current_product = i

        # Get stock from database
        resp = requests.get(stockApi)
        stock = resp.json()

        products_stock = list()

        for i in stock:
            if i['products_id'] == products_id:
                products_stock.append(i)

        # Get image from database
        resp = requests.get(imageApi)
        image = resp.json()

        products_image = list()

        for i in image:
            if i['products_id'] == products_id:
                products_image.append(i)

        return render_template('product-detail.html', current_product=current_product, products_stock=products_stock,
                               products_image=products_image)
    else:
        return redirect(url_for('login'))


@app.route("/chat")
def chat():
    if "user" in session:
        chatList = ["Santa Monica", "Santa Clara", "Valentio Tino", "Christian Junior"]
        return render_template('chat.html', chatList=chatList)
    else:
        return redirect(url_for('login'))


@app.route("/chat/<name>")
def chats(name):
    if "user" in session:
        chatList = ["Santa Monica", "Santa Clara", "Valentio Tino", "Christian Junior"]
        return render_template('chat-detail.html', name=name, chatList=chatList)
    else:
        return redirect(url_for('login'))


@app.route("/orders", methods=['GET'])
def orders():
    if "user" in session:
        resp = requests.get(orderApi)
        orders = resp.json()
        return render_template('orders.html', orders=orders)
    else:
        return redirect(url_for('login'))


@app.route("/paid-orders", methods=['GET'])
def paidOrders():
    if "user" in session:
        resp = requests.get(orderApi)
        ord = resp.json()
        orders = list()
        for i in ord:
            if i['order_status'] == 'Wait confirmation':
                orders.append(i)
        return render_template('paid-orders.html', orders=orders)
    else:
        return redirect(url_for('login'))


@app.route("/paid-orders-detail/<order_id>", methods=['GET'])
def paidOrdersDetail(order_id):
    if "user" in session and session["role"] == "Admin":
        # Get order data
        respOrd = requests.get(orderApi)
        orders = respOrd.json()

        order= dict()
        for ord in orders:
            if ord['order_id'] == order_id:
                order = ord

        # Get list ordered product
        respOP = requests.get((opApi))
        ops = respOP.json()
        op = list()

        for o in ops :
            if o['order_id'] == order_id:
                op.append(o)

        # Get ordered products detail
        respProd = requests.get(productsApi)
        prod = respProd.json()

        products = list()
        for o in op:
            for p in prod:
                if o['products_id'] == p['products_id']:
                    products.append(p)
        return render_template('paid-orders-detail.html', order_id=order_id, order = order, products=products)
    else:
        return redirect(url_for('login'))

@app.route("/order-shipment")
def orderShipment():
    if "user" in session:
        resp = requests.get(orderApi)
        ord = resp.json()
        orders = list()
        for i in ord:
            if i['order_status'] == 'On Shipment':
                orders.append(i)
        return render_template('order-shipment.html', orders=orders)
    else:
        return redirect(url_for('login'))

@app.route("/order-shipment-detail/<order_id>", methods=['GET'])
def orderShipmentDetail(order_id):
    if "user" in session:
        username = session['user']

        respOrd = requests.get(orderApi)
        order = dict()
        for o in  respOrd.json():
            if o['order_id'] == order_id:
                order = o


        respOp = requests.get(opApi)
        op = list()
        respImg = requests.get(imageApi)
        img = str()
        for o in respOp.json():
            if o['order_id'] == order_id:
                for i in respImg.json():
                    if i['products_id'] == o['products_id']:
                        img = i['image_url']

                opi = {
                    'name': o['name'],
                    'price': o['price'],
                    'size': o['size'],
                    'image': img
                }

                op.append(opi)
        return render_template('order-shipment-detail.html', order=order, op=op)
    else:
        return redirect(url_for('login'))


@app.route("/order-detail/<order_id>", methods=['GET'])
def orderDetail(order_id):
    if "user" in session:
        username = session['user']

        respOrd = requests.get(orderApi)
        order = dict()
        for o in  respOrd.json():
            if o['order_id'] == order_id:
                order = o


        respOp = requests.get(opApi)
        op = list()
        respImg = requests.get(imageApi)
        img = str()
        for o in respOp.json():
            if o['order_id'] == order_id:
                for i in respImg.json():
                    if i['products_id'] == o['products_id']:
                        img = i['image_url']

                opi = {
                    'name': o['name'],
                    'price': o['price'],
                    'size': o['size'],
                    'image': img
                }

                op.append(opi)
        return render_template('orders-detail.html', order=order, op=op)
    else:
        return redirect(url_for('login'))


@app.route("/confirmation/<order_id>", methods=['GET', 'POST', 'PUT'])
def confirmation(order_id):
    if "user" in session:
        status = request.form['status']
        resi = request.form['resi']
        resp = requests.get(orderApi)
        ord = resp.json()
        orders = dict()
        for i in ord:
            if i['order_id'] == order_id:
                orders = i

        upd_stat = {
            'order_id': order_id,
            'order_status': status,
            'resi': resi,
            'verif_image': orders['verif_image'],
            'subtotal': orders['subtotal']
        }

        respUp = requests.put(orderApi, json= upd_stat)
        if respUp.status_code == 200:
            print('Update put successfully to Falcon API!')
        else:
            print('Failed to update to Falcon API : ' + str(respUp.status_code))

        return redirect(url_for('paidOrders'))
    else:
        return redirect(url_for('login'))

@app.route("/statistic")
def statistic():
    return render_template('statistic.html')


@app.route("/tes")
def tes():
    return render_template('tes.html')


@app.route("/post-image", methods=['GET', 'POST'])
def postImage():
    try:
        # Get the image file from the HTML form
        image_file = request.files['images']

        # Send the image file as binary in the request body
        response = requests.post(imageApi, data=image_file.read(), headers={'Content-Type': 'image/jpeg'})

        # Check the response status code and content
        print('Response status code:', response.status_code)
        print('Response content:', response.content)

    except Exception as e:
        return 'Error uploading image: {}'.format(e)

    return 'Image uploaded successfully'


@app.route("/cart", methods=['GET'])
def cart():
    if "user" in session:
        username = session['user']
        respCart = requests.get(cartApi)
        cartList = respCart.json()

        respProd = requests.get(productsApi)
        productList = respProd.json()

        respImg = requests.get(imageApi)
        imageList = respImg.json()

        userCart = list()
        productsId = list()

        for crt in cartList:
            if crt['username'] == username and crt['cart_status'] == 'on cart':
                c = {
                    'cart_id': crt['cart_id'],
                    'products_id': crt['products_id'],
                    'size': crt['size']
                }
                productsId.append(c)
                userCart.append(crt)

        product = list()

        # Get product from cart products_id
        for pr in productsId:

            # Search product with same products id
            for p in productList:
                if p['products_id'] == pr['products_id']:

                    # Get image with same products_id
                    image = str()
                    for img in imageList:
                        if img['products_id'] == pr['products_id']:
                            image = img['image_url']
                    prod = {
                        'products_id': p['products_id'],
                        'name': p['name'],
                        'brand': p['brand'],
                        'price': f"{int(p['price']):,}",
                        'image': image,
                        'cart_id': pr['cart_id'],
                        'size': pr['size']
                    }

                    product.append(prod)

        return render_template('cart.html', username=username, product=product)

    else:
        return redirect(url_for('login'))



@app.route("/user-add-cart", methods=['POST'])
def userCart():
    if 'user' in session:
        qty = request.form['qty']
        size = request.form['size']
        products_id = request.form['products_id']

        for i in range(int(qty)):
            cart_id = uuid.uuid4()
            username = session['user']
            cart_status = 'on cart'

            new_cart = {
                'cart_id': str(cart_id),
                'products_id': products_id,
                'username': username,
                'cart_status': cart_status,
                'size': size
            }

            response = requests.post(cartApi, json=new_cart)
            if response.status_code == 201:
                print('Carts posted successfully to Falcon API!')
            else:
                print('Failed to carts stocks to Falcon API : ' + str(response.status_code))
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))



@app.route("/delete-cart/<cart_id>", methods=['GET', 'DELETE'])
def userAdd(cart_id):
    delete_cart = {
        'cart_id': cart_id
    }
    delCart = requests.delete(cartApi, json=delete_cart)
    if delCart.status_code == 204:
        print('Deletion successful.')
    else:
        print('Deletion failed.')
    return redirect(url_for('cart'))


@app.route('/checkout', methods=['GET', 'POST', 'PUT'])
def checkout():
    # Get data
    carts_id = request.form.getlist('carts_id')

    if len(carts_id) == 0:
        return redirect(url_for('cart'))

    now = datetime.datetime.now()
    usr = session['user']

    resp = requests.get(productsApi)
    products = resp.json()

    # Create order id from username and datetime
    usrnmr = re.sub(r'[^0-9]', '', str([ord(c) for c in usr]))
    dt_time = re.sub(r'[^0-9]', '', str(now))[0:14]
    order_id = str(usrnmr) + dt_time

    new_orders = {
        'order_id': order_id,
        'username': usr,
        'subtotal': '0',
        'order_status': 'Unpaid',
        'order_datetime': str(now),
        'verif_image': '',
        'resi': ''
    }

    subtotal = int()

    # Get cart from db
    getCart = requests.get(cartApi)
    crt = getCart.json()


    # Post new_orders to order database
    resp_orders = requests.post(orderApi, json=new_orders)
    if resp_orders.status_code == 201:
        print('Orders posted successfully to Falcon API!')

        # Proccess every input cart
        for cart in carts_id:
            cartDict = dict()

            # Get cart data from databse
            for i in crt:
                if cart == i['cart_id']:
                    cartDict = {
                        'cart_id': i['cart_id'],
                        'username': i['username'],
                        'products_id': i['products_id'],
                        'cart_status': i['cart_status'],
                        'size': i['size']
                    }

            # Update cart status to checked out
            up_status = {
                'cart_id': cartDict['cart_id'],
                'cart_status': 'Checked Out'
            }

            respUp = requests.put(cartApi, json=up_status)
            if respUp.status_code == 200:
                print('Status put successfully to Falcon API!')
            else:
                print('Failed to status to Falcon API : ' + str(respUp.status_code))

            # Get stock from db
            getStock = requests.get(stockApi)
            stock = getStock.json()
            stck = dict()
            oldStock = int()


            for stk in stock:
                if stk['products_id'] == cartDict['products_id'] and stk['size'] == cartDict['size']:
                    stck = stk
                    oldStock = stk['stock']

            newStock = oldStock - 1

            current_date = datetime.datetime.now().date()
            updated_date = current_date.strftime('%Y-%m-%d')

            upStock = {
                'stocks_id': stck['stocks_id'],
                'stock': str(newStock),
                'size': stck['size'],
                'last_updated': updated_date
            }

            respUpst = requests.put(stockApi, upStock)
            if respUpst.status_code == 200:
                print('Stock put successfully to Falcon API!')
            else:
                print('Failed to put stocks to Falcon API : ' + str(respUpst.status_code))

            # Post ordered products to database
            op_id = uuid.uuid4()
            for prod in products:

                # Filtering products
                if prod['products_id'] == cartDict['products_id']:
                    new_op = {
                        'op_id': str(op_id),
                        'products_id': prod['products_id'],
                        'price': prod['price'],
                        'size': cartDict['size'],
                        'name': prod['name'],
                        'order_id': order_id
                    }

                    subtotal += int(prod['price'])
                    print(subtotal)

                    resp_op = requests.post(opApi, json=new_op)
                    if resp_op.status_code == 201:
                        print('OP posted successfully to Falcon API!')
                        up_subtotal = {
                            'order_id': order_id,
                            'order_status': 'Unpaid',
                            'subtotal': subtotal,
                            'verif_image': '',
                            'resi': ''
                        }

                        up_order = requests.put(orderApi, up_subtotal)
                        if up_order.status_code == 200:
                            print('Order put successfully to Falcon API!')
                        else:
                            print('Failed to order stocks to Falcon API : ' + str(up_order.status_code))

                    else:
                        print('Failed to post OP to Falcon API : ' + str(resp_orders.status_code))
    else:
        print('Failed to carts stocks to Falcon API : ' + str(resp_orders.status_code))

    return redirect(url_for('transaction', order_id =order_id))


# User area

@app.route("/raccoon/<products_id>", methods=['GET'])
def raccoon(products_id):
    if 'user' in session:
        username = session['user']
    else:
        username = ' '

    respProd = requests.get(productsApi)
    products = respProd.json()
    product = dict()
    for i in products:
        if i['products_id'] == products_id:
            product = {
                'products_id': i['products_id'],
                'name': i['name'],
                'brand': i['brand'],
                'price': f"{int(i['price']):,}",
                'description': i['description']
            }

    respStock = requests.get(stockApi)
    stocks = respStock.json()
    stock = list()
    for i in stocks:
        if i['products_id'] == products_id:
            stock.append(i)

    idImg = 1
    respImage = requests.get(imageApi)
    images = respImage.json()
    image = list()
    for i in images:
        if i['products_id'] == products_id:
            img = {
                'image_url': i['image_url'],
                'id': idImg
            }
            image.append(img)
            idImg += 1

    return render_template('raccoon.html', product=product, stock=stock, image=image, username=username)


@app.route("/transaction/<order_id>", methods=['GET'])
def transaction(order_id):
    if "user" in session:
        if 'user' in session:
            username = session['user']
        else:
            username = ' '

        respOrd = requests.get(orderApi)

        price = str()

        for o in respOrd.json():
            if o['order_id'] == order_id:
                price = f"{int(o['subtotal']):,}"
        return render_template('transaction.html', username=username, order_id=order_id, price=price)
    else:
        return redirect(url_for('login'))


@app.route("/upload-receipt/<order_id>", methods=['GET', 'POST', 'PUT'])
def uploadReceipt(order_id):
    images = request.files.getlist('images')

    respOrder = requests.get(orderApi)
    orders = respOrder.json()

    current_order = dict()
    for ord in orders:
        if ord['order_id'] == order_id:
            current_order = ord

    filename = str()
    for i in images:
        imgName = str(uuid.uuid4())
        ext = os.path.splitext(i.filename)[1]
        img = Image.open(i)
        filename = f"static/asset/receipt/{imgName}{ext}"
        img.save(filename)

    verif_image = {
        'order_id': order_id,
        'order_status': 'Wait confirmation',
        'verif_image': filename,
        'subtotal': current_order['subtotal'],
        'resi': ''
    }

    respVerif = requests.put(orderApi, json=verif_image)
    if respVerif.status_code == 200:
        print('Verification put successfully to Falcon API!')
    else:
        print('Failed to put verification to Falcon API : ' + str(respOrder.status_code))

    return redirect(url_for('userOrder'))


@app.route("/user-transaction-detail/<order_id>", methods=['GET'])
def userTransactionDetail(order_id):
    if "user" in session:
        username = session['user']

        respOrd = requests.get(orderApi)
        order = dict()
        for o in  respOrd.json():
            if o['order_id'] == order_id:
                order = o


        respOp = requests.get(opApi)
        op = list()
        respImg = requests.get(imageApi)
        img = str()
        for o in respOp.json():
            if o['order_id'] == order_id:
                for i in respImg.json():
                    if i['products_id'] == o['products_id']:
                        img = i['image_url']

                opi = {
                    'name': o['name'],
                    'price': o['price'],
                    'size': o['size'],
                    'image': img
                }

                op.append(opi)
        return render_template('user-transaction-detail.html', username=username, order=order, op=op)
    else:
        return redirect(url_for('login'))


@app.route("/user-order", methods=['GET'])
def userOrder():
    if "user" in session:
        if 'user' in session:
            username = session['user']
        else:
            username = ' '
        return render_template('user-orders.html', username=username)
    else:
        return redirect(url_for('login'))


@app.route("/user-transaction", methods=['GET'])
def userTransaction():
    if "user" in session:
        username = session['user']
        respOrd = requests.get(orderApi)
        orders = respOrd.json()

        respOp = requests.get(opApi)

        order = list()
        for od in orders:
            if od['username'] == username:
                product = list()
                for pro in respOp.json():
                    if pro['order_id'] == od['order_id']:
                        product.append(pro)

                orders = {
                    'order_id': od['order_id'],
                    'subtotal': od['subtotal'],
                    'status': od['order_status'],
                    'product': product
                }

                order.append(orders)
        print(order)
        return render_template('user-transaction.html', username=username, order=order)
    else:
        return redirect(url_for('login'))


# trial and error area


@app.route("/xx")
def xx():
    return render_template('cb.html')


@app.route("/cb", methods=['POST'])
def cb():
    images = request.files.getlist('images')

    for i in images:
        imgName = str(uuid.uuid4())
        ext = os.path.splitext(i.filename)[1]
        img = Image.open(i)
        filename = f"static/asset/verif_image/{imgName}{ext}"
        img.save(filename)

    # print(images)
    return render_template('cb.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
