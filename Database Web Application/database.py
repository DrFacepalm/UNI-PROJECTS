#!/usr/bin/env python3
"""
DeviceManagement Database module.
Contains all interactions between the webapp and the queries to the database.
"""

import configparser
import datetime
from typing import List, Optional

import setup_vendor_path  # noqa
import pg8000

################################################################################
#   Welcome to the database file, where all the query magic happens.
#   My biggest tip is look at the *week 9 lab*.
#   Important information:
#       - If you're getting issues and getting locked out of your database.
#           You may have reached the maximum number of connections.
#           Why? (You're not closing things!) Be careful!
#       - Check things *carefully*.
#       - There may be better ways to do things, this is just for example
#           purposes
#       - ORDERING MATTERS
#           - Unfortunately to make it easier for everyone, we have to ask that
#               your columns are in order. WATCH YOUR SELECTS!! :)
#   Good luck!
#       And remember to have some fun :D
################################################################################


#####################################################
#   Database Connect
#   (No need to touch
#       (unless the exception is potatoing))
#####################################################

def database_connect():
    """
    Connects to the database using the connection string.
    If 'None' was returned it means there was an issue connecting to
    the database. It would be wise to handle this ;)
    """
    # Read the config file
    config = configparser.ConfigParser()
    config.read('config.ini')
    if 'database' not in config['DATABASE']:
        config['DATABASE']['database'] = config['DATABASE']['user']

    # Create a connection to the database
    connection = None
    try:
        # Parses the config file and connects using the connect string
        connection = pg8000.connect(database=config['DATABASE']['database'],
                                    user=config['DATABASE']['user'],
                                    password=config['DATABASE']['password'],
                                    host=config['DATABASE']['host'])
    except pg8000.OperationalError as operation_error:
        print("""Error, you haven't updated your config.ini or you have a bad
        connection, please try again. (Update your files first, then check
        internet connection)
        """)
        print(operation_error)
        return None

    # return the connection to use
    return connection


#####################################################
#   Query (a + a[i])
#   Login
#####################################################

def check_login(employee_id, password: str) -> Optional[dict]:
    """
    Check that the users information exists in the database.
        - True => return the user data
        - False => return None
    """

    # Note: this example system is not well-designed for security.
    # There are several serious problems. One is that the database
    # stores passwords directly; a better design would "salt" each password
    # and then hash the result, and store only the hash.
    # This is ok for a toy assignment, but do not use this code as a model when you are
    # writing a real system for a client or yourself.

    conn = database_connect()
    if(conn is None):
        return None

    cur = conn.cursor()

    try:
        # SQL statement and execute
        sql = """SELECT empid, name, homeAddress, dateOfBirth
                 FROM Employee
                 WHERE empid = %s AND password = %s"""
        cur.execute(sql, (employee_id, password))

        # Attempt to fetch first row
        employee_info = cur.fetchone()

        # If employee info returns nothing, return none
        if employee_info == None:
            cur.close()
            conn.close()
            return employee_info

        result = {
            'empid': employee_info[0],
            'name': employee_info[1],
            'homeAddress': employee_info[2],
            'dateOfBirth': employee_info[3]
        }
        cur.close()
        conn.close()
        return result
    except Exception as e :
        print("aaa")
        print(e)
        # If something went really wrong
        cur.close()
        conn.close()
        return None


#####################################################
#   Query (f[i])
#   Is Manager?
#####################################################

