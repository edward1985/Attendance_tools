# -*- coding: utf-8 -*-
__author__ = 'Gongming Yang'
# Created and owned by:Gongming Yang
# Whelcome to use this tool to record attendance

'''
2015-Dec-20 change student info to allow more hierarchy statistic function
'''
import datetime,time;
import sqlite3

def time_str_int(strtime=None):
  # time.mktime(time.strptime('2014-01-01','%Y-%m-%d'));
  if strtime==None or strtime==u'':
    return None;
  try:
    return int(time.mktime(time.strptime(strtime,'%Y-%m-%d')));
  except:
    try:
      return int(time.mktime(time.strptime(strtime,'%Y/%m/%d')));
    except:
      try:
        return int(time.mktime(time.strptime(strtime,'%Y.%m.%d')));
      except:
        try:
          return int(time.mktime(time.strptime(strtime,'%m/%d/%Y')));
        except:
          print "unknown year format"
          return None;

def time_str_int_min(strtime=None):
  # time.mktime(time.strptime('2014-01-01','%Y-%m-%d'));
  if strtime==None or strtime==u'':
    return None;
  strtime=strtime.strip();
  try:
    return int(time.mktime(time.strptime(strtime,'%Y-%m-%d %H:%M')));
  except:
    try:
      return int(time.mktime(time.strptime(strtime,'%Y-%m-%d %H:')));
    except:
      try:
        return int(time.mktime(time.strptime(strtime,'%Y-%m-%d %H')));
      except:
        try:
          return int(time.mktime(time.strptime(strtime,'%Y-%m-%d')));
        except:
          print "unknown year format"
          return None;

def time_int_str(ttime):
  return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(ttime))

def time_int_str_min(ttime):
  return time.strftime('%Y-%m-%d %H:%M',time.localtime(ttime))

def time_int_str_day(ttime):
  return time.strftime('%Y-%m-%d',time.localtime(ttime))

def get_value(val):
  if val==None:
    return 0;
  else:
    return val;

def get_int(strnum):
  if strnum=='None' or strnum==None or strnum==u'':
    return int(0);
  else:
    return int(strnum);

def sum_val(strnum,num):
  if strnum=='None' or strnum==None or strnum==u'':
    return int(num);
  else:
    return int(strnum)+int(num);

def sum_val_str(strnum,num):
  if strnum=='None' or strnum==None or strnum==u'':
    return str(num);
  else:
    return str(int(strnum)+int(num));

def get_val_unicode(val,code='utf8'):
  if val==None:
    return 0;
  else:
    # print val;
    t= unicode(val).encode(code);
    return t;

def get_course_key(course):
  return course[1];#gl_time

def add_constraints(field,fname,param=[],op="=",co=" and "):
  str ='';
  if field != None:
    str = co + fname + " " + op +" ? ";
    param.append(field);
  return str;

def add_update_set_increase(field,fname,param):
    # if field!=None:
    #   sval="number=:number + number,"
    #   param.append("number")
    # tsql+=" where 1=1 "
    sval = "";
    if field!=None:
      sval ="," + fname +"=?" + " + "+ fname+" ";
      param.append(field);
    return sval;

#encode
def en(name):
  return name;
  # return name.encode("gbk").encode("base64");

def de(name):
  return name;
  # return name.decode("base64").encode("gbk");

