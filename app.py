from flask import Flask, render_template, request, flash,  jsonify, redirect, url_for, session
from datetime import datetime, date
import query
# 创建flask对象
app = Flask(__name__)
app.config['SECRET_KEY'] = 'gsolvit'

#初始化一个登录界面
@app.route('/')
def initial():
    return render_template('index.html')
#用户主页的设置
@app.route('/index', methods=["POST"])
def index():
    userid=request.form.get('title',type=int,default=None)
    password=request.form.get('password',type=str,default=None)
    print(userid, password)
    #获取用户信息进行校验
    sql="select * from hospital_staff"
    result=query.query(sql)

    flag = 0
    for staff in result:
        #print(staff[1],staff[2])
        if staff[0] == userid and staff[3] == password:
            username=staff[2]
            flag = 1
            break
        elif staff[0]==userid and staff[3] != password:
            flag = 0.5
            break
    if flag==1:

        return render_template('admin.html', username=username)
    elif flag==0.5:
        return render_template('index.html', flag=0.5)
    else:
        return u'您没有权限!'

#进入病人信息界面
@app.route('/order/list')
def patient_information():
    return render_template('list.html')
#退出返回登陆界面
@app.route('/user/logout')
def staff_logout():
    return render_template('index.html')

#进入病人信息界面，导入病人信息表格数据
@app.route('/order/listJson')
def get_orders():
    name=request.args.get('patient_name')
    print(name)

    categories=['patient_id','genter','year_old','patient_name','telephone']
    data=[]
    if(name==None):
        sql = "select * from patient"
        result = query.query(sql)
        for record in result:
            d = {categories[i]: record[i] for i in range(len(categories))}
            data.append(d)
        # print(data)
        data_dict = dict(code=0, msg="", count=1000, data=data)
    else:
        sql="select * from patient where patient_name='%s'"%(name)
        result = query.query(sql)
        for record in result:
            d = {categories[i]: record[i] for i in range(len(categories))}
            data.append(d)
        # print(data)
        data_dict = dict(code=0, msg="", count=1000, data=data)

    return jsonify(data_dict)

#利用视图查看病人既往病史
@app.route('/old_diseases')
def old_diseases():
    id = request.args.get('patient_id')
    print("我获得",id)
    sql = "SELECT EXISTS (SELECT 1 FROM information_schema.views WHERE table_schema = 'medical_information'AND table_name = 'disease_details') AS view_exists"
    judge_answer = query.judge_exists_view(sql)
    print(judge_answer[0][0])
    if (judge_answer[0][0] == 0):
        sql = """CREATE VIEW disease_details AS SELECT 
        medical_record.patient_id, medical_record.medical_record_id, 
        medical_record.medical_descripition,medical_record.record_time, 
        medical_record.record_department, hospital_staff.staff_name, hospital_staff.staff_id 
        FROM medical_record 
        JOIN hospital_staff ON 
        medical_record.staff_id = hospital_staff.staff_id"""
        query.create_view(sql)
    sql = "SELECT * FROM DISEASE_DETAILS WHERE patient_id='%s'" % (id)
    result = query.query(sql)
    categories = ['patient_id', 'medical_record_id', 'medical_descripition', 'record_time', 'record_department',
                  'staff_name']
    data = []
    for record in result:
        d = {categories[i]: record[i] for i in range(len(categories))}
        data.append(d)
    print(data)
    return render_template('old_diseases.html',data=data)

@app.route('/order/inlist')
def inpatient():
    return render_template('inpatient_list.html')