def is_manager(employee_id: int) -> Optional[str]:
    """
    Get the department the employee is a manager of, if any.
    Returns None if the employee doesn't manage a department.
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        # SQL statement and execute
        sql = """SELECT Department.name
                 FROM Employee JOIN Department ON(Employee.empid = Department.manager)
                 WHERE Employee.empid = %s"""
        cur.execute(sql, (employee_id,))

        # Attempt to fetch first row
        result = cur.fetchone()

        # If nothing is fetched
        if result == None:
            cur.close()
            conn.close()
            return result


        cur.close()
        conn.close()
        return result[0]
    except Exception as e:
        # If something went really wrong
        print("bbb")
        print(e)
        cur.close()
        conn.close()
        return None


#####################################################
#   Query (a[ii])
#   Get My Used Devices
#####################################################

def get_devices_used_by(employee_id: int) -> list:
    """
    Get a list of all the devices used by the employee.
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        # SQL statement and execute
        sql = """SELECT D.deviceID, D.manufacturer, D.modelNumber
                 FROM Device D JOIN DeviceUsedBy DUB USING(deviceID) JOIN Employee E USING(empID)
                 WHERE E.empid = %s"""
        cur.execute(sql, (employee_id,));

        # Attempt to fetch first row
        result = cur.fetchall()

        if result == None:
            cur.close()
            conn.close()
            return []

        device_usedby = []
        for row in result:
            device_usedby.append(
                [row[0], row[1], row[2]]
            )
        return device_usedby

    except Exception as e:
        # If something went wrong, return an empty list
        print("ccc")
        print(e)
        cur.close()
        conn.close()
        return []



#####################################################
#   Query (a[iii])
#   Get departments employee works in
#####################################################

def employee_works_in(employee_id: int) -> List[str]:
    """
    Return the departments that the employee works in.
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        # SQL statement and execute
        sql = """SELECT department
                 FROM EmployeeDepartments
                 WHERE EmployeeDepartments.empid = %s"""
        cur.execute(sql, (employee_id,));

        # Attempt to fetch all
        result = cur.fetchall()

        if result == None:
            cur.close()
            conn.close()
            return []

        departments = []
        for row in result:
            departments.append(
                row[0]
            )

        cur.close()
        conn.close()
        return departments
    except Exception as e:
        print("ddd")
        print(e)
        # If login failed, return None
        cur.close()
        conn.close()
        return []



#####################################################
#   Query (c)
#   Get My Issued Devices
#####################################################

def get_issued_devices_for_user(employee_id: int) -> list:
    """
    Get all devices issued to the user.
        - Return a list of all devices to the user.
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        # SQL statement and execute
        sql = """SELECT Device.deviceID, Device.purchaseDate, Device.modelNumber, Device.manufacturer
                 FROM Employee JOIN Device ON(Employee.empid = Device.issuedTo)
                 WHERE Employee.empid = %s"""
        cur.execute(sql, (employee_id,));

        # Attempt to fetch all
        result = cur.fetchall()

        if result == None:
            cur.close()
            conn.close()
            return []

        devices = []
        for row in result:
            devices.append(
                [row[0], row[1], row[2], row[3]]
            )

        cur.close()
        conn.close()
        return devices
    except Exception as e:
        print("eee")
        print(e)
        # If login failed, return None
        cur.close()
        conn.close()
        return []


#####################################################
#   Query (b)
#   Get All Models
#####################################################

