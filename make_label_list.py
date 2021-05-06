import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QInputDialog, QPushButton
from PyQt5.QtCore import QSize, QAbstractTableModel, Qt, QVariant
import yaml
import os

class GUI(QWidget):
    def __init__(self):
        super(GUI, self).__init__()
        self.initUI()
        self.label_list = []
        self.sup_check = []
        self.cat_check = []

    def initUI(self):

        first_row_button_loc = (110, 100)
        second_row_button_loc = (110, 150)
        button_sizes = (100, 50)
        # self.le = QLineEdit(self)

        '''Insert Class'''
        ins_button = QPushButton('Add', self)
        ins_button.clicked.connect(self.ins_click)
        ins_button.resize(button_sizes[0], button_sizes[1])
        ins_button.move(first_row_button_loc[0], first_row_button_loc[1])

        '''Undo'''
        undo_button = QPushButton('Delete', self)
        undo_button.clicked.connect(self.del_click)
        undo_button.resize(button_sizes[0], button_sizes[1])
        undo_button.move(first_row_button_loc[0] * 2, first_row_button_loc[1])

        '''Done'''

        done_button = QPushButton('Done', self)
        done_button.clicked.connect(self.save_click)
        done_button.resize(button_sizes[0], button_sizes[1])
        done_button.move(second_row_button_loc[0], second_row_button_loc[1])

        '''Reset'''
        Reset_button = QPushButton('Reset', self)
        Reset_button.clicked.connect(self.clear_click)
        Reset_button.resize(button_sizes[0], button_sizes[1])
        Reset_button.move(second_row_button_loc[0] * 2, second_row_button_loc[1])

        '''View'''
        Reset_button = QPushButton('View', self)
        Reset_button.clicked.connect(self.view_click)
        Reset_button.resize(button_sizes[0], button_sizes[1])
        Reset_button.move(second_row_button_loc[0] * 0.1, second_row_button_loc[1])

    def ins_click(self):
        text_1, ok_1 = QInputDialog.getText(self, "Super Category", "Enter")
        if ok_1 == False:
            return
        text_2, ok_2 = QInputDialog.getText(self, "Category Name", "Enter")
        if ok_2 == False:
            return
        # ok 는 입력 여부 판단하는 녀석임.

        if ok_1 and ok_2 and text_1 != "" and text_2 != "":
            if text_2 not in self.cat_check:
                if text_1 not in self.sup_check:
                    self.label_list.append(
                        {"super category number": len(self.sup_check),
                         "super category": text_1,
                         "category number": len(self.cat_check),
                         "category": text_2,
                         }
                    )
                    self.sup_check += [text_1]
                    self.cat_check += [text_2]
                else:
                    self.label_list.append(
                        {"super category number": len(self.sup_check)-1,
                         "super category": text_1,
                         "category number": len(self.cat_check),
                         "category": text_2,
                         }
                    )
                    self.cat_check += [text_2]

        elif text_1 == "" or text_2 == "":
            print("Please fill in all fields.")
            self.ins_click()

    def del_click(self):
        text_1, ok_1 = QInputDialog.getText(self, "Select list number", "Enter")
        if ok_1 == False:
            return
        if text_1.isdigit()!=True :
            print("Please insert a number")
            return self.del_click()
        else:
            if int(text_1) < 0 or int(text_1) >= len(self.cat_check):
                print("Please insert valid range integer number")
                return self.del_click()
            else:
                idx = int(text_1)
                del self.label_list[idx]

    def save_click(self):
        text_1, ok_1 = QInputDialog.getText(self, "Insert a folder path to be saved", "Enter")
        if ok_1 == False:
            return
        if os.path.isdir(text_1):
            with open(os.path.join(text_1, 'label_list.yaml'), "w") as f:
                yaml.dump(self.label_list, f)
            f.close()

            print('Class list is saved.')
        else:
            print("Please insert valid folder path which a label-list file will be saved.")
            self.save_click()

    def clear_click(self):
        print('Removed all class list')
        self.label_list = []

    def view_click(self):
        if len(self.label_list) == 0:
            print("There are no items")
        else:
            for val in self.label_list:
                print(val)

app = QtWidgets.QApplication(sys.argv)
mainWin = GUI()
mainWin.show()
sys.exit(app.exec_())



