from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import timedelta


app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = 'Qj4MsTJBle'
app.config['MYSQL_PASSWORD'] = 'dVqi6Dtr90'
app.config['MYSQL_DB'] = 'Qj4MsTJBle'

mysql = MySQL(app)


@app.route('/')
def start():

    return render_template('landing.html')


@app.route('/employeelogin/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return redirect(url_for('home'))
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM userstore WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['designation'] = account['designation']
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    return render_template('index.html', msg=msg)


@app.route('/employeelogin/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('customer_id', None)
    session.pop('cust_id', None)
    session.pop('designation',None)
    # Redirect to login page
    return redirect(url_for('login'))


@app.route('/employeelogin/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        if session['designation'] == 'Cashier':
            return render_template('home.html', c_username=session['username'])
        else:
            return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/employeelogin/create_customer_screen', methods=['GET', 'POST'])
def create_customer():
    msg = ''
    # Check if user is loggedin
    if 'loggedin' in session:
        if request.method == 'POST':
            ssn_id = request.form['ssn_id']
            name = request.form['name']
            age = request.form['age']
            address = request.form['address']
            state = request.form['state']
            city = request.form['city']
            msg = "Customer created successfully"
            status = "Active"
            # Insert values into database
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO customers (ssn_id, name, age, address, state, city, status, message) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                        (ssn_id, name, age, address, state, city, status, msg,))
            mysql.connection.commit()

        return render_template("create_customer_screen.html", msg=msg)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/employeelogin/update_customer_screen', methods=['GET', 'POST'])
def update_customer():
    # Check if user is loggedin
    if 'loggedin' in session:
        # Show the profile page with account info
        return render_template('update_customer_screen.html')
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/employeelogin/update_customer_screen/update', methods=['GET', 'POST'])
def update_customer_new():
    if 'loggedin' in session:
        var = ''
        if request.method == 'POST' and ('ssn_id' in request.form or 'customer_id' in request.form):
            ssn_id = request.form['ssn_id']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                'SELECT * FROM customers WHERE ssn_id = %s or  customer_id = %s', (ssn_id, ssn_id,))
            row = cursor.fetchone()
            if row:
                ssn = row["ssn_id"]
                session['admin'] = row['ssn_id']
                tan = row["age"]
                ad = row["address"]
                ns = row["name"]
                ci = row["city"]
                cd = row["customer_id"]
                return render_template('update_customer_screen.html', ssn=ssn, age=tan, address=ad, name=ns, city=ci, customer_id=cd)
            else:
                msg = "Customer does not exist"
                return render_template('update_customer_screen.html', msg=msg)

        elif request.method == 'POST' and 'new_name' in request.form:
            name = request.form['new_name']
            address = request.form['new_address']
            age = request.form['new_age']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            cursor.execute("""UPDATE customers SET name=%s, age=%s, address=%s , status= 'Active', message='Customer update complete' WHERE ssn_id = %s """,
                           (name, age, address, session['admin'],))

            var = "Data updated successfully !!!"
            mysql.connection.commit()
            return render_template('update_customer_screen.html', var=var)

    return redirect(url_for('login'))


@app.route('/employeelogin/delete_customer_screen', methods=['GET', 'POST'])
def delete_customer():
    msg = ""
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST':
            if 'customer_id' in request.form:
                customer_id = request.form['customer_id']
                cursor.execute(
                    'SELECT * FROM customers WHERE customer_id = %s', (customer_id,))
                account = cursor.fetchone()
                if account:
                    session['customer_id'] = account['customer_id']
                    return render_template('delete_customer_screen.html', account=account)
                else:
                    msg = 'Customer does not exist'
                    return render_template('delete_customer_screen.html', msg=msg)
            else:
                cursor.execute(
                    'Delete from customers where customer_id=%s', (session['customer_id'],))
                mysql.connection.commit()
                msg = 'Customer is successfully deleted'
            return render_template('delete_customer_screen.html', msg=msg)
        return render_template('delete_customer_screen.html', msg=msg)
    return redirect(url_for('login'))


@app.route('/employeelogin/create_accnt_screen', methods=['GET', 'POST'])
def create_accnt():
    msg = ''
    # Check if user is loggedin
    if 'loggedin' in session:
        # need all the account info for the user so we can display it on the profile page
        if request.method == 'POST':
            customer_id = request.form['customer_id']
            account_type = request.form['account_type']
            amount = request.form['amount']
            msg = "Account creation complete"
            status = "Active"
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                'SELECT * FROM customers WHERE customer_id = %s', (customer_id,))
            account = cursor.fetchone()
            if account is not None:
                cursor.execute("INSERT INTO accounts (customer_id, account_type, amount, status, message) VALUES (%s,%s,%s,%s,%s)", (
                    customer_id, account_type, amount, status, msg,))
                mysql.connection.commit()
            else:
                msg = "Customer does not exist"
        # Show the profile page with account info
        return render_template('create_accnt_screen.html', msg=msg)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/employeelogin/delete_account_screen', methods=['GET', 'POST'])