def get_all_models() -> list:
    """
    Get all models available.
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        # SQL statement and execute
        sql = """SELECT manufacturer, description, modelnumber, weight
                 FROM Model"""
        cur.execute(sql, ())

        # Attempt to fetch first row
        result = cur.fetchall()

        if result == None:
            cur.close()
            conn.close()
            return []

        models = []
        for row in result:
            models.append(
                [row[0], row[1], row[2], row[3]]
            )

        cur.close()
        conn.close()
        return models
    except Exception as e:
        print("fff")
        print(e)
        # If login failed, return None
        cur.close()
        conn.close()
        return []


#####################################################
#   Query (d[ii])
#   Get Device Repairs
#####################################################

def get_device_repairs(device_id: int) -> list:
    """
    Get all repairs made to a device.
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        # SQL statement and execute
        sql = """SELECT R.repairID, R.faultReport, R.startDate, R.endDate, R.cost
                 FROM Repair R
                 WHERE R.doneTo = %s"""
        cur.execute(sql, (device_id,))

        # Attempt to fetch first row
        result = cur.fetchall()

        if result == None:
            cur.close()
            conn.close()
            return []

        repairs = []
        for row in result:
            repairs.append(
                [row[0], row[1], row[2], row[3], row[4]]
            )

        cur.close()
        conn.close()
        return repairs
    except Exception as e:
        print("ggg")
        print(e)
        # If login failed, return empty list
        cur.close()
        conn.close()
        return []


    # TODO Dummy Data - Change to be useful!
    # Return the repairs done to a certain device
    # Each "Row" contains:
    #       - repairid
    #       - faultreport
    #       - startdate
    #       - enddate
    #       - cost
    # If no repairs = empty list

    # repairs = [
    #     [17, 'Never, The', datetime.date(2018, 7, 16), datetime.date(2018, 9, 22), '$837.13'],
    #     [18, 'Gonna', datetime.date(2018, 8, 3), datetime.date(2018, 9, 22), '$1726.99'],
    #     [19, 'Give', datetime.date(2018, 9, 4), datetime.date(2018, 9, 17), '$1751.01'],
    #     [20, 'You', datetime.date(2018, 7, 21), datetime.date(2018, 9, 23), '$1496.36'],
    #     [21, 'Up', datetime.date(2018, 8, 17), datetime.date(2018, 9, 18), '$1133.88'],
    #     [22, 'Never', datetime.date(2018, 8, 8), datetime.date(2018, 9, 24), '$1520.95'],
    #     [23, 'Gonna', datetime.date(2018, 9, 1), datetime.date(2018, 9, 29), '$611.09'],
    #     [24, 'Let', datetime.date(2018, 7, 5), datetime.date(2018, 9, 15), '$1736.03'],
    # ]
    #
    # return repairs


#####################################################
#   Query (d[i])
#   Get Device Info
#####################################################

def get_device_information(device_id: int) -> Optional[dict]:
    """
    Get related device information in detail.
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        # SQL statement and execute
        sql = """SELECT D.DeviceID, D.SerialNumber, D.PurchaseDate, D.PurchaseCost, D.Manufacturer, D.ModelNumber, D.IssuedTo
                 FROM Device D
                 WHERE D.DeviceID = %s"""
        cur.execute(sql, (device_id,))

        # Attempt to fetch all rows
        device_info = cur.fetchone()

        if device_info == None:
            cur.close()
            conn.close()
            return None

        device = {
            'device_id': device_info[0],
            'serial_number': device_info[1],
            'purchase_date': device_info[2],
            'purchase_cost': device_info[3],
            'manufacturer': device_info[4],
            'model_number': device_info[5],
            'issued_to': device_info[6],
        }

        cur.close()
        conn.close()
        return device
    except Exception as e:
        print("hhh")
        print(e)
        # If nothing was returned, return None
        cur.close()
        conn.close()
        return None

    # TODO Dummy Data - Change to be useful!
    # Return all the relevant device information for the device

    # device_info = [
    #     1,                      # DeviceID
    #     '2721153188',           # SerialNumber
    #     datetime.date(2017, 12, 19),  # PurchaseDate
    #     '$1009.10',             # PurchaseCost
    #     'Zoomzone',             # Manufacturer
    #     '9854941272',           # ModelNumber
    #     1337,                   # IssuedTo
    # ]
    #
    # device = {
    #     'device_id': device_info[0],
    #     'serial_number': device_info[1],
    #     'purchase_date': device_info[2],
    #     'purchase_cost': device_info[3],
    #     'manufacturer': device_info[4],
    #     'model_number': device_info[5],
    #     'issued_to': device_info[6],
    # }
    #
    # return device


#####################################################
#   Query (d[iii/iv])
#   Get Model Info by Device
#####################################################

def get_device_model(device_id: int) -> Optional[dict]:
    """
    Get model information about a device.
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        # SQL statement and execute
        sql = """SELECT M.manufacturer, M.modelNumber, M.description, M.weight
                 FROM Device D JOIN Model M ON(D.manufacturer = M.manufacturer AND D.modelNumber = M.modelNumber)
                 WHERE D.DeviceID = %s"""
        cur.execute(sql, (device_id,))

        # Attempt to fetch all rows
        result = cur.fetchall()

        if result == None:
            cur.close()
            conn.close()
            return result

        model = {
            'manufacturer': result[0],
            'model_number': result[1],
            'description': result[2],
            'weight': result[3],
        }

        cur.close()
        conn.close()
        return model
    except Exception as e:
        print("iii")
        print(e)
        # If nothing was returned, return None
        cur.close()
        conn.close()
        return None

    # TODO Dummy Data - Change to be useful!

    # model_info = [
    #     'Zoomzone',              # manufacturer
    #     '9854941272',            # modelNumber
    #     'brick--I mean laptop',  # description
    #     2000,                    # weight
    # ]
    #
    # model = {
    #     'manufacturer': model_info[0],
    #     'model_number': model_info[1],
    #     'description': model_info[2],
    #     'weight': model_info[3],
    # }
    # return model


