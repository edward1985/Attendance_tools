# -*- coding: utf-8 -*-
__author__ = 'Gongming Yang'
# Created and owned by:Gongming Yang
# Whelcome to use this tool to record attendance

import csv,os
from zbclass_db import *
from yy_kaoqin import *

def mytest(str):
  f = open("debug.txt","a+");
  f.write(str+'\n');
  f.close();

def get_stat_str(all,num):
  if all == 0 and num>0:
    return str(num)+"/ NA"
  elif all==0 and num==0:
    return str(num)+"/ 0%";
  else:
    return str(num)+"/ "+str(int(100.0*num/all))+"%";

class zbclass (object):
  def __init__(self,dbname):
    self.codetype='gbk';

    need_read_csv=False;
    if os.path.isfile(dbname):
      need_read_csv = False;

    self.db = zbc_conn(dbname);

    self.records_exist = False;#didn't retrieve data

    pass;

  def is_val(self,iname,uname):
    if iname.decode(self.codetype).replace(u" ",u"") == uname:
      return True;
    else:
      return False;
  def get_string(self,iname):
    return iname.decode(self.codetype).replace(u" ",u"");

  def get_encode(self,iname):
    #iname.decode('gbk').replace(u" ",u"") == u"智悲双运";
    try:
      if iname.decode('gbk').replace(u" ",u"") == u"智悲":
        self.codetype='gbk';
      else: raise(NameError(""))
    except:
      try:
        if iname.decode('utf8').replace(u" ",u"") == u"智悲":
          self.codetype='utf8';
        else:
          raise(NameError(""));
      except:
        try:
          if iname.decode('gb2312').replace(u" ",u"") == u"智悲":
            self.codetype='gb2312';
          else: raise(NameError(""))
        except:
          try:
            if iname.decode('big5').replace(u" ",u"") == u"智悲":
              self.codetype='big5';#gbk
            else: raise(NameError(""))
          except:
            print "encode error";
            return False;
    return True;

  def is_table_empty(self,name):
    if name=='' or name==u"":
      return True;
    else:
      return False;


  #---Functions for get something from database
  def get_current_user(self):
    ctime=time.time();
    s = self.db.get_student(app_user=u"是");
    # print "----read csv takes",time.time()-ctime;ctime=time.time();
    if len(s)==0:
      return False;
    self.student_id=s[0][0]
    self.nick_name = s[0][1];
    self.jiebie = s[0][2];
    self.class_room= s[0][3];
    self.app_user = s[0][4];
    self.default_semester = s[0][5];
    self.status = s[0][6];
    self.remarks = s[0][7];
    self.remarks_student_id = s[0][8];
    self.insert_time = s[0][9];

    self.jiebie_semester = self.db.get_semester_list();

    self.get_time_by_semester();
    return True;

  def set_current_user(self,student_id=None):
    if student_id==None:
      return False;
    # s = self.db.get_student(app_user=u"是");
    # print "----read csv takes",time.time()-ctime;ctime=time.time();
    s=[];
    if student_id in self.dict_all_student:
      s = self.dict_all_student[student_id];
    if len(s)==0:
      return False;

    self.student_id=s[0][0]
    self.nick_name = s[0][1];
    self.jiebie = s[0][2];
    self.class_room= s[0][3];
    self.app_user = s[0][4];
    self.default_semester = s[0][5];
    self.status = s[0][6];
    self.remarks = s[0][7];
    self.remarks_student_id = s[0][8];
    self.insert_time = s[0][9];

    #jiebie don't need to be updated
    # self.jiebie_semester = self.db.get_semester_list();

    self.get_time_by_semester();

    #write default use into database
    self.db.set_default_user(self.student_id);

    return True;


  def get_time_by_semester(self):
    time_r = self.db.get_start_end_time_by_semester(jiebie=self.jiebie,semester=self.default_semester);
    if len(time_r)>0:
      self.stime = int(time_r[0][0]);
      self.etime = int(time_r[0][1]);
    else:
      self.stime = None;
      self.etime = None;
    return;

  #---Functions for Read CSV
  def change_coding_of_csv(self,fname,ecd="utf8"):
    f=open(fname,"rb");
    reader = csv.reader(f);
    frow = reader.next();#first row
    self.get_encode(frow[0]);
    if ecd not in ['utf8','gbk','gb2312','big5'] or self.codetype==ecd:
      f.close();
      return;

    rows=[[self.get_string(r) for r in row] for row in reader]
    rows.insert(0,[self.get_string(r) for r in frow]);
    f.close();

    f = open(fname,"wb");
    w=csv.writer(f,lineterminator='\n');
    for r in rows:
      w.writerow([get_val_unicode(t,ecd) for t in r ]);
    f.close();

  def read_student_from_csv(self,fname="data/student_info.csv"):
    f=open(fname,"rb");
    reader = csv.reader(f);
    row = reader.next();
    self.get_encode(row[0]);
    row = reader.next(); #escape the headerline
    s=[]
    s = [[self.get_string(r) for r in row] for row in reader];
    f.close();

    if len(s) == 0:
      return None;

    for i in range(len(s)):
      # add rolltime,status,remarks,remarks'student_id,insert_time
      s[i].extend([None,None,None,int(time.time()),]);
    self.db.replace_into_many(u"student",s);

  def read_class_require_from_csv(self,fname="data/class_info.csv"):
    f=open(fname,"rb");
    # reader = csv.DictReader(f);
    reader = csv.reader(f);
    row = reader.next();
    self.get_encode(row[0]);
    row = reader.next();
    s=[]
    ctime = time.time();
    # for row in reader:
    #   t.append(row);
    s = [[self.get_string(row[0]),self.get_string(row[1]),self.get_string(row[2]),self.get_string(row[3]),int(row[4]),
          int(row[5]),int(row[6]),int(row[7]),int(row[8]),int(row[9]),time_str_int(row[10])] for row in reader];
    f.close();
    if s==None:
      return None;
    self.db.replace_into_many(u"class_require",s);

  def read_url_from_csv(self,fname="data/url_info.csv"):
    f=open(fname,"rb");
    # reader = csv.DictReader(f);
    reader = csv.reader(f);
    row = reader.next();
    self.get_encode(row[0]);
    row = reader.next();
    s=[]
    ctime = time.time();
    # for row in reader:
    #   t.append(row);
    s = [[self.get_string(row[0]),self.get_string(row[1]),self.get_string(row[1])] for row in reader];
    f.close();
    if s==None:
      return None;
    self.db.replace_into_many(u"u_url",s);

  def read_semester_from_csv(self,fname="data/semester_info.csv"):
    f=open(fname,"rb");
    # reader = csv.DictReader(f);
    reader = csv.reader(f);
    row = reader.next();
    self.get_encode(row[0]);
    row = reader.next();
    s = [[self.get_string(row[0]),self.get_string(row[1]),time_str_int(row[2]),time_str_int(row[3])] for row in reader];
    f.close();
    if len(s)==0:
      return None;
    self.db.replace_into_many(u"semester",s);

  def read_groups_from_csv(self,fname="data/groups_info.csv"):
    f=open(fname,"rb");
    # reader = csv.DictReader(f);
    reader = csv.reader(f);
    row = reader.next();
    self.get_encode(row[0]);
    row = reader.next();
    s = [[self.get_string(row[0]),self.get_string(row[1]),self.get_string(row[2]),self.get_string(row[3]),self.get_string(row[4]),] for row in reader];
    f.close();
    if s==None:
      return None;
    self.db.replace_into_many(u"groups",s);

  def read_student_list_from_csv(self,fname="data/groups_info.csv"):
    f=open(fname,"rb");
    reader = csv.reader(f);
    row = reader.next();
    self.get_encode(row[0]);
    row = reader.next();
    s = [[self.get_string(row[0]),self.get_string(row[1]),\
          self.get_string(row[2]),self.get_string(row[3]),self.get_string(row[4]),] for row in reader];
    f.close();
    if s==None:
      return None;
    self.db.replace_into_many(u"groups",s);

  def select_file(self,title=u"csv file",file_type="*.csv",default_name="student_info.csv"):
    of  = wx.FileDialog(None,title,u"南无阿弥陀佛",default_name,file_type,wx.FD_OPEN | wx.FD_FILE_MUST_EXIST);
    if of.ShowModal() == wx.ID_CANCEL:
      print "cancel"
      # of.Destroy();
      return None;
    # of.Destroy();
    return of.GetPath();

  def load_new_student(self):
    fname = self.select_file(u"南无阿弥陀佛,选择更新的学员表","*.csv",default_name="./student.csv");
    f=open(fname,"rb");
    # reader = csv.DictReader(f);
    reader = csv.reader(f);
    row = reader.next();
    self.get_encode(row[0]);
    row = reader.next();
    s = [[
            self.get_string(row[3]),
            self.get_string(row[0]),
            self.get_string(row[1]),
            self.get_string(row[2]),
            self.get_string(row[4]),
            int(time.time())] for row in reader];
    f.close();
    if len(s)==0:
      return None;
    self.db.replace_into_many(u"u_student",s);

  #001 get user information.
  def get_current_records(self,jiebie=None,stime=None,etime=None,type=None,stat_type=None,student_id=None):
    # if self.records_exist==False:
    self.records = self.db.get_records(jiebie=jiebie,stime=stime,etime=etime,type=type,stat_type=stat_type,student_id=student_id);
    return self.records;
    # self.records_exist = True;