def delete_account():
    msg = ""
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST':
            if 'account_id' in request.form:
                account_id = request.form['account_id']
                cursor.execute(
                    'SELECT * FROM accounts WHERE account_id = %s', (account_id,))
                account = cursor.fetchone()
                if account:
                    session['account_id'] = account['account_id']
                    return render_template('delete_account_screen.html', account=account)
                else:
                    msg = 'Entered Account id does not exist'
                    return render_template('delete_account_screen.html', msg=msg)
            else:
                cursor.execute(
                    'Delete from accounts where account_id=%s ', (session['account_id'],))
                mysql.connection.commit()
                msg = 'Account is successfully deleted'
            return render_template('delete_account_screen.html', msg=msg)
        return render_template('delete_account_screen.html', msg=msg)
    return redirect(url_for('login'))


@app.route('/employeelogin/customer_status_screen')
def customer_status():
    # Check if user is loggedin
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM customers')
        customer_accounts = cursor.fetchall()
        return render_template('customer_status_screen.html', accounts=customer_accounts)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/employeelogin/accnt_status_screen')
def accnt_status():
    # Check if user is loggedin
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts')
        customer_accounts = cursor.fetchall()
        # Show the profile page with account info
        return render_template('accnt_status_screen.html', accounts=customer_accounts)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/employeelogin/customer_search_screen', methods=['GET', 'POST'])
def customer_search():
    # Check if user is loggedin
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST':
            if 'ssn_id' in request.form and request.form['customer_id'] == '':
                customerssn = request.form['ssn_id']
                cursor.execute(
                    'SELECT * FROM customers WHERE ssn_id = %s', (customerssn,))
                cust_accnt = cursor.fetchone()
                if cust_accnt:
                    return render_template('customer_search_screen.html', account=cust_accnt)
                else:
                    msg = 'Customer does not exist!'
                    return render_template('customer_search_screen.html', msg=msg)
            elif 'customer_id' in request.form and request.form['ssn_id'] == '':
                customerid = request.form['customer_id']
                cursor.execute(
                    'SELECT * FROM customers WHERE customer_id = %s', (customerid,))
                cust_accnt = cursor.fetchone()
                if cust_accnt:
                    return render_template('customer_search_screen.html', account=cust_accnt)
                else:
                    msg = 'Customer does not exist!'
                    return render_template('customer_search_screen.html', msg=msg)
        return render_template('customer_search_screen.html')
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/employeelogin/accnt_search_screen', methods=['GET', 'POST'])
def accnt_search():
    # Check if user is loggedin
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST':
            if 'account_id' in request.form and request.form['customer_id'] == '':
                accountid = request.form['account_id']
                cursor.execute(
                    'SELECT * FROM accounts WHERE account_id = %s', (accountid,))
                accnt = cursor.fetchone()
                if accnt:
                    return render_template('accnt_search_screen.html', account=accnt)
                else:
                    msg = 'Account does not exist!'
                    return render_template('accnt_search_screen.html', msg=msg)
            elif 'customer_id' in request.form and request.form['account_id'] == '':
                customerid = request.form['customer_id']
                cursor.execute(
                    'SELECT * FROM accounts WHERE customer_id = %s', (customerid,))
                accnt = cursor.fetchone()
                if accnt:
                    return render_template('accnt_search_screen.html', account=accnt)
                else:
                    msg = 'Account does not exist!'
                    return render_template('accnt_search_screen.html', msg=msg)
        return render_template('accnt_search_screen.html')
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/cashierhome/cashier_deposit_screen/<int:accnt_id>',methods=['GET', 'POST'])
def cashier_deposit(accnt_id):
    if 'loggedin' in session and session['designation'] == 'Cashier':
        if request.method == 'POST' and 'deposit_money' in request.form:
            deposit_money= request.form['deposit_money']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE account_id = %s ', (accnt_id,))
            res = cursor.fetchone()
            total = res["amount"]
            total = total + int(deposit_money)
            cursor.execute('UPDATE accounts SET amount=%s, status="Active", message="Amount update complete" WHERE account_id = %s ', (total,accnt_id,))
            message = "Deposit"
            cursor.execute("INSERT INTO transactions (account_id, description, amount) VALUES (%s,%s,%s)", (
                    accnt_id, message, deposit_money))
            
            mysql.connection.commit()
            msg = "Amount deposited successfully !!"
            return render_template('cashier_deposit_screen.html', msg=msg, res_accnt=res, latest_balance=total)

        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM accounts WHERE account_id = %s', (accnt_id,))
        accnt = cursor.fetchone()
        return render_template('cashier_deposit_screen.html', account=accnt)
    return redirect(url_for('login'))