#####################################################
#   Query (e)
#   Get Repair Details
#####################################################

def get_repair_details(repair_id: int) -> Optional[dict]:
    """
    Get information about a repair in detail, including service information.
    """
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # SQL statement and execute
        sql = """SELECT R.repairID, R.faultReport, R.startDate, R.endDate, R.cost, S.abn, S.serviceName, S.email, R.doneTo
                FROM Repair R JOIN Service S ON (R.doneBy = S.abn)
                WHERE R.repairID = %s"""
        cur.execute(sql, (repair_id,))
        # Attempt to fetch all rows
        result = cur.fetchone()
        if result == None:
            cur.close()
            conn.close()
            return None
        repair = {
            'repair_id': result[0],
            'fault_report': result[1],
            'start_date': result[2],
            'end_date': result[3],
            'cost': result[4],
            'done_by': {
                'abn': result[5],
                'service_name': result[6],
                'email': result[7],
            },
            'done_to': result[8],
        }
        cur.close()
        conn.close()
        return repair
    except Exception as e:
        print("jjj")
        print(e)
        # If nothing was returned, return None
        cur.close()
        conn.close()
        return None

    # TODO Dummy data - Change to be useful!

    # repair_info = [
    #     17,                    # repair ID
    #     'Never, The',          # fault report
    #     datetime.date(2018, 7, 16),  # start date
    #     datetime.date(2018, 9, 22),  # end date
    #     '$837.13',             # cost
    #     '12345678901',         # service ABN
    #     'TopDrive',            # service name
    #     'repair@example.com',  # service email
    #     1,                     # done to device
    # ]
    #
    # repair = {
    #     'repair_id': repair_info[0],
    #     'fault_report': repair_info[1],
    #     'start_date': repair_info[2],
    #     'end_date': repair_info[3],
    #     'cost': repair_info[4],
    #     'done_by': {
    #         'abn': repair_info[5],@
    #         'service_name': repair_info[6],
    #         'email': repair_info[7],
    #     },
    #     'done_to': repair_info[8],
    # }
    # return repair


#####################################################
#   Query (f[ii])
#   Get Models assigned to Department
#####################################################

def get_department_models(department_name: str) -> list:
    # """
    # Return all models assigned to a department.
    # """

    print(department_name)
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # SQL statement and execute
        sql = """SELECT manufacturer, modelNumber, maxNumber
                 FROM ModelAllocations
                 WHERE ModelAllocations.department = %s"""
        cur.execute(sql, (department_name,))
        # Attempt to fetch all rows
        result = cur.fetchall()
        if result == None:
            cur.close()
            conn.close()
            return []
        models = []
        for row in result:
            models.append(
                [row[0], row[1], row[2]]
            )

        cur.close()
        conn.close()
        return models
    except Exception as e:
        print("kkk")
        print(e)
        # If nothing was returned, return None
        cur.close()
        conn.close()
        return []

    # TODO Dummy Data - Change to be useful!
    # Return the models allocated to the department.
    # Each "row" has: [ manufacturer, modelnumber, maxnumber ]

    # model_allocations = [
    #     ['Devpulse', '4030141218', 153],
    #     ['Gabcube', '1666158895', 186],
    #     ['Feednation', '2050267274', 275],
    #     ['Zoombox', '8860068207', 199],
    #     ['Shufflebeat', '0288809602', 208],
    #     ['Voonyx', '5275001460', 264],
    #     ['Tagpad', '3772470904', 227],
    # ]
    #
    # return model_allocations


