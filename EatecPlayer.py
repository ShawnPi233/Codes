from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from GUI3 import Ui_MainWindow
from myVideoWidget import myVideoWidget
import qtmodern.styles
import qtmodern.windows
import sqlite3
from PyQt5.QtWidgets import QApplication,QWidget,QPushButton,QHBoxLayout,QBoxLayout,QLabel,\
    QSlider,QStyle,QSizePolicy,QVBoxLayout,QFileDialog
from PyQt5.QtMultimedia import QMediaPlayer,QMediaContent
from _pyinstaller_hooks_contrib import*

import os
import sys
import qtmodern.styles
import qtmodern.windows
import datetime
from PyQt5.QtCore import Qt

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow
from PyQt5.QtGui import QIcon
#---------------------------------------------------对话框弹窗类--------------------------------------------------------
class MyDialog(QDialog):
    def __init__(self, parent=None):
        super(MyDialog, self).__init__(parent)
        self.resize(250,100)
        layout = QFormLayout()
        self.lb1 = QLabel("账号")
        self.le1 = QLineEdit()
        layout.addRow(self.lb1, self.le1)
        self.lb2 = QLabel("邮箱")
        self.le2 = QLineEdit()
        layout.addRow(self.lb2, self.le2)
        self.btn3=QPushButton("发送验证邮件")
        layout.addRow(self.btn3)
        self.setLayout(layout)
        self.setWindowTitle("找回密码")
        self.setWindowIcon(QIcon(r"EatecPlayer_logo.png"))  # 任务栏图标添加
#-----------------------------------------------------激活码验证弹窗-----------------------------------------------
class CodeValidateWindow(QDialog):
    def __init__(self, parent=None):
        self.isVIP=False
        super(CodeValidateWindow, self).__init__(parent)
        self.resize(250,100)
        self.setWindowTitle("激活VIP")
        layout = QFormLayout()
        self.lb_acc = QLabel("账号")
        self.le_acc = QLineEdit()
        layout.addRow(self.lb_acc, self.le_acc)
        self.lb_code = QLabel("激活码")
        self.le_code= QLineEdit()
        layout.addRow(self.lb_code, self.le_code)
        self.btn_confirmCode=QPushButton("确定激活")
        self.btn_confirmCode.clicked.connect(self.validate_code)

        layout.addRow(self.btn_confirmCode)
        self.setLayout(layout)
        self.setWindowIcon(QIcon(r"icon.png"))  # 任务栏图标添加

    def validate_code(self):
        sql = sqlite3.connect('user_data.db')
        self.data = sql.execute("select * from user where name='%s'" % self.le_acc.text()).fetchone()
        if self.data:
            if self.data[5] == self.le_code.text():
                self.isVIP=True
        sql.close()
        if self.isVIP:
            QMessageBox.about(self, "激活验证", "激活成功，尊敬的SVIP用户！")
        else:
            QMessageBox.warning(self, "激活验证", "激活失败，请检查账号激活码！")
