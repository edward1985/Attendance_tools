# -*- coding: utf-8 -*-
__author__ = 'Gongming Yang'
# Created and owned by:Gongming Yang
# Whelcome to use this tool to record attendance

import threading
import ctypes
import pythoncom
import pyHook
import win32clipboard
import pyautogui
import win32api, win32con, win32gui
import time
import cv2,numpy
from PIL import ImageGrab
'''
Chinese character: 35 for 2, 17 for one
English: 7 for one
'''
Save_code="utf8"
# user32 = ctypes.windll.user32
# kernel32 = ctypes.windll.kernel32
# psapi = ctypes.windll.psapi
# current_window = None

import wx;
def wx_info(parent, message, caption = 'Insert program title'):
  dlg = wx.MessageDialog(parent, message, caption, wx.OK | wx.ICON_INFORMATION)
  dlg.ShowModal()
  dlg.Destroy()

class hook_thread(object):
  def __init__(self,sq):
    dt = win32gui.GetDesktopWindow()
    self.ss = win32gui.GetWindowRect(dt);
    # df = win32gui.GetForegroundWindow()
    # self.sf = win32gui.GetWindowRect(df);

    # self.img_dot = cv2.imread('dot_no_voice.bmp',0);
    # self.h = int(self.img_dot.shape[0]/2);
    self.img_dot = None;
    self.h = 22;

    self.sq = sq;
    self.nlist = {}
    self.count = 0;
    self.N=9;
    #the default value is in default can be used in my laptop
    # self.mlist=[[45, 524], [47, 544], [95, 535], [195, 662], [851, 352], [78, 534], [85, 826], [44, 1002]];
    self.mlist = None;
    self.start_record=False;
    self.start_auto_mouse = False;
    self.start_moc_input = False;
    self.image_list = [];
    self.image_pos=[0,0,0,0];

    self.start_jietu=False;

    self.start_hook();
    th2 = threading.Thread(target=self.th_process,args=(),name="capture_yy002");
    th2.start();

  #start thread
  def start_hook(self):
    self.hm =  pyHook.HookManager()

    self.hm.MouseAll = self.get_mouse_position
    self.hm.HookMouse()

    self.hm.KeyDown = self.get_key_board
    # self.hm.KeyUp = self.get_key_board
    self.hm.HookKeyboard()
    # pythoncom.PumpMessages()

  def th_process(self):
    while True:
      if self.start_auto_mouse == True:
        # try:
        self.start_capture();
        # except:
        #   print "exception --- occurs 09"
        #   pass;
        self.record_import();
        self.start_auto_mouse = False;
      if self.start_jietu == True:
        self.jietu();
        self.start_jietu=False;
      if self.start_moc_input == True:
        # self.hm.HookMouse();
        pass
      time.sleep(0.3);

  #Functions for inner used
  def click(self,x,y):
      win32api.SetCursorPos((x,y))
      win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
      win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

  def right_click(self,x,y):
      win32api.SetCursorPos((x,y))
      win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,x,y,0,0)
      win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,x,y,0,0)

  def double_click(self,x,y):
      win32api.SetCursorPos((x,y))
      win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
      win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

      win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
      win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
  def wheel_down(self,x,y,down=-1):
      win32api.SetCursorPos((x,y))
      win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL,x,y,down,0)

  def move(self,x,y,stime=0.01):
      win32api.mouse_event(win32con.MOUSEEVENTF_ABSOLUTE|win32con.MOUSEEVENTF_MOVE,x,y)
      time.sleep(stime)
  def copy_get_highlight_value(self,):
    pyautogui.hotkey('ctrl','c');
    data = '';
    try:
      #win32clipboard.RegisterClipboardFormat(str(win32con.CF_UNICODETEXT))
      win32clipboard.OpenClipboard()
      data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
      win32clipboard.EmptyClipboard()
      win32clipboard.CloseClipboard()
    except:
      win32clipboard.EmptyClipboard()
      win32clipboard.CloseClipboard()
    return data;
  def get_mouse_position(self,event):
      # called when mouse events are received
      #print type(event.Message); it is int
      # if event.Message in [513,516]:
      #   print event.Position;
      if self.start_moc_input==True and event.Message in [513,516]:
        self.mlist[self.count]=[event.Position[0],event.Position[1]]
        print self.count,"th=(",self.mlist[self.count],")";
        if self.count >= 7:
          self.start_moc_input=False;
          print "we got all required position:",self.mlist;
          wx_info(None,str(self.mlist),u"阿弥陀佛");

          # self.hm.UnhookMouse()
        self.count = self.count + 1;
      return True

  def get_key_board(self,event):
    #left ctr 162,left alt 164,c 67, d 68, q 81,w 87,a 65,s 83, d 68, f 70
    #CTRL+G 7; ctrl+w 23
    if event.Ascii == 7: #ctrl+G
      #screen copy
      fname = self.time_int_into_str()+'.jpg';
      print "screen_copy..."
      # pyautogui.screenshot()
      pyautogui.screenshot(fname);
      # im = pyautogui.screenshot(region=(self.image_pos[0],self.image_pos[1],self.image_pos[2],self.image_pos[3],))
      # self.image_list.append(im);
    #(left)alt+s stop mock mouse; 24 ctrl+x
    elif event.Ascii == 17: #ctrl+q
      #Stop get users
      self.start_auto_mouse = False;
      print "stop auto mouse fetching ..."
    return True

  def find_next_user(self,x,y,xb,yb):
    img = self.getScreen([x,y,xb,yb])[:,:,0];
    # cv2.imwrite(str(time.time())+"test.jpg",img);

    ret = cv2.matchTemplate(img,self.img_dot,cv2.TM_CCOEFF_NORMED);
    threshold=0.8;
    loc = numpy.where(ret >= threshold);
    # r = cv2.minMaxLoc(ret);
    # print r;

    loc = zip(*loc[::-1]);
    if len(loc) <= 0:
      return False,0,0;
    return True,loc[0][0],loc[0][1];

  def jietu(self):

    screenWidth = self.ss[2];
    screenHeight = self.ss[3];
    self.screenHight=screenHeight
    # self.start_auto_mouse = True;

    nlist = self.nlist;
    k = self.mlist;
    x_s0=k[0][0]; y_s0=(k[0][1]);
    x_s1=k[1][0];y_s1=k[1][1];
    lc_offset_x=k[3][0]-k[2][0]
    lc_offset_y=k[3][1]-k[2][1]
    manual_size=k[6][1]-k[5][1]

    nnPos_x=k[4][0]
    nnPos_y=k[4][1]
    move_down_step=k[1][1]-k[0][1];
    bottom_y = int(k[7][1]);
    bottom_x = k[7][0];

    self.image_pos=[x_s0-10,y_s0-move_down_step, x_s0+bottom_x, bottom_y+move_down_step];
    print self.image_pos;

    ctime = time.time();
    move_down_step = self.get_h_step(k[0][0],k[0][1],k[1][0],k[1][1]);
    print time.time()-ctime;
    self.move_down_step = move_down_step;
    #get the screen handle: It looks unnecessary

    self.screen_capture(move_down_step,bottom_y,x_s0,y_s0);

    wx_info(None,u"完成截图",u"阿弥陀佛");

  def start_capture(self,):

    screenWidth = self.ss[2];
    screenHeight = self.ss[3];
    self.screenHight=screenHeight
    self.start_auto_mouse = True;

    nlist = self.nlist;
    k = self.mlist;
    x_s0=k[0][0]; y_s0=(k[0][1]);
    x_s1=k[1][0]; y_s1=k[1][1];
    lc_offset_x=k[3][0]-k[2][0]
    lc_offset_y=k[3][1]-k[2][1]
    manual_size=k[6][1]-k[5][1]

    nnPos_x=k[4][0]
    nnPos_y=k[4][1]
    move_down_step=k[1][1]-k[0][1];
    bottom_y = int(k[7][1]);
    bottom_x = k[7][0];

    y_s0 = min(y_s0,y_s1);

    self.image_pos=[x_s0-10,y_s0-move_down_step, x_s0+bottom_x, bottom_y+move_down_step];
    print self.image_pos;

    ctime = time.time();
    move_down_step = self.get_h_step(k[0][0],k[0][1],k[1][0],k[1][1]);
    print time.time()-ctime;
    self.move_down_step = move_down_step;
    #get the screen handle: It looks unnecessary

    # self.screen_capture(move_down_step,bottom_y,x_s0,y_s0);

    ytop =int( y_s0-move_down_step/2 );
    ybm = bottom_y
    bottom_y=int(bottom_y+move_down_step/2)

    #????
    self.click(1,y_s1)
    self.move(x_s1,y_s1)
    time.sleep(0.1)
    # df = win32gui.GetForegroundWindow()
    # self.sf = win32gui.GetWindowRect(df);

    #get self.h and self.img_dot
    self.h = int(move_down_step/2);
    self.img_dot=self.getScreen([x_s0-int(self.h/1.5),y_s0-int(self.h/2),x_s0+5,y_s0+int(self.h/2)])[:,:,0];

    #start capture:
    idx = 0;
    count = 0;
    manual_offset_pos = lc_offset_y; #start
    mtime = 0.7;
    false_count = 0;
    #screen capture first.
    self.move(x_s0+300,y_s0);
    self.click(x_s0+300,y_s0);

    whflag = True;
    numidx = int(bottom_y - y_s0)/move_down_step;

    cy = y_s0 - self.h;
    cx = x_s0 ;
    my = bottom_y;
    ret = True;

    while self.start_auto_mouse==True:
      print "cx=",cx,'cy=',cy;
      if whflag and (ret==False or self.screenHight - manual_size - cy <self.h ): #scrool up or not
        #reach the end of the screen:
        #judge it is the last time or not;
        self.click(1,y_s0)
        self.move(x_s0+5,y_s0)
        im_bot = self.getScreen([x_s0+10,cy-self.h,x_s0+80,cy+self.h]);
        # wheel up
        rnum = int((cy-y_s0)/self.move_down_step/3);
        for i in range(rnum):
          self.wheel_down(x_s0,y_s0)
          time.sleep(0.2)

        #check move up , move the botom up:
        im_all = self.getScreen([x_s0-int(self.h/1.5)-1,ytop,130+x_s0,bottom_y]);

        res = cv2.matchTemplate(im_all,im_bot,cv2.TM_CCOEFF_NORMED);
        loc = numpy.where(res >= 0.8);

        loc = zip(*loc[::-1]);

        # timg_1 =  ImageGrab.grab(bbox=tuple([x_s0+10,cy-self.h,x_s0+80,cy+self.h]));
        # timg_2 =  ImageGrab.grab(bbox=tuple([x_s0-10,ytop,130+x_s0,bottom_y]));

        if len(loc)<=0:
          whflag = False;
          print "can't find the loc========"
          continue;

        x,y = loc[0];
        print x,y;
        if abs(cy-(y+ytop+self.h))<=self.h:
          whflag = False;
        else:
          cy = ytop +y - 3;

      #Normal situation:
      ret,tx,dy = self.find_next_user(cx-self.h,cy,cx+200,bottom_y);

      if ret==False:
        print "didn't find the next user------"
      else:
        print "found next user:",tx,dy,cy + dy + self.h;

      #print "ret=",ret,cx,cy,self.screenHight - manual_size - cy

      # if it can't move up and no other match, just break.
      if ret ==False and whflag==True:
        time.sleep(0.3);
        continue;
      if ret == False and whflag==False:
        break;

      cy = cy + dy + self.h;
      # print "------",y_s0+offset,"top",screenHeight
      if screenHeight-manual_size - cy < self.h/2:
        cy = cy - self.h/2;

      if screenHeight <= manual_size + cy: #decide the position
        manual_offset_pos = (lc_offset_y - manual_size);
      else:
        manual_offset_pos = lc_offset_y;

      if self.start_auto_mouse ==False:
        break;

      try: #fist time, it may failed
        ret = self.getOneStudent(x_s0,cy,lc_offset_x,manual_offset_pos,nnPos_x,nnPos_y,nlist,mtime);
      except:
        ret = False;

      if self.start_auto_mouse ==False:
        break;
      #Second: first try is failed, if it approx the up and down for the right manual, try opsite.
      if ret==False:# try another time , in case it take too long time for yy to affect
        self.move(x_s0+300,y_s0);
        self.click(x_s0+300,y_s0);
        try:
          #in this case, we don't change the wait time.
          ret = self.getOneStudent(x_s0,cy,lc_offset_x,manual_offset_pos,nnPos_x,nnPos_y,nlist,5);
        except:
          #save the picture
          im_f = self.getScreen([cx-int(self.h/1.5)-1,int(cy-self.move_down_step/2),cx+130,int(cy+self.move_down_step/2)]);
          im_f.imwrite(str(time.strftime('%Y%m%d_%H_%M%S',time.localtime()))+"failed.jpg");
          ret = False;

        if ret==False:
          # if screenHeight-manual_size - cy > self.h:
          #   continue;
          if manual_offset_pos >0:
            manual_offset_pos = (lc_offset_y - manual_size);
          else:
            manual_offset_pos = (lc_offset_y);
          try:
            #in this case, we don't change the wait time.
            ret = self.getOneStudent(x_s0,cy,lc_offset_x,manual_offset_pos,nnPos_x,nnPos_y,nlist,5);
          except:
            #save the picture
            im_f = self.getScreen([cx-int(self.h/1.5)-1,int(cy-self.move_down_step/2),cx+130,int(cy+self.move_down_step/2)]);
            im_f.imwrite(str(time.strftime('%Y%m%d_%H_%M%S',time.localtime()))+"failed.jpg");
            ret = False;

          if ret == False:
            print "cy jump down one user------\n"
            cy += self.h * 2;# move to next user.
            print cy;

      if self.start_auto_mouse ==False:
        break;

    wx_info(None,u"本次考勤结束",u"阿弥陀佛");

  def record_import(self):
    #finish get all student
    #write into files.
    if len(self.nlist)<=0:
      return;
    self.sq.put(self.nlist);
    return;

    #record into database
    ret = [];
    for i in self.nlist:
      t = unicode(self.nlist[i][0]).encode("utf8");
      ret.append([t,i,self.nlist[i][1]]);
    ret.sort();
    fname = "student_list"+time.strftime('%Y_%m_%d_%H%M%S',time.localtime())+".txt";
    f = open(fname,"ab")
    f.write(u"YY昵称;  YY号;  在线时的时间\r\n".encode(Save_code))
    for i in ret:
      str = i[0].decode("utf8") + u";" + unicode(i[1])+";"\
            +unicode(time.strftime('%Y%m%d_%H:%M:%S',time.localtime(i[2])))+u"\r\n";
      f.write(unicode(str).encode(Save_code));
    f.close();
    #clear the nlist
    self.nlist = {};
    print u"继续获取信息已经结束，文件已保存"

  # img = [[[r,g,b],[r,g,b]],[[r,g,b],[r,g,b]]..]
  #img[:,:,0] get red; img[:,:,1] get yellow; img[:,:,1] get  blue
  def getScreen(self,rect=None):
    print "test---,",rect;
    self.move(500,100)
    if rect==None:
      return cv2.cvtColor(numpy.array(ImageGrab.grab().convert('RGB')), cv2.COLOR_RGB2BGR);
    else:
      # ImageGrab.grab(bbox=tuple(rect)).show()
      tt = ImageGrab.grab(bbox=tuple(rect));
      return cv2.cvtColor(numpy.array(tt.convert('RGB')), cv2.COLOR_RGB2BGR);

  def test_bmp_compare(self):
      ctime = time.time();
      #change the screenshot into cv2 image
      # img1 = numpy.array(ImageGrab.grab().convert('RGB'))
      # img1 = cv2.cvtColor(numpy.array(ImageGrab.grab().convert('RGB')), cv2.COLOR_RGB2BGR)[:,:,0];

      img1=cv2.imread('test_green1.png',0);
      template=cv2.imread('dot_no_voice.bmp',0);
      th, tw = template.shape[:2]
      #the new position of bottom one

      ret = cv2.matchTemplate(img1,template,cv2.TM_CCOEFF_NORMED);
      y,x = numpy.unravel_index(ret.argmax(), ret.shape);

      min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(ret);
      #if threshold =0.8, we match for the user who speaking
      threshold = 0.8
      loc = numpy.where(ret >= threshold)
      for pt in zip(*loc[::-1]):
        cv2.rectangle(img1, pt, (pt[0] + tw, pt[1] + th), 0, 1)
      cv2.imwrite('test1.jpg',img1)

      print time.time()-ctime;

      print "----"

  #return : status,x,y
  def get_position(self,img_s,img_big,threshold=0.8):
    ret = cv2.matchTemplate(img_big,img_s,cv2.TM_CCOEFF_NORMED);
    # y,x = numpy.unravel_index(ret.argmax(), ret.shape);
    loc = numpy.where(ret >= threshold)

    loc = zip(*loc[::-1]);
    if len(loc) <= 0:
      return False,0,0;
    return True,loc[0][0],loc[0][1];


  def screen_capture(self,move_down_step,bottom_y,x_s0,y_s0):
    k = self.mlist;
    h = k[1][1]-k[0][1];
    km = k[7][1];
    num_idx = int(bottom_y - y_s0)/move_down_step;
    print "bottom_y",bottom_y,"y_s",y_s0,"stp",move_down_step;

    km =  int(y_s0 + num_idx*move_down_step);

    self.click(x_s0+300,km)
    self.move(x_s0+300,km);

    ytop =int( y_s0-move_down_step/2 );
    ym=int(km+move_down_step/2)

    fname = u"考勤截图"+unicode(time.strftime('%Y%m%d_%H_%M%S',time.localtime()));

    im_list=[];
    trect = [x_s0-10,ytop,300+x_s0,ym];

    tdown = 0;
    idx=0
    while True:
      im_list.append(
            ImageGrab.grab(bbox=tuple(trect))
      )
      f = fname+unicode("_"+str(idx)+".png");idx+=1;
      pyautogui.screenshot(f);
      #get bottom image
      imcv1 = self.getScreen([x_s0+10, ym-move_down_step, x_s0+130, ym])
      # im1 = ImageGrab.grab(bbox=(x_s0+10, ym-move_down_step, x_s0+130, ym));
      # im1.save("t1.bmp")
      #get the first image
      imcv3 = self.getScreen([x_s0+10,y_s0,x_s0+130,y_s0+int(move_down_step/2)])
      # im2 = ImageGrab.grab(bbox=(x_s0+10,y_s0,x_s0+130,y_s0+int(move_down_step/2)));
      # im2.save("t3.bmp");
      self.move(x_s0,km);
      self.click(x_s0,y_s0)

      # we think it will row up 3 idx
      whtime = int(num_idx/3);
      for i in range(whtime):
        self.wheel_down(x_s0,ym)
        tdown+=1;
        time.sleep(0.1)
      self.move(x_s0+300,km);
      self.click(x_s0+300,km);

      imcv2 = self.getScreen([x_s0-10,ytop,300+x_s0,self.screenHight])
      # im2 = ImageGrab.grab(bbox=(x_s0-10,ytop,300+x_s0,self.screenHight));
      # im2.save("t2.bmp");
      # imcv1=cv2.imread('t1.bmp',0);
      # imcv2=cv2.imread('t2.bmp',0);
      # imcv3=cv2.imread('t3.bmp',0);

      #the new position of bottom one


      tt = True;
      tt,x,y = self.get_position(imcv1,imcv2);
      # ret = cv2.matchTemplate(imcv1,imcv2,cv2.TM_CCOEFF);
      # y,x = numpy.unravel_index(ret.argmax(), ret.shape);

      #the new position of first one
      tt,xf,yf = self.get_position(imcv3,imcv2);
      # ret = cv2.matchTemplate(imcv3,imcv2,cv2.TM_CCOEFF);
      # yf,xf = numpy.unravel_index(ret.argmax(), ret.shape);

      trect = [x_s0-10,ytop+y,300+x_s0,ym];
      print trect;
      # if bottom not move , or top not move.
      if abs(y+ytop-(ym-move_down_step))<10 or abs(yf+ytop-(y_s0))<10:
        break;

    #merge the screen copy
    tym = 0;
    for im in im_list:
      tym += im.size[1];
    from PIL import Image
    cim = Image.new("RGB",(310,tym));

    s_y=0;
    for im in im_list:
      if im == None:
        continue;
      cim.paste(im,(0,s_y))
      s_y += im.size[1];

    print fname;
    cim.save(fname+unicode(".png"));

    #move back
    self.move(x_s0,y_s0)
    time.sleep(0.1)
    self.click(x_s0,y_s0+30)
    time.sleep(0.1)
    for i in range(int(1.2*tdown)):
        self.wheel_down(x_s0,ym,1);#move up
        time.sleep(0.1)
    print "---"

  def get_im(self,src_im,rect=(0,0,100,100)):
      return cv2.getRectSubPix(src_im,(rect[2]-rect[0],rect[3]-rect[1]),((rect[2]+rect[0])/2,(rect[3]+rect[1])/2));

  def get_h_step(self,x0,y0,x1,y1):
    h = y1 - y0;
    self.move(x0+300,y1+h+h);
    im1 = ImageGrab.grab(bbox=(x0-10,y0-int(h/2),x0+10,y0+int(h/2)))
    im2 = ImageGrab.grab(bbox=(x0-10,y0,x0+10,y0+3*h))
    im1.save("t1.bmp");im2.save("t2.bmp")
    # pyautogui.screenshot('t1.bmp',(x0-10,y0-int(h/2),x0+10,y0+int(h/2)));
    # pyautogui.screenshot('t2.bmp',(x1-10,y1-int(h/2),x1+10,y1+3*h);
    im1=cv2.imread('t1.bmp',0);
    imb=cv2.imread('t2.bmp',0);
    ret = cv2.matchTemplate(im1,imb,cv2.TM_CCOEFF);
    y,x = numpy.unravel_index(ret.argmax(), ret.shape);

    # print y,x;
    tmp_im=self.get_im(imb,(x,y,20+x,20+y))
    cv2.imwrite("test_t1_t2.bmp",tmp_im);
    print "---"

    return y+h/2;



  def getOneStudent(self,x_s0,y_s0,lcOffset_x,lcOffset_y,nnPos_x,nnPos_y,nlist,msleepTime=0.3):
    # print x_s0,y_s0,lcOffset_x,lcOffset_y,nnPos_x,nnPos_y
    #move mouse to the student on left
    self.move(x_s0,y_s0)
    self.right_click(x_s0,y_s0)
    time.sleep(msleepTime)

    #click personal information
    self.move(x_s0+lcOffset_x, y_s0+lcOffset_y)
    self.click(x_s0+lcOffset_x, y_s0+lcOffset_y)
    time.sleep(0.7)

    #click nick name upside
    self.move(nnPos_x,nnPos_y)
    self.double_click(nnPos_x,nnPos_y)
    # time.sleep(1)
    #get nick_name
    nick = self.copy_get_highlight_value();
    if len(nick)>0:
      # print "nick={",nick,"}";
      nick=nick.split('\x00')[0];
      print "nick name=",nick;
    else:
      #sleep additional 3 seconds
      tcu = 0
      while tcu<25 and self.start_auto_mouse == True:
        time.sleep(0.2);
        self.click(nnPos_x,nnPos_y)
        self.double_click(nnPos_x,nnPos_y)
        nick = self.copy_get_highlight_value();
        if len(nick)>=2:
          nick=nick.split('\x00')[0];
          break;
        tcu += 1;
      print tcu;
      if tcu==25 or self.start_auto_mouse == False:
        # print "one student not records";
        return False;

    # get the YY No. we just guess the length. so we try more times.
    idx = 1;
    N=13
    data = '';
    while idx<N and self.start_auto_mouse == True:
      toffset = 30*idx;
      self.move(nnPos_x+toffset,nnPos_y,0.001)
      self.click(nnPos_x+toffset,nnPos_y) # clear the selection first.

      # time.sleep(1)

      self.double_click(nnPos_x+toffset,nnPos_y)
      try:
        data = self.copy_get_highlight_value();
        data = data.replace(u'(','').replace(u')','').replace('\x00','');
        # data = data.split('\x00')[0];
        # time.sleep(0.03)
        if len(data)>=6:
          data = int(data);
          break;
      except:
        idx += 1;
        print "data isn't number"
        continue;
      idx +=1;

    #move out of the name list zone
    pyautogui.hotkey('esc');
    self.move(x_s0+200,y_s0)
    # time.sleep(1)
    # print int(data)
    if idx>=N:
      return False;
    else:
      yyNo = data;
      nlist[yyNo]=[nick,time.time()]
      return True;
  def time_int_into_str(self,ttime=None):
    return time.strftime('%Y%m%d_%H%M%S',time.localtime(ttime))