#####################################################
#   Query (f[iii])
#   Get Number of Devices of Model owned
#   by Employee in Department
#####################################################

def get_employee_department_model_device(department_name: str, manufacturer: str, model_number: str) -> list:
    """
    Get the number of devices owned per employee in a department
    matching the model.
    """
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        # SQL statement and execute
        sql = """SELECT Employee.empid, Employee.name, count(Device.DeviceID)
                 FROM ( Employee JOIN EmployeeDepartments USING(empid) ) JOIN Device ON(Employee.empid = Device.issuedTo)
                 WHERE EmployeeDepartments.department  = %s
                      AND Device.manufacturer = %s
                      AND Device.modelNumber = %s
                 GROUP BY Employee.empid, Employee.name"""
        cur.execute(sql, (department_name, manufacturer, model_number))

        # Attempt to fetch all rows
        result = cur.fetchall()

        if result == None:
            cur.close()
            conn.close()
            return []

        models = []
        for row in result:
            models.append(
                [row[0], row[1], row[2]]
            )

        cur.close()
        conn.close()
        return models
    except Exception as e:
        print("lll")
        print(e)
        # If nothing was returned, return empty list
        cur.close()
        conn.close()
        return []


    # E.g. Model = iPhone, Manufacturer = Apple, Department = "Accounting"
    #     - [ 1337, Misty, 20 ]
    #     - [ 351, Pikachu, 10 ]
    # """
    #
    # # TODO Dummy Data - Change to be useful!
    # # Return the number of devices owned by each employee matching department,
    # #   manufacturer and model.
    # # Each "row" has: [ empid, name, number of devices issued that match ]
    #
    # employee_counts = [
    #     [1337, 'Misty', 20],
    #     [351, 'Pikachu', 1],
    #     [919, 'Hermione', 8],
    # ]
    #
    # return employee_counts


#####################################################
#   Query (f[iv])
#   Get a list of devices for a certain model and
#       have a boolean showing if the employee has
#       it issued.
#####################################################

def get_model_device_assigned(model_number: str, manufacturer: str, employee_id: int) -> list:
    """
    Get all devices matching the model and manufacturer and show True/False
    if the employee has the device assigned.

    E.g. Model = Pixel 2, Manufacturer = Google, employee_id = 1337
        - [123656, False]
        - [123132, True]
        - [51413, True]
        - [8765, False]
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        # SQL statement and execute
        sql = """SELECT Device.deviceID,
                        CASE WHEN (Device.issuedTo = %s) THEN TRUE
                                                        ELSE FALSE
                        END
                 FROM Device
                 WHERE Device.manufacturer = %s AND Device.modelNumber = %s"""
        cur.execute(sql, (employee_id, manufacturer, model_number))

        # Attempt to fetch all rows
        result = cur.fetchall()

        if result == None:
            cur.close()
            conn.close()
            return []

        device_assigned = []
        for row in result:
            device_assigned.append(
                [row[0], bool(row[1])]
            )

        cur.close()
        conn.close()
        return device_assigned
    except Exception as e:
        print("mmm")
        print(e)
        # If nothing was returned, return empty list
        cur.close()
        conn.close()
        return []

    # TODO Dummy Data - Change to be useful!
    # Return each device of this model and whether the employee has it
    # issued.
    # Each "row" has: [ device_id, True if issued, else False.]

    # device_assigned = [
    #     [123656, False],
    #     [123132, True],
    #     [51413, True],
    #     [8765, False],
    # ]
    #
    # return device_assigned


#####################################################
#   Get a list of devices for this model and
#       manufacturer that have not been assigned./home/jkwo8485/Desktop/isys2120-asst3-scaffold-master-new/isys2120-asst3-scaffold-master/database.py
def get_unassigned_devices_for_model(model_number: str, manufacturer: str) -> list:
    """
    Get all unassigned devices for the model.
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        # SQL statement and execute
        sql = """SELECT Device.deviceID
                 FROM Device
                 WHERE Device.manufacturer = %s AND Device.modelNumber = %s AND Device.IssuedTo IS NULL"""
        cur.execute(sql, (manufacturer, model_number))

        # Attempt to fetch all rows
        result = cur.fetchall()

        if result == None:
            cur.close()
            conn.close()
            return []

        unissued = []
        for row in result:
            unissued.append(
                row[0]
            )

        cur.close()
        conn.close()
        return unissued
    except Exception as e:
        print("nnn")
        print(e)
        # If nothing was returned, return empty list
        cur.close()
        conn.close()
        return []


    # TODO Dummy Data - Change to be useful!
    # Return each device of this model that has not been issued
    # Each "row" has: [ device_id ]
    # device_unissued = [123656, 123132, 51413, 8765]
    #
    # return device_unissued


