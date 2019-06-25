import sys
import vtk
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
import os

from PyQt5 import QtCore, QtGui
from PyQt5 import Qt
from fury import window,actor
from PyQt5.QtWidgets import QLabel,QRadioButton,QComboBox,QPushButton, QAction, QMenu, QApplication, QFileDialog, QWidget, QSplitter, QGroupBox
from PyQt5.QtGui import QIcon

from dipy.data import fetch_bundles_2_subjects, read_bundles_2_subjects
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from dipy.tracking.streamline import transform_streamlines, length

from shutil import copyfile

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FingureCanvas
from matplotlib.figure import Figure
import pickle
from nibabel import trackvis
from dipy.tracking import utils
interactive = False  # set to True to show the interactive display window

class MainWindow(Qt.QMainWindow):

    def __init__(self, parent = None):
        
        Qt.QMainWindow.__init__(self, parent)

        ####################### menubar###############
        title = "Tractography"
#        top = 400
#        left = 400
#        width = 900
#        height = 500
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File ')
        newAct = QAction('New', self)                
        fileMenu.addAction(newAct)
        ##newAct.triggered.connect(self.openFileNameDialog)
        self.setWindowIcon(QIcon("download.jpg"))
        self.setWindowTitle(title)
        #self.setGeometry(top,left, width, height)
              
        ####################### Pyqt############### 


        ########## frame##################


        self.frame = Qt.QFrame()
        self.VerticalLayout()
        self.HorizontalLayout()


        self.vl = Qt.QVBoxLayout()

        self.vl.addLayout(self.vMain)
        self.vl.addWidget(self.groupBox2)

        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)
        
        self.setLayout(self.vl)
        self.show()

    def VerticalLayout(self):

        self.vMain = Qt.QHBoxLayout()
        groupBox1 = QGroupBox("Select Whole Brain")
        whole_brain = []
        for (dirpath, dirnames, filenames) in os.walk("WholeBrains"):
            whole_brain.extend(filenames)
            break

        self.combo_box1 = QComboBox()
        self.combo_box1.addItems(whole_brain)
        button_box1 = QPushButton("Add")
        button_box2 = QPushButton("Okay")

        button_box2.clicked.connect(self.clickMethod)
        button_box1.clicked.connect(self.openFileNameDialog)

        vbox = Qt.QVBoxLayout()
        vbox.addWidget(self.combo_box1)
        vbox.addWidget(button_box1)
        vbox.addWidget(button_box2)
        vbox.addStretch(1)


        groupBox1.setLayout(vbox)
        ####################################################
        groupBox3 = QGroupBox("Select Tract")
        tracts = ["AF", "CG", "UF"]
        self.combo = QComboBox()
        self.combo.addItems(tracts)
        self.radio1 = QRadioButton("Left tract")
        self.radio1.setChecked(True)
        self.radio2 = QRadioButton("Right tract")
        self.radio3 = QRadioButton("None")
        label = QLabel()
        label.setText("\nKD tree K value :")

        k = ['1', '2', '3', '4']
        comboForK = QComboBox()
        comboForK.addItems(k)

        button = QPushButton("Okay")

        button.clicked.connect(self.clickMethod2)

        vbox3 = Qt.QVBoxLayout()
        vbox3.addWidget(self.combo)
        vbox3.addWidget(self.radio1)
        vbox3.addWidget(self.radio2)
        vbox3.addWidget(self.radio3)
        vbox3.addWidget(label)
        vbox3.addWidget(comboForK)
        vbox3.addWidget(button)
        vbox3.addStretch(1)
        groupBox3.setLayout(vbox3)

        self.vMain.addWidget(groupBox1)
        self.vMain.addWidget(groupBox3)

    def HorizontalLayout(self):
        self.groupBox2 = QGroupBox("vtk Rendering")
        self.vbox2 = Qt.QHBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vbox2.addWidget(self.vtkWidget)
        # self.vl.addWidget(self.frame)

        ############################################

        self.vtkWidget2 = QVTKRenderWindowInteractor(self.frame)
        self.vbox2.addWidget(self.vtkWidget2)
        self.groupBox2.setLayout(self.vbox2)

    def clickMethod(self):

        whole_brain = "WholeBrains/" + str(self.combo_box1.currentText())
        self.load_streamline(whole_brain)
    def clickMethod2(self):

        #AllPickles = []
        #for (dirpath, dirnames, filenames) in os.walk("AllPickles"):
        #    AllPickles.extend(filenames)
        #    break
        side = ""
        if self.radio1.isChecked():
            side = "Left"
        elif self.radio2.isChecked():
            side = "Right"
        elif self.radio3.isChecked():
            side = "Left"

        choose_pickle = self.combo.currentText() + side + ".pickle"
        Title = self.combo.currentText() + side

        choosed_pickle = "AllPickles/" + choose_pickle
        whole_brain = "WholeBrains/" + str(self.combo_box1.currentText())

        self.load_streamline2(whole_brain,choosed_pickle)
        #if choose_pickle in AllPickles:
        #    choosed_pickle = "AllPickles/" + choose_pickle
        #    whole_brain = "WholeBrains/" + str(self.combo_box1.currentText())
        #    print("choosed_pickle",choosed_pickle)
        #    print("whole_brain", whole_brain)


    def openFileNameDialog(self):
        global fileName 
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileWithPath, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Track Files (*.trk)", options=options)
        fileName=os.path.basename(fileWithPath)
        splitFile=fileName.split(".")[0]
        print(splitFile)
        j=0
        while 1:
            doChange=self.checkFile(fileName)
            print(doChange)
            if doChange is 0:
                break
            else:
                j=j+1
                print(j)
                fileName=splitFile+"("+str(j)+").trk"
                print(fileName)


        dest="C:/Users/User/Desktop/Demo/WholeBrains/"+fileName
        copyfile(fileWithPath, dest)
        self.combo_box1.clear()
        whole_brain = []
        for (dirpath, dirnames, filenames) in os.walk("WholeBrains"):
                whole_brain.extend(filenames)
                break
        self.combo_box1.addItems(whole_brain)
        print("done...")

    def checkFile(self,fileName):
        whole_brain = []
        for (dirpath, dirnames, filenames) in os.walk("WholeBrains"):
            whole_brain.extend(filenames)
            break
        if fileName in whole_brain:
            return 1
        else:
            return 0

    def load_streamline(self,fileName):
        
        print(fileName)
        global wholeTract
        from fury import window
        scene = window.Scene()
        
        affine=utils.affine_for_trackvis(voxel_size=np.array([1.25,1.25,1.25]))

        wholeTract= nib.streamlines.load(fileName)
        wholeTract = wholeTract.streamlines
        print(wholeTract)        
        wholeTract_transform = transform_streamlines(wholeTract, np.linalg.inv(affine))
        stream_actor = actor.line(wholeTract_transform)

        #scene.set_camera(position=(-176.42, 118.52, 128.20),
        #         focal_point=(113.30, 128.31, 76.56),
        #         view_up=(0.18, 0.00, 0.98))   
        scene.add(stream_actor)
        
        self.vtkWidget.GetRenderWindow().AddRenderer(scene)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.iren.Initialize()
        self.iren.Start()
    
    def load_streamline2(self,fileName,fileName2):
        from fury import window
        scene = window.Scene()
        
        affine=utils.affine_for_trackvis(voxel_size=np.array([1.25,1.25,1.25]))
        
        print(fileName)
        choosed_pickle = fileName2
        whole_brain=fileName
        T, hdr = trackvis.read(whole_brain, as_generator=False)
        T = np.array([s[0] for s in T], dtype=np.object)

        pickle_in = open(choosed_pickle, "rb")
        st = pickle.load(pickle_in)
        tr = []
        vote = []
        v = []
        vote2 = [0] * len(T)

        for l in range(len(st)):
            m, k = max((v, i) for i, v in enumerate(st[l]))

            if m > 0:
                if (m == 1):
                    vote2.pop(l)
                    vote2.insert(l, 1)

                tr.append(l)

        tk = []
        for o in range(len(T)):
            if o not in tr:
                tk.append(o)
        T2 = np.delete(T, tk)
        vote = np.delete(vote2, tk)
        vote.tolist()

        part1 = []
        part2 = []
        total = []
        total = T2.tolist()
        for i in range(len(vote)):

            if vote[i] == 1:
                part1.append(total[i])


            else:
                part2.append(total[i])
                
        tract_transform = transform_streamlines(part1, np.linalg.inv(affine))
        stream_actor = actor.line(tract_transform,(1., 0.5, 0))

        tract_transform2 = transform_streamlines(part2, np.linalg.inv(affine))
        stream_actor2 = actor.line(tract_transform2,(0, 0.5, 1.))
        
        scene.add(stream_actor)
        scene.add(stream_actor2)
        
        self.vtkWidget2.GetRenderWindow().AddRenderer(scene)
        self.iren = self.vtkWidget2.GetRenderWindow().GetInteractor()
        self.iren.Initialize()
        self.iren.Start()
if __name__ == "__main__":
    
    app = Qt.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
