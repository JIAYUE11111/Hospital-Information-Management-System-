import pymysql
from config import config

def query(sql):
    """
    功能; 使用sql语句查询数据库中人员身份信息.
    参数: sql(string)
    """
    db = pymysql.connect(host='localhost', user='root', password=config['MYSQL_PASSWORD'], database=config['DATABASE_NAME'], charset='utf8')
    cur = db.cursor()
    try:
        cur.execute(sql)
        result = cur.fetchall()

        db.commit()

        print('query success')

    except:
        print('query loss')
        db.rollback()
    cur.close()
    db.close()
    return result

def delete(sql):
    """
    功能; 使用sql语句删除数据库中人员身份信息.
    参数: sql(string)
    """
    db = pymysql.connect(host='localhost', user='root', password=config['MYSQL_PASSWORD'], database=config['DATABASE_NAME'], charset='utf8')
    cur = db.cursor()
    try:
        cur.execute(sql)
        result = "success"

        db.commit()

        print('delete success')

    except:
        result = "loss"
        print('delete loss')
        db.rollback()
    cur.close()
    db.close()
    return result

def add(sql):
    """
    功能; 使用sql语句添加数据库中人员身份信息.
    参数: sql(string)
    """
    db = pymysql.connect(host='localhost', user='root', password=config['MYSQL_PASSWORD'], database=config['DATABASE_NAME'], charset='utf8')
    cur = db.cursor()
    try:
        cur.execute(sql)
        result = cur.fetchall()

        db.commit()
        result=1
        print('add success')

    except:
        result=0
        print('add loss')
        db.rollback()
    cur.close()
    db.close()
    return result

def update(sql):
    """
    功能; 使用sql语句更新数据库中人员身份信息.
    参数: sql(string)
    """
    db = pymysql.connect(host='localhost', user='root', password=config['MYSQL_PASSWORD'], database=config['DATABASE_NAME'], charset='utf8')
    cur = db.cursor()
    try:
        cur.execute(sql)
        result = cur.fetchall()

        db.commit()
        str='update success'


    except:
        str='update loss'
        db.rollback()
    cur.close()
    db.close()
    return str

def create_trigger1():
    db = pymysql.connect(host='localhost', user='root', password=config['MYSQL_PASSWORD'], database=config['DATABASE_NAME'], charset='utf8')
    cur = db.cursor()
    try:
        cur.execute("DROP TRIGGER IF EXISTS add_patient;")
        # 创建触发器
        create_trigger_query = """
        CREATE TRIGGER add_patient
        BEFORE INSERT ON patient
        FOR EACH ROW
        BEGIN
            IF EXISTS (SELECT * FROM patient WHERE patient_name = NEW.patient_name AND telephone = NEW.telephone) THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '数据已经存在，不需要再插入';
            END IF;
        END ;
        
        """

        cur.execute(create_trigger_query)
        db.commit()

        print('create success')
        result='success'

    except:
        print('create loss')
        result='loss'
        db.rollback()
    cur.close()
    db.close()
    return result


def create_trigger2():
    db = pymysql.connect(host='localhost', user='root', password=config['MYSQL_PASSWORD'],
                         database=config['DATABASE_NAME'], charset='utf8')
    cur = db.cursor()
    try:
        cur.execute("DROP TRIGGER IF EXISTS add_medical_record;")
        # 创建触发器
        create_trigger_query = """
        CREATE TRIGGER add_medical_record
BEFORE INSERT ON medical_record
FOR EACH ROW
BEGIN
  IF NEW.staff_id NOT IN (SELECT staff_id FROM hospital_staff)
  OR NEW.record_department NOT IN (SELECT department_name FROM department)
  THEN
  SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '插入被拒绝';
  END IF;
END;
        """
        cur.execute(create_trigger_query)
        db.commit()
        print('create success')
        result = 'success'
    except:
        print('create loss')
        result = 'loss'
        db.rollback()
    cur.close()
    db.close()
    return result

def create_call_procedure(number):
    db = pymysql.connect(host='localhost', user='root', password=config['MYSQL_PASSWORD'],
                         database=config['DATABASE_NAME'], charset='utf8')
    cur = db.cursor()
    try:
        cur.execute("DROP PROCEDURE IF EXISTS update_info;")
        # 创建过程
        create_PROCEDURE_query = """
        
CREATE PROCEDURE update_info(IN inputID INT)
BEGIN
    IF EXISTS (
        SELECT medicine.medicine_id 
        FROM contain
        JOIN medicine ON contain.medicine_id = medicine.medicine_id 
        WHERE contain.sheet_id = inputID
        AND contain.how_many > medicine.how_many
    )
    THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'UPDATE IS NOT ACCEPTED AS 库存不足';
    END IF;

    UPDATE medicine, contain 
    SET medicine.how_many = medicine.how_many - contain.how_many
    WHERE medicine.medicine_id = contain.medicine_id 
    AND contain.sheet_id = inputID;

    UPDATE prescription_sheet 
    SET medicine_already = 1 
    WHERE sheet_id = inputID;
END;

        """
        cur.execute(create_PROCEDURE_query)
        cur.callproc('update_info', [number])

        db.commit()
        print('call procedure_success')
        result = 'success'

    except:
        print('call procedure_loss')
        result = 'loss'
        db.rollback()
    cur.close()
    db.close()
    return result
def judge_exists_view(sql):
    db = pymysql.connect(host='localhost', user='root', password=config['MYSQL_PASSWORD'],
                         database=config['DATABASE_NAME'], charset='utf8')
    cur = db.cursor()
    try:
        cur.execute(sql)
        result = cur.fetchall()

        db.commit()

        print('judge success')
    except:
        print('judge loss')
        db.rollback()
    cur.close()
    db.close()
    return result

def create_view(sql):

    db = pymysql.connect(host='localhost', user='root', password=config['MYSQL_PASSWORD'],database=config['DATABASE_NAME'], charset='utf8')
    cur = db.cursor()
    try:
        cur.execute(sql)
        result = cur.fetchall()

        db.commit()

        print('create success')
    except:
        print('create loss')
        db.rollback()
    cur.close()
    db.close()
    return result