#####################################################
#   Get Employees in Department
#####################################################

def get_employees_in_department(department_name: str) -> list:
    """
    Return all the employees' IDs and names in a given department.
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        # SQL statement and execute
        sql = """SELECT Employee.empid, Employee.name
                 FROM Employee JOIN EmployeeDepartments USING(empid)
                 WHERE EmployeeDepartments.department = %s"""
        cur.execute(sql, (department_name,))

        # Attempt to fetch all rows
        result = cur.fetchall()

        if result == None:
            cur.close()
            conn.close()
            return []

        employees = []
        for row in result:
            employees.append(
                [row[0], row[1]]
            )
        cur.close()
        conn.close()
        return employees
    except Exception as e:
        print("ooo")
        print(e)
        # If nothing was returned, return empty list
        cur.close()
        conn.close()
        return []

    # TODO Dummy Data - Change to be useful!
    # Return the employees in the department.
    # Each "row" has: [ empid, name ]

    # employees = [
    #     [15905, 'Rea Fibbings'],
    #     [9438, 'Julia Norville'],
    #     [36020, 'Adora Lansdowne'],
    #     [98809, 'Nathanial Farfoot'],
    #     [58407, 'Lynne Smorthit'],
    # ]
    #
    # return employees


#####################################################
#   Query (f[v])
#   Issue Device
#####################################################

def issue_device_to_employee(employee_id: int, device_id: int):
    """
    Issue the device to the chosen employee.
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        # SQL statement and execute
        sql = """SELECT COUNT(*)
                 FROM Device
                 WHERE Device.deviceID = %s AND Device.issuedTo IS NULL"""
        cur.execute(sql, (device_id,))

        # Attempt to fetch all rows
        result = cur.fetchone()

        if result[0] == 0:
            cur.close()
            conn.close()
            return(False, "Device already issued")

        # fix this later if you need to
        sql = """SELECT COUNT(*)
                 FROM EmployeeDepartments
                 WHERE empid = %s"""
        cur.execute(sql, (employee_id,))

        # Attempt to fetch all rows
        result = cur.fetchone()

        if result[0] == 0:
            cur.close()
            conn.close()
            return(False, "Employee not in department")

        sql = """UPDATE Device
                 SET issuedTo = %s
                 WHERE deviceID = %s"""
        cur.execute(sql, (employee_id, device_id))

        conn.commit()
        cur.close()
        conn.close()
        return (True, None)
    except Exception as e:
        print("ppp")
        print(e)
        # If something went wrong, return (False, None)
        cur.close()
        conn.close()
        return (False, None)

    # TODO issue the device from the employee
    # Return (True, None) if all good
    # Else return (False, ErrorMsg)
    # Error messages:
    #       - Device already issued?
    #       - Employee not in department?

    # return (False, "Device already issued")




#####################################################
#   Query (f[vi])
#   Revoke Device Issued to User
#####################################################