class zbc_conn(object):
  def __init__(self,fname):
    self.conn = sqlite3.connect(fname);
    self.table_field={}

    #semester can be flexible defined to help statistics
    self.table_field["semester"] = ["jiebie","semester","stime","etime"]

    self.table_field["groups"] = ["major","jiebie","department","sub_department","class_room"]

    self.table_field["class_require"]=["jiebie","course_name",\
                                  "type","stat_type","heritage","faben","group_learn",\
                                  "number","duration","total_duration",\
                                  "gl_time"];
    self.table_field["u_url"]=["uname","uurl","upos"];
     #primary key: student_id,jiebie,class_room
    self.table_field["student"]=\
      ["student_id","nick_name","jiebie","class_room",\
       "app_user","default_semester","status",\
       "remarks","remarks_student_id","insert_time",
       ]
    #name = mouse_list
    self.table_field["value_list"]=["name","value"]

    self.table_field["attendance"]=\
       ["student_id","jiebie","course_name","class_room",
        "report","attend_ot","leave_ot","remarks","insert_time"]

    #for kaoqin only
    self.table_field["u_student"]=\
       ["yynum","serial_num","real_name",\
        "nick_name","status","mod_time"]
    self.table_field["kaoqin_table"]=\
       ["jiebie","course_name","kaoqinyuan_id",\
        "student_id","nick_name","record","kaoqin_time"]
    '''
    #yynum vs student_id; nick_name=nick_name
    '''

    #key: jiebie,course_name,kaoqinyuan_id,student_id

    self.table_field["records"]=["student_id","jiebie","course_name",\
                                 "type","stat_type","heritage","faben",\
                            "group_learn","number","total_duration","ftime"]

    #undo=0 means already inserted. undo=1 means already undo.
    self.table_field["records_history"]=["student_id","jiebie","course_name","type","stat_type","heritage","faben",\
                            "group_learn","number","duration","ftime","record_time","undo"]

    self.create_tables();


  def import_records(self,dbname,tablename="records"):
    sconn = sqlite3.connect(dbname);
    scur = sconn.cursor();
    tsql = "select ";
    for field in self.table_field[tablename]:
      tsql += field+',';

    tsql = tsql[:-1] + " from " + tablename +";" ;
    scur.execute(tsql);
    data = None;
    data = scur.fetchall();
    scur.close();
    sconn.close();

    #import into current database
    self.replace_into_many(tablename,data);
  def create_tables(self):
    # f=open("data/db.txt",'r');
    # tsql = f.read();

    cur = self.conn.cursor();
    tsql = """
      create table if not exists u_student(
             yynum nvarchar,
             serial_num nvarchar,
             real_name nvarchar,
             nick_name nvarchar,
             status nvarchar(3),
             mod_time int,
             constraint P_u_student1 primary key(serial_num)
      );
    """
    cur.executescript(tsql);
    self.conn.commit();
    tsql = """
        CREATE INDEX if not exists index_u_student1 ON u_student (yynum);
    """
    cur.executescript(tsql);
    self.conn.commit();


    cur = self.conn.cursor();
    tsql = """
      create table if not exists u_url(
             uname nvarchar,
             uurl nvarchar,
             upos int,
             constraint P_semester1 primary key(uname)
      );
    """
    cur.executescript(tsql);
    self.conn.commit();

    cur = self.conn.cursor();
    tsql = """
      create table if not exists value_list(
             name nvarchar,
             value nvarchar,
             constraint P_semester1 primary key(name)
      );
    """
    cur.executescript(tsql);
    self.conn.commit();

    tsql = """
      create table if not exists semester(
             jiebie nvarchar,
             semester nvarchar,
             stime float,
             etime float,
             constraint P_semester1 primary key(jiebie,semester)
      );
    """
    cur.executescript(tsql);
    self.conn.commit();

    tsql = """
      create table if not exists groups(
             jiebie nvarchar,
             department nvarchar,
             sub_department nvarchar,
             class_room nvarchar,
             major nvarchar not null,
             constraint P_semester1 primary key(jiebie,department,sub_department,class_room)
      );
    """
    cur.executescript(tsql);
    self.conn.commit();


    #by add gl_time as part of primary key, the course_name can be the same.
    #e.g. ketou gl_time1, ketou gl_time2, ketou gl_time3. then ketou is equal to sum of gl_time(1,2,3)
    tsql = """
      CREATE TABLE IF NOT EXISTS class_require (
              jiebie  NVARCHAR ,
              course_name  NVARCHAR NOT NULL,
              type  NVARCHAR ,
              stat_type  NVARCHAR ,
              heritage INTEGER,
              faben INTEGER,
              group_learn INTEGER,
              number INTEGER,
              duration INTEGER,
              total_duration INTEGER,
              gl_time float,
              CONSTRAINT primary1 PRIMARY KEY (jiebie,course_name,gl_time)
      );
    """
    cur.executescript(tsql);
    self.conn.commit();

    # student: unique_id,real_name,nick_name,mayjor, jiebie ,department, class_room，     rolltime,  status, insert_time, app_user
    #       ( 学号,      名字       昵称       主修   界别  , 分区   ,班级           注册本班时间,   状态,  变更时间,   是否是当前正在使用的本app)
    #          13Q01    张三        圆         前行   15届     网络    第一小组           2015        在册    2015       True
    #
    # tsql_old_version = """
    #   CREATE TABLE IF NOT EXISTS student (
    #           Buddhism_name  NVARCHAR NOT NULL,
    #           real_name  NVARCHAR ,
    #           jiebie  NVARCHAR ,
    #           group_name  NVARCHAR ,
    #           location  NVARCHAR ,
    #           insert_time float,
    #           PRIMARY KEY (Buddhism_name,jiebie,group_name)
    #   );
    # """
    #insert_time is used to record the changing of the status. It is better to separate this table.
    tsql = """
      CREATE TABLE IF NOT EXISTS student (
              student_id  NVARCHAR NOT NULL,
              nick_name  NVARCHAR DEFAULT '',
              jiebie  NVARCHAR ,
              class_room  NVARCHAR ,
              app_user  NVARCHAR ,
              default_semester  NVARCHAR ,
              rolltime float,
              status  NVARCHAR ,
              remarks  NVARCHAR ,
              remarks_student_id  NVARCHAR ,
              insert_time float,
              PRIMARY KEY (student_id,jiebie,class_room,insert_time)
      );
    """
    cur.executescript(tsql);
    self.conn.commit();

    # tsql = """
    #   CREATE TABLE IF NOT EXISTS student_status (
    #           student_id  NVARCHAR NOT NULL,
    #           jiebie  NVARCHAR ,
    #           class_room NVARCHAR,
    #           status  NVARCHAR ,
    #           remarks  NVARCHAR ,
    #           remarks_student_id  NVARCHAR ,
    #           insert_time float,
    #           PRIMARY KEY (student_id,jiebie,insert_time)
    #   );
    # """
    # cur.executescript(tsql);
    # self.conn.commit();

    '''
    self.table_field["kaoqin_table"]=\
       ["jiebie","course_name","kaoqinyuan_id",\
        "student_id","nick_name","record","kaoqin_time"]
    '''
    #insert_time is used to record the changing of the status. It is better to separate this table.
    tsql = """
      CREATE TABLE IF NOT EXISTS kaoqin_table (
              jiebie  NVARCHAR ,
              course_name NVARCHAR ,
              kaoqinyuan_id NVARCHAR ,
              student_id  NVARCHAR NOT NULL,
              nick_name  NVARCHAR DEFAULT '',
              record  NVARCHAR,
              kaoqin_time float,
              PRIMARY KEY (jiebie,course_name,kaoqinyuan_id,student_id,record)
      );
    """
    cur.executescript(tsql);
    self.conn.commit();

    tsql = """
      CREATE TABLE IF NOT EXISTS attendance (
              student_id  NVARCHAR NOT NULL,
              jiebie  NVARCHAR ,
              course_name  NVARCHAR DEFAULT '',
              class_room  NVARCHAR DEFAULT '',
              report NVARCHAR,
              attend_ot NVARCHAR,
              leave_ot NVARCHAR,
              remarks  NVARCHAR DEFAULT '',
              insert_time float,
              PRIMARY KEY (student_id,jiebie,class_room,course_name,insert_time)
      );
    """
    cur.executescript(tsql);
    self.conn.commit();

    tsql = """
      CREATE TABLE IF NOT EXISTS records (
              student_id  NVARCHAR NOT NULL,
              jiebie NVARCHAR NOT NULL,
              course_name  NVARCHAR NOT NULL,
              type    NVARCHAR NOT NULL,
              stat_type  NVARCHAR ,
              heritage INTEGER,
              faben INTEGER,
              group_learn INTEGER,
              number INTEGER,
              total_duration INTEGER,
              ftime float,
              CONSTRAINT main_class_primary1 PRIMARY KEY (jiebie,course_name,student_id,ftime)
      );
    """
    cur.executescript(tsql);
    self.conn.commit();

    tsql = """
      CREATE TABLE if not exists records_history (
              student_id  NVARCHAR NOT NULL,
              jiebie NVARCHAR NOT NULL,
              course_name  NVARCHAR NOT NULL,
              type    NVARCHAR NOT NULL,
              stat_type  NVARCHAR ,
              heritage INTEGER,
              faben INTEGER,
              group_learn INTEGER,
              number INTEGER,
              duration INTEGER,
              ftime float,
              record_time float,
              undo INTEGER,
              CONSTRAINT main_class_primary1 PRIMARY KEY (student_id,jiebie,course_name,record_time)
      );
    """
    cur.executescript(tsql);
    self.conn.commit();

    tsql = """
       create index if not exists require_index_001 on class_require (course_name);
    """
    cur.executescript(tsql);
    self.conn.commit();

    tsql = """
        CREATE INDEX if not exists student_idx_col12 ON student (student_id,jiebie);
    """
    cur.executescript(tsql);
    self.conn.commit();

    cur.close()
  def replace_into(self,tablename,param):
    tsql="replace into "+tablename+"(";
    f = "";
    for field in self.table_field[tablename]:
      tsql += field+',';
      f += "?,";
    tsql = tsql[:-1]+") "+"values(" + f[:-1] + ");";
    cur = self.conn.cursor();
    cur.execute(tsql,param);
    self.conn.commit();
    cur.close();

  def update_student_status(self,tparam):
    tsql="update student set status=?,remarks=?,remarks_student_id=?,insert_time=?" \
         " where student_id=? and jiebie=? and insert_time = (select max(insert_time) from student where" \
         " student_id=? and jiebie=? );";
    param = [tparam[6],tparam[7],tparam[8],tparam[9],tparam[0],tparam[2],tparam[0],tparam[2]]

    cur = self.conn.cursor();
    cur.execute(tsql,param);
    self.conn.commit();
    cur.close();

  def get_registed_user(self):
    tsql="select yynum,serial_num,real_name,nick_name from u_student" \
         " where status=? "
    param = [u'是'];
    cur = self.conn.cursor();
    cur.execute(tsql,param);
    ret = cur.fetchall();
    cur.close();
    return ret;

  def get_all_user_with_data(self,course_name=None):
    tsql="select course_name,student_id,nick_name,record from kaoqin_table ";

    cur = self.conn.cursor();
    if course_name!=None:
      param = [course_name];
      tsql += " where course_name=? "
      cur.execute(tsql,param);
    else:
      cur.execute(tsql);
    ret = cur.fetchall();
    cur.close();
    return ret;

  def get_kaoqin(self,cname=None):
    tsql="" \
         "select us.nick_name,us.real_name,us.serial_num,us.yynum,us.status," \
         " kt.course_name,kt.student_id,kt.nick_name,kt.record,kt.kaoqin_time " \
         " from u_student as us left join kaoqin_table as kt " \
         " on us.nick_name=kt.nick_name where kt.course_name=?"\
         " union all " \
         " select us.nick_name,us.real_name,us.serial_num,us.yynum,us.status," \
         " kt.course_name,kt.student_id,kt.nick_name,kt.record,kt.kaoqin_time " \
         " from kaoqin_table as kt left join u_student as us  " \
         " on us.nick_name=kt.nick_name where us.nick_name isnull and kt.course_name=? ";

    param = [cname,cname]
    tsql = tsql + " order by kt.course_name desc,kt.nick_name,kt.student_id "
    cur = self.conn.cursor();
    if len(param)==0:
      cur.execute(tsql);
    else:
      cur.execute(tsql,param)
    ret = None;
    ret = cur.fetchall();
    cur.close();
    return ret;

  def get_all_kaoqin(self,cname=None):
    tsql="" \
         "select us.nick_name,us.real_name,us.serial_num,us.yynum,us.status," \
         " kt.course_name,kt.student_id,kt.nick_name,kt.record,kt.kaoqin_time " \
         " from u_student as us left join kaoqin_table as kt " \
         " on us.nick_name=kt.nick_name "\
         " union all " \
         " select us.nick_name,us.real_name,us.serial_num,us.yynum,us.status," \
         " kt.course_name,kt.student_id,kt.nick_name,kt.record,kt.kaoqin_time " \
         " from kaoqin_table as kt left join u_student as us  " \
         " on us.nick_name=kt.nick_name where us.nick_name isnull";

    tsql = tsql + " order by kt.course_name desc,kt.nick_name,kt.student_id "
    cur = self.conn.cursor();
    cur.execute(tsql);
    ret = cur.fetchall();
    cur.close();
    return ret;

  def get_all_kaoqin_yy(self,cname=None):
    tsql="" \
         "select us.nick_name,us.real_name,us.serial_num,us.yynum,us.status," \
         " kt.course_name,kt.student_id,kt.nick_name,kt.record,kt.kaoqin_time " \
         " from u_student as us left join kaoqin_table as kt " \
         " on us.yynum=kt.student_id "\
         " union all " \
         " select us.nick_name,us.real_name,us.serial_num,us.yynum,us.status," \
         " kt.course_name,kt.student_id,kt.nick_name,kt.record,kt.kaoqin_time " \
         " from kaoqin_table as kt left join u_student as us  " \
         " on us.yynum=kt.student_id where us.yynum isnull";

    tsql = tsql + " order by kt.course_name desc,kt.nick_name,kt.student_id "
    cur = self.conn.cursor();
    cur.execute(tsql);
    ret = cur.fetchall();
    cur.close();
    return ret;

  def get_value_table(self,name="mouse_list"):
    tsql="select value from value_list where name=? ;";
    param = [name]

    cur = self.conn.cursor();
    cur.execute(tsql,param)
    ret = None;
    ret = cur.fetchall();
    cur.close();
    return ret;

  def clear_db_class_student(self):
    tsql="delete from class_require;";
    cur = self.conn.cursor();
    cur.execute(tsql);
    self.conn.commit();
    cur.close();

    tsql="delete from student;";
    cur = self.conn.cursor();
    cur.execute(tsql);
    self.conn.commit();
    cur.close();

    tsql="delete from semester;";
    cur = self.conn.cursor();
    cur.execute(tsql);
    self.conn.commit();
    cur.close();

    tsql="delete from groups;";
    cur = self.conn.cursor();
    cur.execute(tsql);
    self.conn.commit();
    cur.close();

  def stat_student_status(self,stime,etime,jiebie=None,student_id=None,class_room=None,section="min"):
    tsql = "select jiebie,class_room,student_id,status "+section+"(insert_time) from student where 1=1 ";
    param=[]
    tsql += self.add_constraints(jiebie,"jiebie",param);
    tsql += self.add_constraints(student_id,"student_id",param);
    tsql += self.add_constraints(class_room,"class_room",param);

    tsql += self.add_constraints(stime,"insert_time",param,">=");
    tsql += self.add_constraints(etime,"insert_time",param,"<=");

    tsql += " group by student_id,jiebie,class_room order by jiebie,class_room"

    cur = self.conn.cursor();
    if len(param)==0:
      cur.execute(tsql);
    else:
      cur.execute(tsql,param)
    ret = None;
    ret = cur.fetchall();
    cur.close();
    return ret;
  def stat_student_attendance(self):
    tsql = "select jiebie,student_id,count(course_name),max(insert_time) from attendance group by student_id,jiebie"
    cur = self.conn.cursor();
    cur.execute(tsql);
    ret = None;
    ret = cur.fetchall();
    cur.close();
    return ret;
  def clear_default_user(self):
    tsql="update student set app_user=''"
    cur = self.conn.cursor();
    cur.execute(tsql);
    self.conn.commit();
    cur.close();
  # clear all user and then set the only default user.
  def set_default_user(self,student_id,default_semester=None):
    self.clear_default_user();
    tsql="update student set app_user=? where student_id=?"
    tsql="update student set app_user=? "
    param=[u"是"]
    if default_semester!=None:
      param.append(default_semester);
      tsql+=",default_semester=? "
    tsql += " where student_id=? ";
    param.append(student_id);

    cur = self.conn.cursor();
    cur.execute(tsql,param);
    self.conn.commit();
    cur.close();
  def replace_into_many(self,tablename,param):
    tsql="insert or replace into "+tablename+"(";
    f = "";
    for field in self.table_field[tablename]:
      tsql += field+',';
      f += "?,";
    tsql = tsql[:-1]+") "+"values(" + f[:-1] + ");";

    cur = self.conn.cursor();
    cur.executemany(tsql,param);
    self.conn.commit();
    cur.close();
  def remove_records(self,student_id=None,jiebie=None,course_name=None,ftime=None):
    param = [];
    tsql = "delete from records "

    tsql+=" where 1=1 "
    tsql+=add_constraints(student_id,"student_id",param)
    tsql+=add_constraints(jiebie,"jiebie",param)
    tsql+=add_constraints(course_name,"course_name",param)
    tsql+=add_constraints(ftime,"ftime",param)

    cur = self.conn.cursor();
    if len(param)>0:
      cur.execute(tsql,param);
    else:
      cur.execute(tsql);
    self.conn.commit()
    cur.close();
    return;
  def update_records(self,student_id=None,jiebie=None,course_name=None,
                     number = None,duration=None,heritage=None,faben=None,group_learn=None,):
    param = [];
    tsql = "update records set "

    sval = ""
    sval += add_update_set_increase(number,"number",param);
    sval += add_update_set_increase(duration,"duration",param);
    sval += add_update_set_increase(heritage,"heritage",param);
    sval += add_update_set_increase(faben,"faben",param);
    sval += add_update_set_increase(group_learn,"group_learn",param);

    if len(sval)==0:
      return; #nothing need to be updated

    tsql += sval[1:];

    tsql+=" where 1=1 "
    #field,fname,param=[],op="=",co=" and "):
    tsql+=add_constraints(student_id,"student_id",param)
    tsql+=add_constraints(jiebie,"jiebie",param)
    tsql+=add_constraints(course_name,"course_name",param)

    cur = self.conn.cursor();
    if len(param)>0:
      cur.execute(tsql,param);
    else:
      cur.execute(tsql);
    cur.close();
    return;
  def get_latest_done_history(self,student_id=None,jiebie=None,course_name=None,semester=None):
    tsql = " select stat_type, heritage, faben, group_learn, number, duration,  ftime , record_time" \
           " from records_history" \
           " where undo=0 "
    tmp =[];
    flag = False
    if student_id!=None:
      tmp.append(student_id);
      tsql += " and student_id = ? "
      flag = True;

    if jiebie!=None:
      tmp.append(jiebie);
      tsql += " and jiebie = ? "
      flag = True;

    if course_name!=None:
      tmp.append(course_name);
      tsql += " and course_name = ? "
      flag = True;

    if semester!=None:
      tmp.append(semester);
      tsql += " and semester = ? "
      flag = True;

    tsql += " order by record_time desc limit 1 "

    cur = self.conn.cursor();
    if flag:
      cur.execute(tsql,tmp);
    else:
      cur.execute(tsql);

    ret = None;
    ret = cur.fetchall();
    cur.close();

    if len(ret)>0:
      self.update_latest_done_history(student_id,jiebie,course_name,semester,ret[0][7]);
      return ret[0];
    else:
      return None;
  def update_latest_done_history(self,student_id=None,jiebie=None,course_name=None,semester=None,record_time=None):
    tsql = " update records_history set undo=1" \
           " where 1=1 "
    tmp =[];
    flag = False
    if student_id!=None:
      tmp.append(student_id);
      tsql += " and student_id = ? "
      flag = True;

    if jiebie!=None:
      tmp.append(jiebie);
      tsql += " and jiebie = ? "
      flag = True;

    if course_name!=None:
      tmp.append(course_name);
      tsql += " and course_name = ? "
      flag = True;

    if semester!=None:
      tmp.append(semester);
      tsql += " and semester = ? "
      flag = True;

    if record_time!=None:
      tmp.append(record_time);
      tsql += " and record_time = ? "
      flag = True;

    cur = self.conn.cursor();
    if flag:
      cur.execute(tsql,tmp);
    else:
      cur.execute(tsql);

    self.conn.commit();
    cur.close();
    return ;
  def get_semester(self,jiebie=None):

    tsql = "select jiebie,semester,stime,etime from semester where 1=1 "

    param = []
    if jiebie!=None:
      param.append(jiebie)
      tsql += " and jiebie=? "

    cur = self.conn.cursor();
    if len(param)>0:
      cur.execute(tsql,param);
    else:
      cur.execute(tsql);

    ret = cur.fetchall();
    cur.close();
    return ret;

  def get_semester_list(self,jiebie=None):
    ret = self.get_semester(jiebie)
    sem = {}
    for row in ret:
      if row[0] not in sem:
        sem[row[0]]=[[row[1],row[2],row[3]]]
      else:
        sem[row[0]].append([row[1],row[2],row[3]])

    return sem;
  def get_all_r_class(self,jiebie=None,stime=None,etime=None,course_name=None):

    tsql = "select "
    for t in self.table_field["class_require"]:
      tsql += t+","
    tsql =tsql[:-1] + " from class_require where 1=1 "
    param = [];
    tsql+=add_constraints(jiebie,"jiebie",param)
    tsql+=add_constraints(course_name,"course_name",param)
    tsql+=add_constraints(stime,"gl_time",param,op=">=")
    tsql+=add_constraints(etime,"gl_time",param,op="<=")

    tsql +=  " order by jiebie,course_name "

    cur = self.conn.cursor();
    if len(param)>0:
      cur.execute(tsql,param);
    else:
      cur.execute(tsql);

    ret = None;
    ret = cur.fetchall();
    cur.close();
    return ret;
  def get_all_records(self,jiebie=None,stime=None,etime=None,course_name=None,student_id=None):
    tsql = "select "
    for t in self.table_field["records"]:
      tsql += t+","
    tsql = tsql[:-1] + " from records where 1=1 "
    param = [];
    tsql+=add_constraints(jiebie,"jiebie",param)
    tsql+=add_constraints(course_name,"course_name",param)
    tsql+=add_constraints(student_id,"student_id",param)
    tsql+=add_constraints(stime,"ftime",param,op=">=")
    tsql+=add_constraints(etime,"ftime",param,op="<=")

    tsql += " group by jiebie,course_name,student_id "

    cur = self.conn.cursor();
    if len(param)>0:
      cur.execute(tsql,param);
    else:
      cur.execute(tsql);

    ret = None;
    ret = cur.fetchall();
    cur.close();
    return ret;
  def get_all_attendance(self,student_id=None,jiebie=None,stime=None,etime=None,course_name=None):

    tsql = "select "
    for t in self.table_field["attendance"]:
      tsql += t+","
    tsql += " max(insert_time) from attendance where 1=1 "
    param = [];
    tsql+=add_constraints(jiebie,"jiebie",param)
    tsql+=add_constraints(student_id,"student_id",param)
    tsql+=add_constraints(course_name,"course_name",param)
    tsql+=add_constraints(stime,"insert_time",param,op=">=")
    tsql+=add_constraints(etime,"insert_time",param,op="<=")

    tsql += " group by jiebie,course_name,student_id order by jiebie,course_name,student_id "

    cur = self.conn.cursor();
    if len(param)>0:
      cur.execute(tsql,param);
    else:
      cur.execute(tsql);

    ret = None;
    ret = cur.fetchall();
    cur.close();
    return ret;
  def get_jiebie_department(self,student_id=None,jiebie=None,stime=None,etime=None,course_name=None):

    tsql = "select "
    for t in self.table_field["attendance"]:
      tsql += t+","
    tsql += " max(insert_time) from attendance where 1=1 "
    param = [];
    tsql+=add_constraints(jiebie,"jiebie",param)
    tsql+=add_constraints(student_id,"student_id",param)
    tsql+=add_constraints(course_name,"course_name",param)
    tsql+=add_constraints(stime,"gl_time",param,op=">=")
    tsql+=add_constraints(etime,"gl_time",param,op="<=")

    tsql += " group by jiebie,course_name,student_id order by jiebie,course_name,student_id "

    cur = self.conn.cursor();
    if len(param)>0:
      cur.execute(tsql,param);
    else:
      cur.execute(tsql);

    ret = None;
    ret = cur.fetchall();
    cur.close();
    return ret;
  def add_constraints(self,field,fname,param=[],op="=",co=" and "):
    str ='';
    if field != None:
      str = co + fname + " " + op +" ? ";
      param.append(field);
    return str;
  def add_update_set_str(self,field,fname,param=[],op="=",co=","):
    str ='';
    if field != None:
      str = fname  + op +"?"+co;
      param.append(field);
    return str;
  def get_student_jiebie(self,student_id):
    tsql = "select distinct jiebie from student where student_id=? order by jiebie";
    cur = self.conn.cursor();
    cur.execute(tsql,[student_id]);
    ret = cur.fetchall();
    cur.close();
    return ret;
  def get_student_in_class(self,class_room):
    tsql = "select distinct student_id from student where class_room=? ";
    cur = self.conn.cursor();
    cur.execute(tsql,[class_room]);
    ret = cur.fetchall();
    cur.close();
    return ret;
  def get_student_latest(self,student_id,jiebie,class_room):
    tsql = "select student_id,nick_name,jiebie," \
           " class_room,app_user,default_semester,status,remarks,max(insert_time) from student where student_id=? " \
           "and jiebie=? and class_room=? ";
    cur = self.conn.cursor();
    cur.execute(tsql,[student_id,jiebie,class_room]);
    ret = cur.fetchall();
    cur.close();
    return ret;
  def get_student(self,jiebie=None,stime=None,etime=None,class_room=None,student_id=None,major=None,
          department=None,app_user=None,status=None,tablename="student",op="max"):
    # tsql="select student_id,real_name,jiebie,group_name,location," \
    #      " insert_time from student ;";
    tsql="select ";
    for field in self.table_field[tablename]:
      tsql += field+",";
    tsql += op+"(insert_time) from " + tablename +" where 1=1 ";

    param =[]
    tsql += self.add_constraints(jiebie,"jiebie",param)
    tsql += self.add_constraints(class_room,"class_room",param)
    tsql += self.add_constraints(student_id,"student_id",param)
    tsql += self.add_constraints(app_user,"app_user",param)
    tsql += self.add_constraints(status,"status",param)
    tsql += self.add_constraints(stime,"insert_time",param,op=">=")
    tsql += self.add_constraints(etime,"insert_time",param,op="<=")

    if op=="max":
      tsql += " group by jiebie,student_id" \
            " order by jiebie,class_room,student_id "

    cur = self.conn.cursor();
    if len(param)==0:
      cur.execute(tsql);
    else:
      cur.execute(tsql,param);
    ret = None;
    ret = cur.fetchall();
    cur.close();
    return ret;
  def get_student_status(self,jiebie=None,stime=None,etime=None,class_room=None,student_id=None,major=None,
          department=None,app_user=None,status=None,tablename="student",op="max"):
    # tsql="select student_id,real_name,jiebie,group_name,location," \
    #      " insert_time from student ;";
    tsql="select ";
    for field in self.table_field[tablename]:
      tsql += field+",";
    tsql += op+"(insert_time) from " + tablename +" where 1=1 ";

    param =[]
    tsql += self.add_constraints(jiebie,"jiebie",param)
    tsql += self.add_constraints(class_room,"class_room",param)
    tsql += self.add_constraints(student_id,"student_id",param)
    tsql += self.add_constraints(app_user,"app_user",param)
    tsql += self.add_constraints(status,"status",param)
    tsql += self.add_constraints(stime,"insert_time",param,op=">=")
    tsql += self.add_constraints(etime,"insert_time",param,op="<=")

    tsql += " group by jiebie,student_id" \
            " order by jiebie,class_room,student_id "

    cur = self.conn.cursor();
    if len(param)==0:
      cur.execute(tsql);
    else:
      cur.execute(tsql,param);
    ret = None;
    ret = cur.fetchall();
    cur.close();
    return ret;
  def get_student_min(self,op="min"):
    # tsql="select student_id,real_name,jiebie,group_name,location," \
    #      " insert_time from student ;";
    tsql="select ";
    for field in self.table_field["student"]:
      tsql += "st."+field+",";

    # tsql+="select * from ( select student_id,jiebie,min(insert_time) as ts from student group by jiebie,student_id ) as x inner join student as st on x.student_id=st.student_id and x.jiebie = st.jiebie and x.ts=st.insert_time '"

    tsql = tsql[:-1] + " from ( select student_id,jiebie,"+op+"(insert_time) " \
          " as ts from student group by jiebie,student_id ) " \
          " as x inner join student as st on x.student_id=st.student_id " \
          " and x.jiebie = st.jiebie and x.ts=st.insert_time "

    cur = self.conn.cursor();
    cur.execute(tsql);
    ret = None;
    ret = cur.fetchall();
    cur.close();
    return ret;
  def get_attendence_of_student(self,jiebie=None,class_room=None,course_name=None):
    # tsql = "select s.student_id,s.jiebie,at.course_name,s.class_room,at.report," \
    #        " at.attend_ot,at.leave_ot,at.remarks,at.insert_time,s.status," \
    #        " s.nick_name,max(s.insert_time) " \
    #        " from student as s " \
    #        " left join attendance as at  " \
    #        " on s.student_id=at.student_id and s.jiebie=at.jiebie and s.class_room=at.class_room " ;

    #get all unique students in this jiebie and this class_room
    sdt = self.get_student(jiebie=jiebie,class_room=class_room);

    if course_name==None or jiebie==None or class_room==None: # this means we only display student list , no course information should exist
      ret = []
      for row in sdt:
        ret.append(
          [row[0],row[2],None,row[3],None,None,None,None,None,row[6],row[1]]
        )
      return ret;
    else:#we need display courses' information
      tsql="select student_id,jiebie,course_name,class_room,report,attend_ot,leave_ot,remarks,max(insert_time)" \
           " from attendance where student_id=? and jiebie=? and class_room=? and course_name=? " \
           " group by student_id,jiebie,class_room order by student_id "

      ret_list=[]
      for row in sdt:
        param=[row[0],row[2],row[3],course_name];
        cur = self.conn.cursor();
        cur.execute(tsql,param);
        ret = cur.fetchall();
        if len(ret)==0:
          ret_list.append([row[0],row[2],None,row[3],None,None,None,None,None,row[6],row[1]])
        else:
          for arow in ret:
            t = list(arow);
            t.append(row[6])
            t.append(row[1])
            ret_list.append(t)
        cur.close();
      return ret_list;
  def update_attendence(self,tablename,param,
                        course_name=None,report=None,attend_ot=None,
                        leave_ot=None,remarks=None,insert_time=None):

    #update
    #INSERT INTO table (id, name, age) VALUES (1, 'A', 19) ON DUPLICATE KEY UPDATE id = id + 1;
    #insert or replace into  will remove, yet up statement will just update

    if param[-1]==u"" or param[-1]==None or param[-1]==0 :
      param[-1]= int(time.time())

    tsql="insert into "+tablename+"(";
    f = "";
    for field in self.table_field[tablename]:
      tsql += field+',';
      f += "?,";
    tsql = tsql[:-1]+") "+"values(" + f[:-1] + ") ";

    try:
      cur = self.conn.cursor();
      if len(param)==0:
        cur.execute(tsql);
      else:
        cur.execute(tsql,param);
      self.conn.commit();
    except:
      # mysql support ( insert into tables(xx) values(xx) on duplicate key update set x=a), but sqlite didn't
      tparam=[];
      tsql = "update " + tablename + " set ";
      tsql+=self.add_update_set_str(report,"report",tparam);
      tsql+=self.add_update_set_str(attend_ot,"attend_ot",tparam);
      tsql+=self.add_update_set_str(leave_ot,"leave_ot",tparam);
      tsql+=self.add_update_set_str(remarks,"remarks",tparam);
      tsql+=self.add_update_set_str(course_name,"course_name",tparam);
      tsql+=self.add_update_set_str(insert_time,"insert_time",tparam);
      tsql=tsql[:-1] + \
           " where student_id=? and jiebie=? and course_name=? and class_room=? and  insert_time=?  "

      tparam.extend([param[0],param[1],param[2],param[3],param[8]])
      cur = self.conn.cursor();
      if len(tparam)==0:
        cur.execute(tsql);
      else:
        cur.execute(tsql,tparam);
      self.conn.commit();
    return;
  def insert_student_status(self,para,remarks="",remarks_student_id=""):

    tsql="replace into student(student_id,real_name,nick_name," \
         "major,jiebie,department,class_room,app_user,default_semester,rolltime,status," \
         "remarks,remarks_student_id,insert_time)" \
         " values(?,?,?,?,?,?,?,?,?,?)  "
    param = [student_id,jiebie,status,remarks,remarks_student_id,int(time.time())];

    cur = self.conn.cursor();
    cur.execute(tsql,param);
    self.conn.commit();
    return;
  # table_field["groups"] = ["major","jiebie","department","sub_department","class_room"]
  def get_major(self):
    tsql = "select distinct major,jiebie from groups order by major,jiebie";
    cur = self.conn.cursor();

    cur.execute(tsql);
    ret = cur.fetchall();
    cur.close();
    return ret;
  # table_field["groups"] = ["major","jiebie","department","sub_department","class_room"]
  def get_department_jiebie(self):
    tsql = "select distinct department,jiebie from groups order by department,jiebie";
    cur = self.conn.cursor();
    cur.execute(tsql);
    ret = cur.fetchall();
    cur.close();
    return ret;
  # table_field["groups"] = ["major","jiebie","department","sub_department","class_room"]
  def get_sub_department_jiebie(self):
    tsql = "select distinct sub_department,jiebie from groups order by sub_department,jiebie";
    cur = self.conn.cursor();
    cur.execute(tsql);
    ret = cur.fetchall();
    cur.close();
    return ret;
  # table_field["groups"] = ["major","jiebie","department","sub_department","class_room"]
  def get_class_room_jiebie(self):
    tsql = "select distinct class_room,jiebie from groups order by class_room,jiebie";
    cur = self.conn.cursor();
    cur.execute(tsql);
    ret = cur.fetchall();
    cur.close();
    return ret;
  # table_field["groups"] = ["major","jiebie","department","sub_department","class_room"]
  def get_jiebie(self,major=None):
    tsql = "select distinct jiebie from groups where 1=1 ";

    param = [];
    tsql += self.add_constraints(major,"major",param);

    cur = self.conn.cursor();
    if len(param)==0:
      cur.execute(tsql);
    else:
      cur.execute(tsql,param);
    ret = None;
    ret = cur.fetchall();
    cur.close();
    return ret;
  # get class_room information
  def get_class_room(self,jiebie=None):
    tsql = " select distinct class_room from groups where 1=1 "
    param = [];
    tsql += self.add_constraints(jiebie,"jiebie",param);

    cur = self.conn.cursor();
    if len(param)==0:
      cur.execute(tsql);
    else:
      cur.execute(tsql,param);
    ret = None;
    ret = cur.fetchall();
    cur.close();
    return ret;
  def get_useful_url(self):
    tsql = "select distinct uname,uurl from u_url"
    cur = self.conn.cursor();
    cur.execute(tsql);

    ret = None;
    ret = cur.fetchall();
    cur.close();
    return ret;
  def delete_url(self,uname):
    tsql = "delete from u_url where uname=?"
    param =[uname]
    cur = self.conn.cursor();
    cur.execute(tsql,param);

    self.conn.commit()
    cur.close();
    return ;
  def add_url(self,uname,url):
    tsql = "insert into u_url(uname,uurl) values(?,?)"
    param =[uname,url]
    cur = self.conn.cursor();
    cur.execute(tsql,param);
    self.conn.commit()
    cur.close();
    return ;
  def update_url(self,uname,url):
    tsql = "update u_url set uurl=? where uname=?"
    param =[url,uname]
    cur = self.conn.cursor();
    cur.execute(tsql,param);
    self.conn.commit()
    cur.close();
    return ;
  def change_oldid_to_newid(self,oldid,newid=None):
    tsql = "update records set student_id=? where student_id=?"
    param =[newid,oldid]
    cur = self.conn.cursor();
    cur.execute(tsql,param);
    self.conn.commit()
    cur.close();

    tsql = "update records_history set student_id=? where student_id=?"
    param =[newid,oldid]
    cur = self.conn.cursor();
    cur.execute(tsql,param);
    self.conn.commit()
    cur.close();

    tsql = "update student set student_id=? where student_id=?"
    param =[newid,oldid]
    cur = self.conn.cursor();
    cur.execute(tsql,param);
    self.conn.commit()
    cur.close();
    return ;
  def get_courses_required(self,jiebie=None,type=None,course_name=None,stat_type=None,stime=None,etime=None):
    tsql = "select distinct course_name,type,stat_type from class_require where 1=1 ";

    param = [];
    tsql += self.add_constraints(jiebie,"jiebie",param);
    tsql += self.add_constraints(type,"type",param);
    tsql += self.add_constraints(course_name,"course_name",param);
    tsql += self.add_constraints(stat_type,"stat_type",param);
    tsql += self.add_constraints(stime,"gl_time",param,op=">=");
    tsql += self.add_constraints(etime,"gl_time",param,op="<=");

    tsql += " order by gl_time "

    cur = self.conn.cursor();
    if len(param)==0:
      cur.execute(tsql);
    else:
      cur.execute(tsql,param);
    ret = None;
    ret = cur.fetchall();
    cur.close();
    return ret;
  def get_start_end_time_by_semester(self,jiebie=None,semester=None):
    tsql = "select stime,etime from semester where 1=1 ";
    param = [];
    tsql+=add_constraints(jiebie,"jiebie",param);
    tsql+=add_constraints(semester,"semester",param);

    cur = self.conn.cursor();
    if len(param)>0:
      cur.execute(tsql,param);
    else:
      cur.execute(tsql);
    ret = None;
    ret = cur.fetchall();
    cur.close();
    return ret;
  #semester is changed into a time range[starttime,endtime]
  def get_records(self,jiebie=None,stime=None,etime=None,
                  type=None,stat_type=None,student_id=None):
    tsql = "select cr.gl_time,cr.jiebie,cr.course_name,cr.type,cr.heritage," \
           "cr.faben,cr.group_learn,cr.number,cr.duration,cr.total_duration," \
           "cr.gl_time,r.student_id,r.heritage ,r.faben,r.group_learn," \
           "r.number,r.total_duration,cr.stat_type,r.ftime,30" \
           " from class_require as cr left join records as r " \
           " on r.jiebie = cr.jiebie and r.course_name = cr.course_name ";
    param = [];
    flag = False;

    if student_id!=None:
      tsql += " and (r.student_id is NULL or r.student_id=?) ";
      # tsql += " and  r.student_id=? ";
      # param.append(None);
      param.append(student_id);
      flag=True;

    tsql += " where 1=1 ";

    if jiebie!=None:
      tsql += " and cr.jiebie=? ";
      param.append(jiebie);
      flag=True;

    if stime!=None:
      tsql += " and cr.gl_time >= ? "
      param.append(stime);
      flag=True;

    if etime!=None:
      tsql += " and cr.gl_time <= ? "
      param.append(etime);
      flag=True;

    if type !=None:
      tsql+=" and cr.type= ?";
      param.append(type);
      flag=True;

    if stat_type !=None:
      tsql+=" and cr.stat_type= ? ";
      param.append(stat_type);
      flag=True;

    tsql += " order by cr.gl_time,cr.jiebie,cr.type,cr.course_name,r.student_id desc";

    cur = self.conn.cursor();
    if flag==True:
      cur.execute(tsql,param);
    else:
      cur.execute(tsql);
    ret = None;
    ret = cur.fetchall();
    cur.close();
    x = [];
    for i in ret:
      x.append(list(i));
    return x;
  #semester is changed into a time range[starttime,endtime]
  def get_sole_records(self,jiebie=None,stime=None,etime=None,
                  type=None,stat_type=None,student_id=None,course_name=None,con=" "):
    tsql = "select student_id,jiebie,course_name,type,stat_type," \
           "heritage,faben,group_learn,number,total_duration," \
           "ftime from records "
    param = [];
    flag = False;
    tsql += " where 1=1 ";

    tsql +=add_constraints(student_id,"student_id",param,);
    tsql +=add_constraints(jiebie,"jiebie",param,);
    tsql +=add_constraints(type,"type",param,);
    tsql +=add_constraints(course_name,"course_name",param,);
    tsql +=add_constraints(stat_type,"stat_type",param,);
    tsql +=add_constraints(stime,"stime",param,op=">=",co=" and ");
    tsql +=add_constraints(stime,"stime",param,op=">=",co=" and ");

    tsql += " order by ftime desc " + con;

    cur = self.conn.cursor();
    if len(param)>0:
      cur.execute(tsql,param);
    else:
      cur.execute(tsql);
    ret = None;
    ret = cur.fetchall();
    cur.close();
    x = [];
    for i in ret:
      x.append(list(i));
    return x;
  def get_history_records(self,jiebie=None,type=None,stat_type=None,uname=None):
    tsql = "select student_id,jiebie,course_name,type,stat_type,heritage," \
           " faben,group_learn,number,duration,ftime,record_time,undo " \
           " from records_history where 1=1 ";
    param = [];
    flag = False;

    if jiebie!=None:
      tsql += " and jiebie=? ";
      param.append(jiebie);
      flag=True;

    if type !=None:
      tsql+=" and type= ?";
      param.append(type);
      flag=True;

    if stat_type !=None:
      tsql+=" and stat_type= ?";
      param.append(stat_type);
      flag=True;

    if uname!=None:
      tsql += " and student_id=? ";
      param.append(uname);
      flag=True;

    tsql += " order by undo asc,ftime desc ";

    cur = self.conn.cursor();
    if flag==True:
      cur.execute(tsql,param);
    else:
      cur.execute(tsql);
    ret = None;
    ret = cur.fetchall();
    cur.close();
    x = [];
    for i in ret:
      x.append(list(i));
    return x;

