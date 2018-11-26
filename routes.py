"""
Route management.
(You shouldn't need to change this *much*)
This provides all of the websites routes and handles what happens each
time a browser hits each of the paths. This serves as the interaction
between the browser and the database while rendering the HTML templates
to be displayed.
"""

# Importing the required packages
from flask import Flask, redirect, url_for, render_template, request, flash, jsonify

import database

user_details = {}                   # User details kept for us
session = {}                        # Session information (logged in state)
page = {}                           # Determines the page information

# Initialise the application
app = Flask(__name__)
app.secret_key = """U29tZWJvZHkgb25jZSB0b2xkIG1lIFRoZSB3b3JsZCBpcyBnb25uYSBy
b2xsIG1lIEkgYWluJ3QgdGhlIHNoYXJwZXN0IHRvb2wgaW4gdGhlIHNoZWQgU2hlIHdhcyBsb29r
aW5nIGtpbmRhIGR1bWIgV2l0aCBoZXIgZmluZ2VyIGFuZCBoZXIgdGh1bWIK"""


#####################################################
#   INDEX
#####################################################

@app.route('/')
def index():
    """
    Provides the main home screen if logged in.
        - Gets the user device list.
        - Displays user information from user table.
        - Shows what departments the user is part of.
    """
    # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    page['title'] = 'Device Management'

    # Get the list of devices "Used By" the current employee
    used_by = database.get_devices_used_by(user_details['empid'])

    if used_by is None:
        used_by = []

    # Get the departments that the user works in
    works_in = database.employee_works_in(user_details['empid'])

    if works_in is None:
        works_in = []

    return render_template('index.html',
                           session=session,
                           page=page,
                           user=user_details,
                           used_by=used_by,
                           works_in=works_in,
                           manager_of=session['manager'])


#####################################################
#   LOGIN
#####################################################

@app.route('/login', methods=['POST', 'GET'])
def login():
    """
    Provides /login
        - [GET] If they are just viewing the page then render login page.
        - [POST] If submitting login details, check login.
    """
    # Check if they are submitting details, or they are just logging in
    if(request.method == 'POST'):
        # submitting details
        # The form gives back EmployeeID and Password
        login_return_data = database.check_login(
            request.form['id'],
            request.form['password']
        )

        # If it's null, saying they have incorrect details
        if login_return_data is None:
            page['bar'] = False
            flash("Incorrect id/password, please try again")
            return redirect(url_for('login'))

        # If there was no error, log them in
        page['bar'] = True
        flash('You have been logged in successfully')
        session['logged_in'] = True

        # Store the user details for us to use throughout
        global user_details
        user_details = login_return_data

        # Is the user a manager or a normal user?
        session['manager'] = database.is_manager(request.form['id'])
        return redirect(url_for('index'))

    elif(request.method == 'GET'):
        return(render_template('login.html', session=session, page=page))


#####################################################
#   LOGOUT
#####################################################

@app.route('/logout')
def logout():
    """
    Logs out of the current session
        - Removes any stored user data.
    """
    session['logged_in'] = False
    session['manager'] = None
    page['bar'] = True
    flash('You have been logged out')
    return redirect(url_for('index'))


#####################################################
#   Models
#####################################################

@app.route('/models')
def models():
    """
    Shows a list of all models.
    """
    # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    models = database.get_all_models()
    if models is None:
        page['bar'] = False
        flash('Error communicating with database')
        models = []
    return(render_template('models.html',
                           page=page,
                           session=session,
                           models=models))


#####################################################
#   MyDevices
#####################################################

@app.route('/mydevices')
def mydevices():
    """
    Shows a list of devices issued to me.
    """
    # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    device_list = database.get_issued_devices_for_user(user_details['empid'])

    if device_list is None:
        page['bar'] = False
        flash('Error communicating with database')
        device_list = []

    return(render_template('mydevices.html',
                           device_list=device_list,
                           session=session,
                           page=page))


#####################################################
#   Device (Single Device View)
#####################################################