if __name__=="__main__":
  t = hook_thread(None);
  # t.test_bmp_compare()


'''
  def unused_get_key_board(self,event):
    #left ctr 162,left alt 164,c 67, d 68, q 81,w 87,a 65,s 83, d 68, f 70
    if event.KeyID in [164,162,65,83,68,67,10]:
      self.klist[event.KeyID] = event.Time;

    #(left)alt+c screen copy
    if event.KeyID in [164,162,67]:
      # print event.KeyID,"--",event.Time;
      #been push in 500mili seconds
      if max(max(self.klist[67],self.klist[164]),self.klist[162])\
          -min(min(self.klist[67],self.klist[164]),self.klist[162]) < 900:
        #screen copy
        fname = self.time_int_into_str()+'.png';
        print "screen_copy..."
        pyautogui.screenshot(fname);
        #if success, then clear the status of self.klist
        self.klist[164] =0;
        self.klist[67] =100000;

    #(left)alt+a start auto mouse
    if event.KeyID in [164,162,65]:
      #been push in 500mili seconds
      if max(max(self.klist[65],self.klist[164]),self.klist[162])\
          -min(min(self.klist[65],self.klist[164]),self.klist[162]) < 900:
        #Stop get users
        self.start_auto_mouse = True;
        print "start auto mouse fetching..."
        self.klist[164] =0;
        self.klist[65] =100000;

    #(left)alt+s stop mock mouse
    if event.KeyID in [164,162,83]:# 68 is d
      #been push in 500mili seconds
      if max(max(self.klist[83],self.klist[164]),self.klist[162])\
          -min(min(self.klist[83],self.klist[164]),self.klist[162]) < 900:
        #Stop get users
        self.start_auto_mouse = False;
        print "stop auto mouse fetching ..."

        self.klist[164] =0;
        self.klist[83] =100000;

    #ctrl+d get training
    if event.KeyID in [164,162,68]:# 68 is d
      #been push in 500mili seconds
      if max(max(self.klist[68],self.klist[164]),self.klist[162])\
          -min(min(self.klist[68],self.klist[164]),self.klist[162]) < 900:
        #Stop get users
        self.start_moc_input = True;
        print "Please start training auto mouse..."
        self.klist[164] =0;
        self.klist[68] =100000;

    return True

# if __name__=="__main__":
#   th = hook_thread();
#   hstr = u""
#   hstr+= u"本软件通过模拟鼠标和键盘动作，获取当前房间内用户列表\r\n";
#   hstr+= u"如果您的分辨率不是1366×786,则需要输入八个定位点\r\n";
#   hstr+= u"输入moc（不分大小写），然后按照图示输入8个定位点\r\n";
#   hstr+= u"或按(左边)alt+d，然后按照图示输入8个定位点\r\n";
#   hstr+= u"输入start（不分大小写）,即启动自动模拟鼠标操作获取在线学员的信息\r\n";
#   hstr+= u"或按(左边)alt+a,即启动自动模拟鼠标操作获取在线学员的信息\r\n";
#   hstr+= u"获取信息时，请不要按键或移动鼠标 \r\n"
#   hstr+= u"按(左边)alt+s，再等一会，可停止自动鼠标移动 \r\n";
#   hstr+= u"按(左边)alt+c, 即可拷屏，并把结果自动保存到本软件运行的目录下\r\n";
#   print hstr;
#   while True:
#     if True:
#     # try:
#        in_str = raw_input("");
#        comm = in_str.split()[0].upper();
#        if comm == 'MOC':
#          th.start_input_pos();
#          continue;
#        elif comm == 'START':
#          th.start_capture();
#          continue;
#     # except:
#     #   import sys
#     #   print sys.exc_traceback()
#     #   print sys.exc_info()
#     #   pass;
#     print hstr;
'''