def revoke_device_from_employee(employee_id: int, device_id: int):
    """
    Revoke the device from the employee.
    """
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # SQL statement and execute
        sql = """SELECT COUNT(*)
                 FROM Device
                 WHERE Device.deviceID = %s AND Device.issuedTo IS NULL"""
        cur.execute(sql, (device_id,))
        # Attempt to fetch all rows
        result = cur.fetchone()

        if result[0] == 1:
            cur.close()
            conn.close()
        sql = """SELECT COUNT(*)
                 FROM Device
                 WHERE Device.deviceID = %s AND Device.issuedTo != %s"""
        cur.execute(sql, (device_id, employee_id))
        # Attempt to fetch all rowsOptional[dict]
        result = cur.fetchone()

        if result[0] == 1:
            cur.close()
            conn.close()
            return(False, "Employee not assigned to device")

        sql = """UPDATE Device
                 SET issuedTo = NULL
                 WHERE deviceID = %s"""
        cur.execute(sql, (device_id,))

        conn.commit()
        cur.close()
        conn.close()
        return (True, None)
    except Exception as e:
        print("qqq")
        print(e)
        # If something went wrong, return (False, None)
        cur.close()
        conn.close()
        return (False, None)

    # TODO revoke the device from the employee.
    # Return (True, None) if all good
    # Else return (False, ErrorMsg)
    # Error messages:
    #       - Device already revoked?
    #       - employee not assigned to device?

    # return (False, "Device already unassigned")
    # return (True, None)

###########################
######## Extension ########
###########################

def extension1() -> list:
    """
    Number of devices used by the each department
    """

    # join employeedept join deviceusedby(usedby) group

    # Note: this example system is not well-designed for security.
    # There are several serious problems. One is that the database
    # stores passwords directly; a better design would "salt" each password
    # and then hash the result, and store only the hash.
    # This is ok for a toy assignment, but do not use this code as a model when you are
    # writing a real system for a client or yourself.


    conn = database_connect()
    if(conn is None):
        return None

    cur = conn.cursor()

    try:
        # SQL statement and execute
        sql = """SELECT EmployeeDepartments.Department, COUNT(DeviceUsedBy.deviceID) AS "Number of Devices"
                 FROM EmployeeDepartments JOIN DeviceUsedBy USING(empid)
                 GROUP BY EmployeeDepartments.Department
                 ORDER BY "Number of Devices" DESC, EmployeeDepartments.Department ASC"""
        cur.execute(sql, ())

        # Attempt to fetch first row
        result = cur.fetchall()

        # If employee info returns nothing, return none
        if result == None:
            cur.close()
            conn.close()
            return []

        counts = []
        for row in result:
            counts.append(
                [row[0], row[1]]
            )

        cur.close()
        conn.close()
        return counts
    except Exception as e :
        print("ex1")
        print(e)
        # If something went really wrong
        cur.close()
        conn.close()
        return None
        # counts = [
        #     ['Legal', 10],
        #     ['af', 2]
        # ]



def extension2() -> list:
    """
    Total cost of repairs incurred by each department
    """

    conn = database_connect()
    if(conn is None):
        return None

    cur = conn.cursor()

    try:
        # SQL statement and execute
        sql = """SELECT ED.department, SUM(R.cost)
                 FROM Repair R JOIN Device D USING(deviceID)
	                  JOIN EmployeeDeparments ED ON (D.issuedTo = ED.empId)
                 GROUP BY ED.department
                 ORDER BY R.cost DESC, ED.department ASC"""
        cur.execute(sql, ())

        # Attempt to fetch first row
        result = cur.fetchall()

        # If employee info returns nothing, return none
        if result == None:
            cur.close()
            conn.close()
            return []

        costs = []
        for row in result:
            costs.append(
                [row[0], row[1]]
            )

        cur.close()
        conn.close()
        return costs
    except Exception as e :
        print("ex2")
        print(e)
        # If something went really wrong
        cur.close()
        conn.close()
        return None