#进入病人信息界面，导入病人信息表格数据
@app.route('/order/inpatientlist')
def get_inpatientorders():
    name=request.args.get('patient_name')#用于搜索
    print(name)
    sql = "SELECT EXISTS (SELECT 1 FROM information_schema.views WHERE table_schema = 'medical_information'AND table_name = 'inpatient_details') AS view_exists"
    judge_answer = query.judge_exists_view(sql)
    print(judge_answer[0][0])
    if (judge_answer[0][0] == 0):
        sql = "CREATE VIEW inpatient_details AS SELECT inpatient.In_time, inpatient.bed_number, inpatient.staff_id,  inpatient.Hea_staff_id,patient.patient_name, patient.patient_id, hospital_staff.staff_name FROM inpatient JOIN patient ON patient.patient_id = inpatient.patient_id JOIN hospital_staff ON hospital_staff.staff_id = inpatient.staff_id"
        query.create_view(sql)
    categories=['patient_id','patient_name','In_time','staff_name','bed_number']
    data=[]
    if(name==None):
        sql = "select patient_id,patient_name,IN_time,staff_name,bed_number from inpatient_details"
        result = query.query(sql)
        for record in result:
            d = {categories[i]: record[i] for i in range(len(categories))}
            data.append(d)
        # print(data)
        data_dict = dict(code=0, msg="", count=1000, data=data)
    else:
        sql="select patient_id,patient_name,IN_time,staff_name,bed_number  from inpatient_details where patient_name='%s'"%(name)
        result = query.query(sql)
        for record in result:
            d = {categories[i]: record[i] for i in range(len(categories))}
            data.append(d)
        # print(data)
        data_dict = dict(code=0, msg="", count=1000, data=data)
    print(data_dict)
    return jsonify(data_dict)

@app.route('/order/delete',methods=['GET'])
def inpatient_delete():
    patient_id = request.args.get('patient_id')
    reason = request.args.get('reason')
    print(patient_id,reason)
    if reason=='正常出院':
        sql="DELETE FROM inpatient where patient_id='%s'"%(patient_id)
        query.delete(sql)
        return jsonify({'success': 1})
    elif reason=='意外去世':
        sql="DELETE FROM operation where patient_id='%s'"%(patient_id)
        query.delete(sql)
        sql="DELETE FROM inpatient where patient_id='%s'"%(patient_id)
        query.delete(sql)
        sql = "DELETE FROM patient where patient_id='%s'" % (patient_id)
        query.delete(sql)
        return jsonify({'success': 1})
    else:
        return jsonify({'success': 0})

@app.route('/order/add')
def add_patient():
    return render_template('add.html')

@app.route('/order/save',methods=['POST'])
def save_newpatient():
    name=request.form.get('patient_name')
    sex=request.form.get('sex')
    tel=request.form.get('telephone')
    date=request.form.get('date')
    year_old=request.form.get('year_old')
    department=request.form.get('department')
    doc_id=request.form.get('doctor_id')

    answer=request.form.get('need')
    bed=request.form.get('number')
    orderdate=request.form.get('orderdate')
    des=request.form.get('patient_description')
#先添加新的病人信息
    query.create_trigger1()#创建触发器用于这个病人是否已经在信息表里
    sql="INSERT INTO patient(patient_name,genter,year_old,telephone) VALUES('%s','%s','%s','%s')"%(name,sex,year_old,tel)
    query.add(sql)
    sql="SELECT patient_id FROM patient WHERE patient_name='%s' AND telephone='%s'"%(name,tel)
    result = query.query(sql)
    patient_id=result[0][0]
#更新病历
    query.create_trigger2()
    sql="INSERT INTO medical_record(patient_id,staff_id,medical_descripition,record_time,record_department) VALUES ('%s','%s','%s','%s','%s')"%(patient_id,doc_id,des,date,department)
    ##创建触发器用于插入合适的值进入record表中,记录有了
    ans=query.add(sql)
    #print('the result of add list',ans)
    if ans==1:
        if answer == '是':  # 如果病人不需要住院只需要添加病人个人信息，和病历内容
            sql = "INSERT INTO inpatient(patient_id,staff_id,Hea_staff_id,In_time,bed_number) VALUES('%s','%s','%s','%s','%s')" % (
            patient_id, doc_id, 4, orderdate, bed)
            query.add(sql)
        response_data = {'success': 1}
    else:
        response_data = {'success': 0}
    return jsonify(response_data)

@app.route('/patient/sheet')
def show_sheet():
    return render_template('sheet.html')