@app.route('/cashierhome/cashier_withdraw_screen/<int:accnt_id>',methods=['GET', 'POST'])
def cashier_withdraw(accnt_id):
    if 'loggedin' in session and session['designation'] == 'Cashier':
        if request.method == 'POST' and 'withdraw_money' in request.form:
            withdraw_money= request.form['withdraw_money']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE account_id = %s ', (accnt_id,))
            res = cursor.fetchone()
            total = res["amount"]
            if int(withdraw_money) > total:
                msg = 'Withdraw not allowed, please choose smaller amount'
                return render_template('cashier_withdraw_screen.html', msg=msg, account=res)
            else:
                total = total - int(withdraw_money)
                cursor.execute(
                    'UPDATE accounts SET amount=%s, status="Active", message="Amount update complete" WHERE account_id = %s ',
                    (total, accnt_id,))
                message = "Withdraw"
                cursor.execute("INSERT INTO transactions (account_id, description, amount) VALUES (%s,%s,%s)", (
                    accnt_id, message, withdraw_money))
                mysql.connection.commit()
                msg = "Amount Withdraw successfully !!"
                return render_template('cashier_withdraw_screen.html', msg=msg, res_accnt=res, latest_balance=total)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM accounts WHERE account_id = %s', (accnt_id,))
        accnt = cursor.fetchone()

        return render_template('cashier_withdraw_screen.html', account=accnt)

    return redirect(url_for('login'))


@app.route('/cashierhome/cashier_transfer_screen/<int:accnt_id>',methods=['GET', 'POST'])
def cashier_transfer(accnt_id):
    if 'loggedin' in session and session['designation'] == 'Cashier':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE account_id = %s', (accnt_id,))
        accnt = cursor.fetchone()
        if request.method == 'POST':
            source_amt = accnt["amount"]
            #Store source initial balance
            s_i_balance=source_amt
            target_account_id = request.form['target_account_id']
            transfer_amount = request.form['transfer_amount']
            cursor.execute(
                'SELECT * FROM accounts WHERE account_id = %s', (target_account_id,))
            res = cursor.fetchone()
            #Check if target account exists or not
            if res is None:
                msg = 'Target account does not exist'
                return render_template('cashier_transfer_screen.html', msg=msg, account=accnt)
            else:  
                #Check if balance is available to transfer
                if int(transfer_amount) > source_amt:
                    msg = 'Transfer not allowed, please choose smaller amount'
                    return render_template('cashier_transfer_screen.html', msg=msg, account=accnt)
                else:
                    if int(target_account_id) == int(accnt_id):
                        msg = 'Source account and Target account should be different'
                        return render_template('cashier_transfer_screen.html', msg=msg, account=accnt)
                    else:
                        #Add transfer amount in target account
                        total = res["amount"]
                        #Store initial balance
                        t_i_balance=total
                        total = total + int(transfer_amount)
                        cursor.execute('UPDATE accounts SET amount=%s WHERE account_id = %s ', (total,target_account_id,))
                        message = "Transfer"
                        cursor.execute("INSERT INTO transactions (account_id, description, amount) VALUES (%s,%s,%s)", (
                            target_account_id, message, transfer_amount))
                        cursor.execute('SELECT * FROM accounts WHERE account_id = %s ', (accnt_id,))
                        #Withdraw money from source account
                        source_amt = source_amt - int(transfer_amount)
                        cursor.execute(
                            'UPDATE accounts SET amount=%s, status="Active", message="Amount update complete" WHERE account_id = %s ',
                            (source_amt, accnt_id,))
                        message = "Transfer"
                        cursor.execute("INSERT INTO transactions (account_id, description, amount) VALUES (%s,%s,%s)", (
                            accnt_id, message, transfer_amount))
                        mysql.connection.commit()
                        msg = "Amount transfer completed successfully"
                        return render_template('cashier_transfer_screen.html', msg=msg, t_acc=res, s_acc=accnt, s_amt=s_i_balance, t_amt=t_i_balance, s_balance=source_amt,t_balance=total) 
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE account_id = %s', (accnt_id,))
        accnt = cursor.fetchone()
        return render_template('cashier_transfer_screen.html', account=accnt)
    return redirect(url_for('login'))