#-------------------------------------------------------主窗体类--------------------------------------------------------
class myMainWindow(Ui_MainWindow,QMainWindow,CodeValidateWindow):
    def __init__(self):
        self.create_sql() #创建用户数据库
        self.isOpen = False
        self.isLogin= False
        self.sld_video_pressed = False
        self.app = QApplication(sys.argv)
        super(Ui_MainWindow,self).__init__()
        super(CodeValidateWindow, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(r"icon.png")) #任务栏图标添加
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.videoFullScreen = False   # 判断当前widget是否全屏
        self.videoFullScreenWidget = myVideoWidget()   # 创建一个全屏的widget
        self.videoFullScreenWidget.setFullScreen(True)
        self.videoFullScreenWidget.hide()               # 不用的时候隐藏起来
        self.player = QMediaPlayer(None,QMediaPlayer.VideoSurface)
        self.player.setVideoOutput(self.wgt_video)  # 视频播放输出的widget，就是上面定义的
        self.slider.sliderMoved.connect(self.set_position)
        self.slider.valueChanged.connect(self.setClock)  # 设置时间条
        self.player.positionChanged.connect(self.position_changed)
        self.player.durationChanged.connect(self.duration_changed)
        self.btn_open.clicked.connect(self.openVideoFile)   # 打开视频文件按钮
        self.btn_login.clicked.connect(self.login) #登录确认
        self.btn_play.clicked.connect(self.playVideo)       # play
        self.btn_stop.clicked.connect(self.pauseVideo)       # pause
        self.btn_close.clicked.connect(self.close)
        self.btn_max.clicked.connect(self.formchange)
        self.btn_mini.clicked.connect(self.showMinimized)
        self.btn_darkmode.clicked.connect(self.darkMode)
        self.btn_fullscreen.clicked.connect(self.videoDoubleClicked)
        self.btn_findPassword.clicked.connect(self.findpswd)
        self.btn_openVIP.clicked.connect(self.show_codeValidateWindow)
        self.volSlider.valueChanged.connect(self.volChanged) #音量控制
        #self.setWindowFlag(Qt.FramelessWindowHint)  #隐藏边框
        # self.setWindowOpacity(0.9)  # 设置窗口透明度
        # self.setAttribute(Qt.WA_TranslucentBackground) # 设置窗口背景透明
        self.videoFullScreenWidget.doubleClickedItem.connect(self.videoDoubleClicked) #双击响应
        self.wgt_video.doubleClickedItem.connect(self.videoDoubleClicked)   #双击响应
        qss = "QPushButton{color:black;font:幼圆}" \
              "QPushButton:hover{color:#888888}" \
              "QPushButton:!hover { color: black }" \
              "QPushButton:hover { boder:3px blue  }"
        self.setStyleSheet(qss)
        #--------------------工具栏调用--------------------------
        # self.comboBox.currentIndexChanged.connect(self.tools_choose)  # 点击下拉列表，触发对应事件
        # self.comboBox.activated(self,4).connect(self.show_notebook)
        now = datetime.datetime.now()
        if now.hour>=17 or now.hour<=5:
            self.isDark = True
            self.btn_darkmode.setStyleSheet \
                ("text-align:top;background:#FFFFFF;border-radius:8px")
        else:
            self.isDark = False
            self.btn_darkmode.setStyleSheet \
                ("text-align:top;background:#000000;border-radius:8px")
        # self.actionStudy.triggered.connect()
    def tools_choose(self):
        self.choice=4
        #self.comboBox.currentIndex()
        self.show_notebook()


    #--------------------------------窗体类内方法实现----------------------------------
    def formchange(self):
        if self.isMaximized():
            self.showNormal()# 切换放大按钮图标字体
        else:
            self.showMaximized()
    def openVideoFile(self):
        if self.isLogin:
            self.player.setMedia(QMediaContent(QFileDialog.getOpenFileUrl()[0]))  # 选取视频文件
            self.wgt_video.setVisible(True)
            self.player.play()  # 播放视频
            self.isOpen = True
            self.playVideo()
        else:self.openError()
    def playVideo(self):
        if self.isOpen==False:
            self.player.play()
            self.isOpen = True
            self.btn_play.setText("▎▎")
            self.btn_play.setStyleSheet("font-size:15px;border:none")
        else:
            self.player.pause()
            self.isOpen = False
            self.btn_play.setText("▶")
            self.btn_play.setStyleSheet("font-size:35px;border:none")
    def pauseVideo(self):
        self.player.pause()
    #------------------------------全屏按钮全屏--------------------------------
    def videoFullScreen(self):
        if self.player.duration() > 0:
            if self.videoFullScreen:
                self.player.pause()
                self.videoFullScreenWidget.hide()
                self.player.setVideoOutput(self.wgt_video)
                self.player.play()
                self.videoFullScreen = False
            else:
                self.player.pause()
                self.videoFullScreenWidget.show()
                self.player.setVideoOutput(self.videoFullScreenWidget)
                self.player.play()
                self.videoFullScreen = True
    #双击视频全屏
    def videoDoubleClicked(self,text):
        if self.player.duration() > 0:  # 开始播放后才允许进行全屏操作
            if self.videoFullScreen:
                self.player.pause()
                self.videoFullScreenWidget.hide()
                self.player.setVideoOutput(self.wgt_video)
                self.player.play()
                self.videoFullScreen = False
            else:
                self.player.pause()
                self.videoFullScreenWidget.show()
                self.player.setVideoOutput(self.videoFullScreenWidget)
                self.player.play()
                self.videoFullScreen = True
    #单击登录，并弹窗提示
    def login(self):
        sql = sqlite3.connect('user_data.db')
        self.data = sql.execute("select * from user where name='%s'" %self.account_text.text()).fetchone()
        if self.data:
                if self.data[2] == self.password_text.text():
                    self.isLogin=True
        sql.close()
        if self.isLogin:
                    self.pureVideo()  # 只显示视频 去除登录界面
                    QMessageBox.about(self, "登录验证", "登录成功，尊敬的VIP用户！")
        else:
            QMessageBox.warning(self, "登录验证", "登录失败，请检查账号密码！")
            # print("账号：%s \n 密码：%s",data[1],data[2])
    #找回密码
    def findpswd(self):
        self.show_dialog()
        QMessageBox.about(self, "验证邮件", "发送成功，请到邮箱查收！")
        self.flag=True
    # def validate_code(self):
    #     self.show_codeValidateWindow()
    #     sql = sqlite3.connect('user_data.db')
    #     self.data = sql.execute("select * from user where name='%s'" % self.account_text.text()).fetchone()
    #     if self.data:
    #         if self.data[3] == self.code:
    #             self.isLogin = True
    #     sql.close()
    #     if self.isLogin:
    #         self.pureVideo()  # 只显示视频 去除登录界面
    #         QMessageBox.about(self, "登录验证", "登录成功，尊敬的VIP用户！")
    #     else:
    #         QMessageBox.warning(self, "登录验证", "登录失败，请检查账号密码！")
    #             print("账号：%s \n 密码：%s",self.data[1],self.data[2])
    #打开视频时隐藏登录界面
    def pureVideo(self):
        self.account_label.hide()
        self.password_label.hide()
        self.account_text.hide()
        self.password_text.hide()
        self.btn_login.hide()
        self.btn_rigis.hide()
        self.btn_findPassword.hide()

    def openError(self):
        QMessageBox.about(self, "打开失败", "请先登录账号！")