@app.route('/device/<int:deviceid>')
def device(deviceid):
    """
    Show the device details
        - Repairs.
        - Device information.
    """
    # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    device_info = database.get_device_information(deviceid)

    if device_info is None:
        page['bar'] = False
        flash('Error communicating with database')
        return redirect(url_for('index'))

    repairs = database.get_device_repairs(deviceid)

    if repairs is None:
        page['bar'] = False
        flash('Error communicating with database')
        repairs = []

    return(render_template('device_info.html',
                           device_info=device_info,
                           repairs=repairs,
                           session=session,
                           page=page))


#####################################################
#   Device Model
#####################################################

@app.route('/device/<int:deviceid>/model')
def devicemodel(deviceid):
    """
    Show the device details
        - Repairs.
        - Device information.
    """
    # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    model_info = database.get_device_model(deviceid)

    if model_info is None:
        page['bar'] = False
        flash('Error communicating with database')
        return redirect(url_for('index'))

    return(render_template('model.html',
                           model_info=model_info,
                           session=session,
                           page=page))


#####################################################
#   Repair (Single Repair View)
#####################################################

@app.route('/repair/<int:repairid>')
def repair(repairid):
    """
    Show the repair details, including service info.
    """
    # Check if the user is logged in, if not: back to login.
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    repair_info = database.get_repair_details(repairid)

    if repair_info is None:
        page['bar'] = False
        flash('Error communicating with database')
        return redirect(url_for('index'))

    return render_template('repair.html',
                           repair_info=repair_info,
                           session=session,
                           page=page)

################################################################################
#                        Manager Section
################################################################################


#####################################################
#   Department Models
#####################################################

@app.route('/departmentmodels')
def departmentmodels():
    """
    Shows the list of models assigned to the department.

    1. The manager can click a model and see the devices per employee
        of that model.
    2. The manager can then select the employee and show all devices matching
        the model and indicate whether the user has been issued or not.

    Page Layout (yes it's hacky, and no it's not secure - it's for demonstration only!):
        1. /departmentmodels => Show table of models to departments
        2. /departemntmodels?model=___&manufacturer=___ => show employee counts
        3. /departmentmodels?model=___&manufacturer=___&empid=____ => show all devices for model and indicate.
    """
    # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    # Check if user is manager
    if session['manager'] is None:
            return redirect(url_for('index'))

    # Get any URL arguments
    model = request.args.get('model', '')
    manufacturer = request.args.get('manufacturer', '')
    empid = request.args.get('empid', '')
    department = request.args.get('department', '')

    # See what we are actually rendering?
    if empid != '' and manufacturer != '' and model != '' and department != '':
        # We have all three - show the device list of issued true/false.
        device_assigned = database.get_model_device_assigned(model, manufacturer, empid)

        if device_assigned is None:
            flash('No model/manufacturer/employee matching')
            page['bar'] = True
            return redirect(url_for('departmentmodels'))

        return render_template('model_device_assigned.html',
                               device_assigned=device_assigned,
                               department=session['manager'],
                               empid=empid,
                               model=model,
                               manufacturer=manufacturer,
                               session=session,
                               page=page)

    elif empid == '' and manufacturer != '' and model != '' and department != '':
        # Manager has selected a model - show employee counts
        model_counts = database.get_employee_department_model_device(
            department,
            manufacturer, model)

        if model_counts is None:
            page['bar'] = False
            flash('No model/manufacturer matching department')
            return redirect(url_for('departmentmodels'))

        return render_template('model_counts.html',
                                model_counts=model_counts,
                                model=model,
                                session=session,
                                manufacturer=manufacturer,
                                department=session['manager'],
                                page=page)
    else:
        # Show all models from the department
        department_models = database.get_department_models(session['manager'])

        return render_template('departmentmodels.html',
                               department_models=department_models,
                               department=session['manager'],
                               session=session,
                               page=page)


#####################################################
#   Issue Device
#####################################################