@app.route('/cashierhome/account_details_screen/', methods=['GET', 'POST'])
def account_details():
    if 'loggedin' in session and session['designation'] == 'Cashier':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST':
            if request.form['account_id'] == '' and request.form['csn_id'] == '':
                return render_template('account_details_screen.html', msg='Either one of the two fields is required')
            elif 'account_id' in request.form and request.form['csn_id'] == '':
                accntid = request.form['account_id']
                cursor.execute(
                    'SELECT * FROM accounts WHERE account_id = %s', (accntid,))
                accnt = cursor.fetchone()
                if accnt:
                    return render_template('account_details_screen.html', account=accnt)
                else:
                    msg = 'Account does not exist!'
                    return render_template('account_details_screen.html', msg=msg)
            elif 'csn_id' in request.form and request.form['account_id'] == '':
                csnid = request.form['csn_id']
                cursor.execute(
                    'SELECT customer_id FROM customers WHERE ssn_id = %s', (csnid,))
                cuid = cursor.fetchone()
                if cuid:
                    cursor.execute(
                        'SELECT * FROM accounts WHERE customer_id = %s', (cuid['customer_id'],))
                    accnts = cursor.fetchall()
                    if accnts:
                        session['cust_id'] = cuid['customer_id']
                        return render_template('account_details_screen.html', c_accounts=accnts)
                    else:
                        msg = 'Customer does not exist!'
                        return render_template('account_details_screen.html', msg=msg)
                else:
                    cursor.execute(
                    'SELECT * FROM accounts WHERE customer_id = %s', (csnid,))
                    accnts = cursor.fetchall()
                    if accnts:
                        session['cust_id'] = csnid
                        return render_template('account_details_screen.html', c_accounts=accnts)
                    else:
                        msg = 'Customer does not exist!'
                        return render_template('account_details_screen.html', msg=msg)
        return render_template('account_details_screen.html')
    return redirect(url_for('login'))


@app.route('/cashierhome/account_details_screen/<int:accnt_id>')
def accnt_id_details(accnt_id):
    if 'loggedin' in session and session['designation'] == 'Cashier':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if 'cust_id' in session:
            a_obj = {}
            cursor.execute(
                'SELECT * FROM accounts WHERE customer_id = %s', (session['cust_id'],))
            accnts = cursor.fetchall()
            for a in accnts:
                if a['account_id'] == accnt_id:
                    a_obj = a
            return render_template('account_details_screen.html', c_accounts=accnts, accnt_obj=a_obj)
        else:
            return redirect(url_for('account_details'))
    return redirect(url_for('login'))


@app.route('/cashierhome/account_statement_screen/', methods=['GET', 'POST'])
def account_statement():
    if 'loggedin' in session and session['designation'] == 'Cashier':
        if request.method == 'POST':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            if 'account_id' in request.form:
                if 'no_of_transactions' in request.form:
                    accntid = request.form['account_id']
                    transactions = request.form['no_of_transactions']
                    cursor.execute('SELECT transaction_id, description, amount, DATE(created_at) FROM transactions WHERE account_id = %s', (accntid,))
                    accnts = cursor.fetchmany(int(transactions))
                    return render_template('account_statement_screen.html', accounts=accnts, accntid=accntid)
                elif 'start_date' in request.form and 'end_date' in request.form and request.form['start_date'] != '' and request.form['end_date'] != '':
                    accntid = request.form['account_id']
                    startdate = request.form['start_date']
                    enddate = request.form['end_date']
                    if(startdate < enddate):
                        cursor.execute(
                            'SELECT transaction_id, description, amount, DATE(created_at) FROM transactions WHERE (account_id = %s) AND (DATE(created_at) BETWEEN %s AND %s)',
                            (accntid, startdate, enddate))
                        accnts = cursor.fetchall()
                        return render_template('account_statement_screen.html', accounts=accnts, accntid=accntid)
                    else:
                        msg = 'Please select correct dates'
                        return render_template('account_statement_screen.html', msg=msg)
                else:
                    msg = 'Please fill required fields'
                    return render_template('account_statement_screen.html',msg=msg)
        return render_template('account_statement_screen.html')
    return redirect(url_for('login'))
