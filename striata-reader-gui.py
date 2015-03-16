#! /usr/bin/python

#  Small PyQt applicaion that gives stiata-reader a GUI.  
#
# Pass filename of .emc statement as first argument, for use as "open with" from browser.
# 
#		eg:
#			striata-reader-gui.py ../path/to/statement.emc
#
# Script dependencies:
#     - striata-reader for Linux  (get it from http://www.striata.com/resources/striata-reader/index.php)
#     - PyQt4 (see your distribution's docs about how to install it )

import sys
import os
import subprocess
import string
import shutil
from PyQt4 import QtGui
from PyQt4 import QtCore

global PATH_TO_STRIATA_READER, STRIATA_READER_DEFAULT_OPTIONS, TEMP_FOLDER, STATEMENT_BROWSE_FILE_FILTER_LIST
# NOTE older versions of striata might work with the following path.  Just uncomment to make it work.
# Remember to point it to the *binary* version of striata-reader
#PATH_TO_STRIATA_READER = "/usr/bin/striata-reader-1.0-27-linux"
PATH_TO_STRIATA_READER = "/usr/bin/striata-readerc"
STRIATA_READER_DEFAULT_OPTIONS = ["-openwith=/usr/bin/firefox"]
TEMP_FOLDER = "/tmp/striata-gui/"
STATEMENT_BROWSE_FILE_FILTER_LIST = "Statements (*.emc);;All files (*)"

def createTempDir():
        if not os.path.exists(TEMP_FOLDER):
                os.mkdir(TEMP_FOLDER)
                
def deleteTempDir():
        if os.path.exists(TEMP_FOLDER):
                shutil.rmtree(TEMP_FOLDER)
                
def displayError(message):
        QtGui.QMessageBox.critical(None, "Decoder error", message)
        
def displayWarning(message):
        QtGui.QMessageBox.warning(None, "Decoder warning", message)

class ProcessStarter():
        def __init__(self, filePathGetter, passwordGetter):
                self.filePathGetter = filePathGetter
                self.passwordGetter = passwordGetter

        def startProcess(self):
                argumentList = [PATH_TO_STRIATA_READER] + STRIATA_READER_DEFAULT_OPTIONS + [str("-password=" + self.passwordGetter()), str(self.filePathGetter()), "-outdir="+TEMP_FOLDER]
                try:
                        process = subprocess.Popen(argumentList, 0,  stdout=subprocess.PIPE, shell=False)
                        output = process.communicate()
                except:
                        errorMessage = "Running " + PATH_TO_STRIATA_READER + " failed for some reason. Does the file exist? Is it the correct path? Did you install striata-reader?"
                        
                        try:
                            # not everyone has the magic lib
                            import magic
                            magicChecker = magic.open(magic.MAGIC_MIME)
                            magicChecker.load()
                            fileTypeAsString = magicChecker.file(PATH_TO_STRIATA_READER)
                            if 'text' in fileTypeAsString:
                                errorMessage = errorMessage + " Please note that the selected executable is not a binary file."
                        except:
                            pass
                        displayError(errorMessage)
                        return
                        
                if (process.returncode != 0):
                        decodeError = "Decoding document failed.\n" + PATH_TO_STRIATA_READER + " said:\n"
                        for o in output:
                                if (o != None):
                                        decodeError = decodeError + o
                        displayError(decodeError)
                                        
class Dialog(QtGui.QDialog):
        def __init__(self, parent =None):
                QtGui.QWidget.__init__(self, parent)
                self.setWindowTitle('Statement decoder')
                mainLayout = QtGui.QVBoxLayout()
                self.setLayout(mainLayout)
                
                openFileLayout = QtGui.QHBoxLayout()
                openFileLabel = QtGui.QLabel("Path to statement")
                mainLayout.addWidget(openFileLabel)
                mainLayout.addLayout(openFileLayout)
                self.fileLineEdit = QtGui.QLineEdit()
                fileOpenButton = QtGui.QPushButton("Browse")
                openFileLayout.addWidget(self.fileLineEdit)
                openFileLayout.addWidget(fileOpenButton)
                
                self.decodeButton = QtGui.QPushButton("Open statement")
                
                passwordLabel = QtGui.QLabel("Enter password")
                self.passwordLineEdit = QtGui.QLineEdit()
                self.passwordLineEdit.setEchoMode(QtGui.QLineEdit.Password)
                self.decodeButton = QtGui.QPushButton("Open statement")
                self.decodeButton.setDefault(True)
                
                mainLayout.addWidget(passwordLabel)
                mainLayout.addWidget(self.passwordLineEdit)
                mainLayout.addStretch()
                mainLayout.addWidget(self.decodeButton)
                self.connect(fileOpenButton, QtCore.SIGNAL('pressed()'), self.askForFile)
                
        def askForFile(self):
                filepath = QtGui.QFileDialog.getOpenFileName(self, "Specify path to statement", "", STATEMENT_BROWSE_FILE_FILTER_LIST)
                self.setFilename(filepath)
                
        def setFilename(self, filepath):
                self.fileLineEdit.setText(filepath)

if __name__ == "__main__":
        app = QtGui.QApplication(sys.argv)
        dialog = Dialog()
        
        processStarter = ProcessStarter(dialog.fileLineEdit.text, dialog.passwordLineEdit.text)
        dialog.connect(dialog.decodeButton, QtCore.SIGNAL('pressed()'), processStarter.startProcess)
        
        createTempDir()
        if len(sys.argv) > 1:
                dialog.setFilename(sys.argv[1])	
        dialog.show()
        
        result = app.exec_()
        try:
                deleteTempDir()
        except:
                displayWarning("Temp dir '" + TEMP_FOLDER +"' could not be deleted.  Your statements were extracted here.")
                
        sys.exit(result)