@app.route('/issuedevice', methods=['POST', 'GET'])
def issue_device():
    # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))
    if session['manager'] is None:
        return redirect(url_for('index'))

    if(request.method == 'POST'):
        empid = request.form.get('empid')
        device_id = request.form.get('deviceid')

        if empid is None or device_id is None:
            page['bar'] = False
            flash('Invalid request')
            return redirect(url_for('issue_device'))

        # If it is a POST - they are sending an 'issue' request
        res = database.issue_device_to_employee(empid, device_id)
        if res[0]:
            page['bar'] = True
            flash('Device successfully issued')
        else:
            page['bar'] = False
            flash(res[1])
        return redirect(url_for('issue_device'))

    elif(request.method == 'GET'):
        # Else they're looking at the page.
        # 1. Get the list of models (Other parts will be async through ajax)
        models = database.get_department_models(session['manager'])

        if models is None:
            page['bar'] = False
            flash('Error communicating with database')
            models = []

        # 3. Get the employees in the department (once chosen)
        employees = database.get_employees_in_department(session['manager'])

        if employees is None:
            page['bar'] = False
            flash('Error communicating with database')
            employees = []

        return render_template('issue.html',
                                       page=page,
                                       session=session,
                                       employees=employees,
                                       models=models)


#####################################################
#   Get device list for model
#####################################################

@app.route('/modeldevices', methods=['GET'])
def model_devices():
    """
    Returns the list of devices that correspond with the given
    model.
    """
    # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    model = request.args.get('modelnumber')
    manufacturer = request.args.get('manufacturer')

    # If no model or manufacturer
    if model is None or manufacturer is None:
        return jsonify({'error': True})

    devices = database.get_unassigned_devices_for_model(model, manufacturer)

    if devices is None:
        return jsonify({'error': True})

    return jsonify({'devices': devices})


#####################################################
#   Get employees for department
#####################################################

@app.route('/departmentemployees', methods=['GET'])
def departmentemployees():
    """
    Return the list of employees that work in the
    department.
    """
    department = request.args.get('department')

    if department is None:
        flash('Error retrieving devices')
        return jsonify({'error': True})

    employees = database.get_employees_in_department(department)

    if employees is None:
        return jsonify({'error': True})

    return jsonify({'employees': employees})


#####################################################
#   Remove Device (POST only, no page associated)
#####################################################

@app.route('/revokedevice', methods=['GET'])
def revoke_device():
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    if(session['manager'] is None):
        return redirect(url_for('index'))

    # If they're sending the revoke
    device_id = request.args.get('device_id')
    employee_id = request.args.get('empid')
    model = request.args.get('model')
    department = request.args.get('department')
    manufacturer = request.args.get('manufacturer')

    if device_id is None or employee_id is None:
        page['bar'] = False
        flash('Invalid Request Sent')
        return redirect(url_for('departmentmodels'))

    # Attempt the "revoke"
    success = database.revoke_device_from_employee(employee_id, device_id)

    if success is None:
        page['bar'] = False
        flash('Database Request Failed')
        return redirect(url_for('departmentmodels',
                                model=model,
                                manufacturer=manufacturer,
                                empid=employee_id,
                                department=department))

    page['bar'] = success[0]
    flash("Device Revoked" if success[0] else success[1])

    # Return true if success else if there was an error send the message
    return redirect(url_for('departmentmodels',
                                model=model,
                                manufacturer=manufacturer,
                                empid=employee_id,
                                department=department))


######### Extension ########

#####################################################
#   Extension 1 Device Count
#####################################################

@app.route('/deviceCount')
def deviceCount():
    """
    something spmething device count
    """
    # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    # empid = request.args.get('empid')

    counts = database.extension1()


    if counts is None:
        page['bar'] = False
        flash('You dont manage anything? or perhaps something else')
        counts = []
    return(render_template('deviceCount.html',
                           page=page,
                           session=session,
                           deviceCounts=counts))

#####################################################
#   Extension 2 Repair Costs
#####################################################

@app.route('/repair_costs')
def repair_costs():
    """
    something spmething repair costs
    """
    # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    # empid = request.args.get('empid')

    costs = database.extension2()


    if costs is None:
        page['bar'] = False
        flash('You dont manage anything? or perhaps something else')
        costs = []
    return(render_template('repair_costs.html',
                           page=page,
                           session=session,
                           costs=costs))


#####################################################
#   Extension 3 Repair Costs
#####################################################

@app.route('/repair_costs')
def repair_costs():
    """
    something spmething repair costs
    """
    # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    # empid = request.args.get('empid')

    costs = database.extension2()


    if costs is None:
        page['bar'] = False
        flash('You dont manage anything? or perhaps something else')
        costs = []
    return(render_template('repair_costs.html',
                           page=page,
                           session=session,
                           costs=costs))