@app.route('/order/sheet')
def sheet_content():
    sheet_id=request.args.get('sheet_id')
    print(sheet_id)
    categories = ['sheet_id', 'medical_record_id', 'sheet_money', 'medicine_already']
    data = []
    if sheet_id==None:
        sql = "select * from prescription_sheet"
        result = query.query(sql)
        print(result)
        for record in result:
            d = {}
            for i in range(len(categories)):
                if i==2:
                    ans=float(record[i])
                    print(ans)
                    d[categories[i]] = ans
                elif i==3:
                    if record[i]==1:
                        d[categories[i]] = "是"
                    else:
                        d[categories[i]] = "否"
                else:
                    d[categories[i]] = record[i]
            data.append(d)
        print(data)
        data_dict = dict(code=0, msg="", count=1000, data=data)
        return jsonify(data_dict)
    else:
        sql = "select * from prescription_sheet where sheet_id='%s'"%(sheet_id)
        result = query.query(sql)
        print(result)
        for record in result:
            d = {}
            for i in range(len(categories)):
                if i == 2:
                    ans = float(record[i])
                    print(ans)
                    d[categories[i]] = ans
                elif i == 3:
                    if record[i] == 1:
                        d[categories[i]] = "是"
                    else:
                        d[categories[i]] = "否"
                else:
                    d[categories[i]] = record[i]
            data.append(d)
        print(data)
        data_dict = dict(code=0, msg="", count=1000, data=data)
        return jsonify(data_dict)



#用于记录付款的处方单然后进一步更新
@app.route('/pay/answer',methods=['POST'])
def update_pay_medicine():
    value=request.form.get('value')
    sheet_id=request.form.get('id')
    print(value,sheet_id)

    #更新处方和库房信息
    if value=='是':
        result=query.create_call_procedure(sheet_id)
        print(result)
        if result=='success':
            response_data = {'success': 1}
        else:
            response_data = {'success': 0}
    print(response_data)
    return jsonify(response_data)


#要处理药方这张网页啦
@app.route('/medicine/list')
def medicine_call():
    # 处理之前先需要进行删除过期药品
    sql="DELETE FROM medicine WHERE how_long <= CURDATE() OR how_many=0;"
    query.delete(sql)
    return render_template('medicine.html')

@app.route('/medicine/sheet')
def medicine_list():
    medicine_id = request.args.get('medicine_id')  # 用于搜索
    print(medicine_id)
    categories = ['medicine_id', 'medicine_name', 'how_many', 'produce_date', 'die_date']
    data = []
    if medicine_id==None:
        sql="SELECT * FROM medicine"
        result=query.query(sql)
        for record in result:
            d = {categories[i]: record[i] for i in range(len(categories))}
            data.append(d)
    # print(data)
        data_dict = dict(code=0, msg="", count=1000, data=data)
        return jsonify(data_dict)

    else:
        sql = "SELECT * FROM medicine where medicine_id='%s'"%(medicine_id)
        result = query.query(sql)
        for record in result:
            d = {categories[i]: record[i] for i in range(len(categories))}
            data.append(d)
            # print(data)
        data_dict = dict(code=0, msg="", count=1000, data=data)
        return jsonify(data_dict)



@app.route('/user/information_change')
def patient_information_change():
    return render_template('information_change.html')

@app.route('/new_information',methods=["post"])
def new_tel_password():
    userid=request.form.get('title',type=int,default=None)
    usertel=request.form.get('usertelephone',type=str,default=None)
    user_oldpass=request.form.get('oldpassword',type=str,default=None)
    user_newpass=request.form.get('newpassword',type=str,default=None)
    #sql = "INSERT INTO STUDENT VALUES ('%s','%s','%s','%s','%s','%s','%s','%s')" % (
    #name, sex, stu_no, college, major, ad_year, password, stu_no)
    #sql="SELECT staff_password FROM hospital_staff WHERE staff_id='%s'"%(userid)
    #result=query.query(sql)
    sql0="UPDATE hospital_staff SET tel='%s'WHERE staff_id='%s'"%(usertel,userid)
    result0=query.update(sql0)
    sql1="UPDATE hospital_staff SET staff_password='%s' WHERE staff_password='%s'and staff_id='%s'"%(user_newpass,user_oldpass,userid)
    result1= query.update(sql1)
    #电话信息可以直接更改
    sql2="SELECT staff_password FROM hospital_staff WHERE staff_id='%s'"%(userid)
    result2=query.query(sql2)
    print(result2[0][0])
    if result2[0][0]==user_newpass:
        flag=1
    else:
        flag=0
    return render_template('information_change.html',flag=flag)

if __name__ == '__main__':
    app.run()