#--------------------------------以下为无边框窗口移动实现方法---------------------------#
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))  # 更改鼠标图标

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.m_flag:
            self.move(QMouseEvent.globalPos() - self.m_Position)  # 更改窗口位置
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))

# --------------------------------夜间模式实现方法---------------------------#
    def darkMode(self):
        if self.isDark==False :#天黑自动夜间模式或手动夜间模式
            qtmodern.styles.dark(self.app)
            self.btn_darkmode.setStyleSheet\
                ("\ text-align:top;\
                background:#FFFFFF;\
                border-radius:8px;\
                border:none;\
                font-size:13px;")
            self.isDark = True
        else :
            qtmodern.styles.light(self.app)
            self.btn_darkmode.setStyleSheet\
                ("\ text-align:top;\
                background:#000000;\
                border-radius:8px;\
                border:none;\
                font-size:13px;")
            self.isDark = False
    #弹出窗体显示
    def show_dialog(self):
        dialog = MyDialog()
        dialog.show()
        dialog.exec()
    def show_notebook(self):
        note = NotebookWindow()
        note1 = qtmodern.windows.ModernWindow(note)
        note1.show()
    def show_codeValidateWindow(self):
        codeValidateWindow=CodeValidateWindow()
        codeValidateWindow.show()
        codeValidateWindow.exec()
    #------------------------------------视频进度条------------------------------------------
    def setClock(self):
        tmp1 = self.player.position()
        tmp2 = self.player.duration()
        t1m=str(tmp1 // 1000 // 60).zfill(2)#补足2位 //表示整除
        t1s=str(tmp1 // 1000 % 60).zfill(2)#同上
        t2m=str(tmp2 // 1000 // 60).zfill(2)#同上
        t2s=str(tmp2 //1000 % 60).zfill(2)#同上
        self.lb_time.setText("%s:%s/%s:%s" % (t1m,t1s,t2m,t2s))

    def position_changed(self, position):
        self.slider.setValue(position)
    def duration_changed(self, duration):
        self.slider.setRange(0, duration)

    def set_position(self, position):
        self.player.setPosition(position)
    def volChanged(self): # 音量调节
        self.player.setVolume(self.volSlider.value())
    #------------------------------------用户数据库建立----------------------------------------
    def create_sql(self):
        self.sql = sqlite3.connect("user_data.db")
        self.sql.execute("""create table if not exists
            %s
            (
            %s integer primary key autoincrement,
            %s varchar(128),
            %s varchar(128),
            %s int(1),
            %s char(128),
            %s char(128)
            )"""
                    % ('user', 'id', 'name', 'passworld', 'ifvip', 'vipstatus', 'key')
                    )
        self.sql.close()

    def showdata(username):
        sql = sqlite3.connect('user_data.db')
        data =sql.execute("select * from user where name='%s'" %
                           username).fetchone()
        sql.close()
        return data
    #----------------------------------------工具栏功能实现方法-------------------------------------------

    def __main__(self):
        self.app = QApplication(sys.argv)
        self.mw = myMainWindow()
        now = datetime.datetime.now()
        if now.hour >= 17 or now.hour <= 5:
            qtmodern.styles.dark(self.app)
        else:
            qtmodern.styles.light(self.app)
        self.mw.show()
        sys.exit(self.app.exec_())
class NotebookWindow(myMainWindow):
    def __init__(self):
        # super(NotebookWindow, self).__init__()
        super(myMainWindow, self).__init__()
        # self.setGeometry(600, 500, 570, 445)
        layout = QFormLayout()
        self.lb_text = QLabel("笔记")
        self.le_text = QTextEdit()
        layout.addRow(self.lb_text, self.le_text)
        self.lb_name = QLabel("笔记命名")
        self.le_name = QLineEdit()
        layout.addRow(self.lb_name, self.le_name)
        self.btn_save = QPushButton("保存便笺")
        layout.addRow(self.btn_save)
        self.setLayout(layout)
        self.setWindowIcon(QIcon(r"icon.png"))  # 任务栏图标添加
        self.btn_save.clicked.connect(self.save_notebook)

        self.setWindowTitle("食课便笺")
        self.setGeometry(600, 500, 570, 445)
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.setWindowIcon(QIcon('icon.png'))
        self.setWindowOpacity(0.9)

        nowTime = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        self.filename = nowTime + '.txt'
        self.openFileName = self.filename
        self.openFilePath = r'Notes:'
        self.isSaved = False
        self.fintText = ''
        self.replaceText = ''

        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(0, 1, 0, 0)

        self.menuBar = QMenuBar(self)
        self.setMenuBar(self.menuBar)

        self.menuFile = QMenu("文件(&F)")
        self.menuEdit = QMenu("编辑(&E)")
        self.menuFormat = QMenu("格式(&D)")
        self.menuView = QMenu("查看(&V)")
        self.menuHelp = QMenu("帮助(&H)")
        self.menuBar.addMenu(self.menuFile)
        self.menuBar.addMenu(self.menuEdit)
        self.menuBar.addMenu(self.menuFormat)
        self.menuBar.addMenu(self.menuView)
        self.menuBar.addMenu(self.menuHelp)

        self.menuFileNew = QAction("新建(&N)")
        self.menuFileNew.setShortcut("Ctrl+N")
        self.menuFile.addAction(self.menuFileNew)
        self.menuFileNew.triggered.connect(self.newFile)

        self.menuFileOpen = QAction("打开(&O)")
        self.menuFileOpen.setShortcut("Ctrl+O")
        self.menuFile.addAction(self.menuFileOpen)
        self.menuFileOpen.triggered.connect(self.openFile)

        self.menuFileSave = QAction("保存(&S)")
        self.menuFileSave.setShortcut("Ctrl+S")
        self.menuFile.addAction(self.menuFileSave)
        self.menuFileSave.triggered.connect(self.saveFile)

        self.menuFileSaveAs = QAction("另存为(&A)...")
        self.menuFile.addAction(self.menuFileSaveAs)
        self.menuFileSaveAs.triggered.connect(self.saveas)

        self.menuFile.addSeparator()
        self.menuExit = QAction("退出(&X)")
        self.menuFile.addAction(self.menuExit)
        self.menuExit.triggered.connect(self.exit)

        self.menuEditUndo = QAction("撤销(&U)")
        self.menuEditUndo.setShortcut("Ctrl+Z")
        self.menuEdit.addAction(self.menuEditUndo)
        self.menuEditUndo.triggered.connect(self.undo)

        self.menuEdit.addSeparator()

        self.menuEditCut = QAction("剪切(&T)")
        self.menuEditCut.setShortcut("Ctrl+X")
        self.menuEdit.addAction(self.menuEditCut)
        self.menuEditCut.triggered.connect(self.cut)

        self.menuEditCopy = QAction("复制(&C)")
        self.menuEditCopy.setShortcut("Ctrl+C")
        self.menuEdit.addAction(self.menuEditCopy)
        self.menuEditCopy.triggered.connect(self.copy)

        self.menuEditPaste = QAction("粘贴(&P)")
        self.menuEditPaste.setShortcut("Ctrl+V")
        self.menuEdit.addAction(self.menuEditPaste)
        self.menuEditPaste.triggered.connect(self.paste)

        self.menuEditDel = QAction("删除(&T)")
        self.menuEditDel.setShortcut("Del")
        self.menuEdit.addAction(self.menuEditDel)
        self.menuEditDel.triggered.connect(self.delete)

        self.menuEdit.addSeparator()
        self.menuEdit.addSeparator()

        self.menuEditAll = QAction("全选(&A)")
        self.menuEditAll.setShortcut("Ctrl+A")
        self.menuEdit.addAction(self.menuEditAll)
        self.menuEditAll.triggered.connect(self.selectAll)

        # self.menuEditDate = QAction("时间/日期(&D)")
        # self.menuEditDate.setShortcut("F5")
        # self.menuEdit.addAction(self.menuEditDate)
        # self.menuEditDate.triggered.connect(self.insertDatetime)

        self.menuFormatWarp = QAction("自动换行(&W)")
        self.menuFormatWarp.setCheckable(True)
        self.menuFormatWarp.setChecked(True)
        self.menuFormat.addAction(self.menuFormatWarp)
        self.menuFormatWarp.changed.connect(self.formatWarp)

        self.menuFormatFont = QAction("字体(&F)...")
        self.menuFormat.addAction(self.menuFormatFont)
        self.menuFormatFont.triggered.connect(self.fontSelect)

        self.menuViewStatusBar = QAction("状态栏(&S)")
        self.menuViewStatusBar.setCheckable(True)
        self.menuViewStatusBar.setChecked(True)
        self.menuView.addAction(self.menuViewStatusBar)
        self.menuViewStatusBar.changed.connect(self.statusBarShow)

        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)

        self.plainTextEdit = QPlainTextEdit(self)
        self.gridLayout.addWidget(self.plainTextEdit)
        self.font = QFont("幼圆", 12)
        self.plainTextEdit.setFont(self.font)
        self.plainTextEdit.cursorPositionChanged.connect(self.cursorPosition)
        self.plainTextEdit.textChanged.connect(self.textChange)
        self.plainTextEdit.setPlainText("视频类别：计算机网络（识别有误？可编辑修正！）\n"
                                        "关键词：计算机网络 介绍 互联网 基础 局域网\n"
                                        "关键短语：将会介绍 自顶向下\n\n"
                                        "食课时间："+nowTime+"\n"
                                        "本次食课："
                                        )
        # self.plainTextEdit.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # self.plainTextEdit.customContextMenuRequested[QtCore.QPoint].connect(self.myListWidgetContext)
        qss = "QPushButton{color:black;font:幼圆}" \
              "QPushButton:hover{color:#888888}" \
              "QPushButton:!hover { color: black }" \
              "QPushButton:hover { boder:3px blue  }"
        self.setStyleSheet(qss)
        self.show()

    def save_notebook(self):
        nowTime = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        filename=nowTime+'.txt'
        f=open(filename, 'w')
        f.write(self.le_text.toPlainText()) #读取笔记内容
        f.close()
        QMessageBox.about(self, "食课便笺", "保存成功！")

    def get_thread(self, main_thread):
        self.main_thread = main_thread

    def newFile(self):
            self.openFilePath = ''
            self.openFileName = self.filename
            self.setWindowTitle(self.openFileName + ' - 食课便笺')
            self.plainTextEdit.clear()

    def openFile(self):
            filename, filetype = QFileDialog.getOpenFileName(self, "打开", "./", "文本文档 (*.txt);;所有文件 (*)")
            if filename != "":
                self.plainTextEdit.clear()
                with open(filename, 'r', encoding='gb18030', errors='ignore') as f:
                    self.plainTextEdit.appendPlainText(f.read())
                f.close()
                self.openFilePath = filename
                self.openFileName = os.path.basename(filename)
                self.setWindowTitle(self.openFileName + ' - 食课便笺')

    def saveFile(self):
            if self.openFilePath == "":
                filename, filetype = QFileDialog.getSaveFileName(self, '保存', './', "文本文档 (*.txt);;所有文件 (*)")
                if filename == "":
                    return False

                self.openFilePath = filename
                self.openFileName = os.path.basename(filename)
                self.setWindowTitle(self.openFileName + ' - 食课便笺')

            file = open(self.openFilePath, 'w', encoding='gb18030', errors='ignore')
            file.write(self.plainTextEdit.toPlainText())
            file.close()
            self.setWindowTitle(self.openFileName + ' - 食课便笺')
            self.isSaved = True
            return True

    def saveas(self):
            filename, filetype = QFileDialog.getSaveFileName(self, '保存', './', "文本文档 (*.txt);;所有文件 (*)")
            if filename == "":
                return False

            self.openFilePath = filename
            self.openFileName = os.path.basename(filename)
            self.setWindowTitle(self.openFileName + ' - 食课便笺')
            file = open(self.openFilePath, 'w', encoding='gb18030', errors='ignore')
            file.write(self.plainTextEdit.toPlainText())
            file.close()
            self.setWindowTitle(self.openFileName + ' - 食课便笺')
            self.isSaved = True
            return True

    def exit(self):
        if self.isSaved == False:

            result = QMessageBox.question(self, '食课便笺', '是否将更改保存到' + self.openFileName,
                                                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if result == QMessageBox.Yes:
                result = self.saveFile()
                if result == True:
                    QtCore.QCoreApplication.quit()
                else:
                    return False
            elif result == QMessageBox.No:
                QtCore.QCoreApplication.quit()
            else:
                return False

        return True

    def undo(self):
            self.plainTextEdit.undo()

    def cut(self):
            self.plainTextEdit.cut()

    def copy(self):
            self.plainTextEdit.copy()

    def paste(self):
            self.plainTextEdit.paste()

    def delete(self):
            self.plainTextEdit.textCursor().deletePreviousChar()

    def selectAll(self):
            self.plainTextEdit.selectAll()

    # def insertDatetime(self):
    #         datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    #         self.plainTextEdit.insertPlainText(datetime)

    def fontSelect(self):
            font, ok = QFontDialog.getFont(self.font)
            if ok:
                self.font = font
                self.plainTextEdit.setFont(font)
    def textChange(self):
            self.isSaved = False
            self.setWindowTitle('食课便笺  ' + self.openFileName)

    def formatWarp(self):
            if self.menuFormatWarp.isChecked():
                self.plainTextEdit.setLineWrapMode(QPlainTextEdit.WidgetWidth)
            else:
                self.plainTextEdit.setLineWrapMode(QPlainTextEdit.NoWrap)

    def statusBarShow(self):
            if self.menuViewStatusBar.isChecked():
                self.statusBar.show()
            else:
                self.statusBar.hide()

    # def insertDatetime(self):
    #     self.plainTextEdit.insertPlainText(self.lb_time.text())

    def cursorPosition(self):
            row = self.plainTextEdit.textCursor().blockNumber()
            col = self.plainTextEdit.textCursor().columnNumber()
            self.statusBar.showMessage("行 %d , 列 %d" % (row + 1, col + 1))

    def closeEvent(self, QcloseEvent):
            result = self.exit()
            if result == True:
                QcloseEvent.accept()
                self.saveFile()
            else:
                QcloseEvent.ignore()

    #----------------------关闭窗口响应-----------------------------
    def closeEvent(self, event):
        """
        重写closeEvent方法，实现dialog窗体关闭时执行一些代码
        :param event: close()触发的事件
        :return: None
        """
        reply = QMessageBox.question(self,
                                               '食课便笺',
                                               "是否要退出程序？",
                                               QMessageBox.Yes | QMessageBox.No,
                                               QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.save_notebook()
            event.accept()
        else:
            event.ignore()
class Runwindow(myMainWindow):
    def __init__(self):
        super(myMainWindow).__init__()

if __name__== '__main__':
    rw = Runwindow()
    rw.__main__()

