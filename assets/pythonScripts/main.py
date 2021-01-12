# SYSTEM IMPORTS
import os,pathlib,time,json,shutil,argparse

from log import output,output_direct
from generateData import generateMetaData
from HashGen import generateFileHash
from DrivePart import GoogleDrive

# AVAILABLE HASHES, DEFAULT = md5
# [blake2b, blake2s, md5,
# sha1, sha224, sha256,
# sha384, sha3_224, sha3_256,
# sha3_384,sha3_512, sha512,
# shake_128, shake_256]

# .GDFID is a file extention to store Google Drive Folder IDs
  # ummmm

class App():
  APP_FOLDER_PATH = None # APP's Main Folder, Where we are going to store App related Files # APP's Main Folder, Where we are going to store App related Files
  CCODES = None # COMMUNICATION CODES
  APP_SETTINGS = None # APP SETTINGS

  # LOAD REPOSITORY SETTINGS
  REPOSITORY_PATH = None
  REPOSITORY_SETTINGS_PATH = None
  REPOSITORY_SETTINGS = None
  REPOSITORY_LOG_FOLDER_PATH = None
  REPOSITORY_DATA_FOLDER_PATH = None
  REPOSITORY_DIR_DATA_PATH = None
  COMMIT_FILE_PATH = None

  # LOAD CLOUD_STORAGE CONFIGURATION, GID_FOLDER_PATH = GOOGLE DRIVE IDs will be stored
  REPOSITORY_CLOUD_STORAGE_FOLDER_PATH = None
  GID_FOLDER_PATH = None

  Gservice = None

  def __init__(self):
    args_const = argparse.ArgumentParser(description='A File Handing System with Multiple Cloud Storage Support, Build for People by Programmers [i know its cringy]')
    args_const.add_argument('-cd',"--change-directory", metavar='directory', type=str, help='Please Specify a Directory')
    args_const.add_argument('-init',"--initialize", help='Initillizes the Current Working Directory', action="store_true")
    args_const.add_argument('-u',"--update", help='Update the Repository App Data', action="store_true")
    args_const.add_argument('-dev',"--development", help='Enable Development Environment', action="store_true")
    args_const.add_argument('-clean',"--clean", help='Cleans repository data, must be used with Development Environment Only', action="store_true")
    args_const.add_argument('-glogin',"--googleLogin", help='Log-in into Google Account', action="store_true")
    args_const.add_argument('-guserinfo',"--googleUserInfo", help='Provides Account Information for Logged In Google Account', action="store_true")

    args = args_const.parse_args()

    if(args.development):
      if(args.clean):
        try:
          shutil.rmtree(os.path.join('.',"Testing",'.usp'))
        except Exception as e: pass

      self.Development()
    else:
      # CHANGE THE CWD [CURRENT WORKING DIRECTORY] ARGUMENT, ALWAYS SPECIFY THIS ARGUMENT
      if(args.change_directory): os.chdir(args.change_directory)
      self.Production()

    self.LOAD_APP_INIT_DATA()

    if(args.googleLogin) :
      self.startGoogleLogin()
      self.getGoogleUserInfo()
      exit()

    if(args.googleUserInfo):
      self.getGoogleUserInfo()
      exit()

    self.LOAD_REPOSITORY_INIT_DATA()

    if(args.initialize):
      self.initialize()
      # self.REPOSITORY_SETTINGS = self.LOAD_REPOSITORY_SETTINGS()

    if(args.update):
      self.REPOSITORY_SETTINGS = self.LOAD_REPOSITORY_SETTINGS()
      self.update()

  def Production(self):
    USER_HOME_PATH = pathlib.Path.home()

    os.environ["APP_FOLDER_PATH"] = os.path.join(USER_HOME_PATH,".usp")

  def Development(self):
    os.environ["APP_FOLDER_PATH"] = os.path.join(os.getcwd(),'assets','installation','.usp') # APP's Main Folder, Where we are going to store App related Files

    os.chdir(os.path.join('.',"Testing"))

  def LOAD_APP_INIT_DATA(self):
    self.CCODES = self.LOAD_COMMUNICATION_CODES() # COMMUNICATION CODES
    self.APP_SETTINGS = self.LOAD_APP_SETTINGS() # APP SETTINGS

  def LOAD_REPOSITORY_INIT_DATA(self):
    # LOAD REPOSITORY SETTINGS
    self.REPOSITORY_PATH = os.path.join(self.APP_SETTINGS["repository_folderName"])

    self.REPOSITORY_SETTINGS_PATH = os.path.join(self.REPOSITORY_PATH,  self.APP_SETTINGS["repositorySettings_fileName"])
    self.REPOSITORY_LOG_FOLDER_PATH = os.path.join(self.REPOSITORY_PATH, self.APP_SETTINGS["log_folderName"])
    self.REPOSITORY_DATA_FOLDER_PATH = os.path.join(self.REPOSITORY_PATH, self.APP_SETTINGS["data_folderName"])
    self.REPOSITORY_DIR_DATA_PATH = os.path.join(self.REPOSITORY_PATH, self.APP_SETTINGS["repository_directoryData_fileName"])
    self.COMMIT_FILE_PATH = os.path.join(self.REPOSITORY_PATH,self.APP_SETTINGS["repository_commit_fileName"])

    # LOAD CLOUD_STORAGE CONFIGURATION, GID_FOLDER_PATH = GOOGLE DRIVE IDs will be stored
    self.REPOSITORY_CLOUD_STORAGE_FOLDER_PATH = os.path.join(self.REPOSITORY_PATH, self.APP_SETTINGS["repository_cloudData_folderName"])
    self.GID_FOLDER_PATH = os.path.join(self.REPOSITORY_CLOUD_STORAGE_FOLDER_PATH, self.APP_SETTINGS["repository_googleDriveID_folderName"])

  def LOAD_APP_SETTINGS(self):
    APP_SETTINGS_PATH = os.path.join(os.environ["APP_FOLDER_PATH"],"Appsetting.json")

    with open(APP_SETTINGS_PATH,"r") as file_:
        APP_SETTINGS = json.load(file_)

    return APP_SETTINGS

  def LOAD_REPOSITORY_SETTINGS(self):
    try:
      # LOAD REPOSITORY SETTINGS
      with open(self.REPOSITORY_SETTINGS_PATH,"r") as file_:
              REPOSITORY_SETTINGS = json.load(file_)

      output({"code":self.CCODES["REPO_SETTINGS_LOAD"],"msg":"Loaded Repository Settings"})
      return REPOSITORY_SETTINGS
    except OSError:
      print({"code": self.CCODES["PRE_INIT_REPOSITORY"],"msg":"First Initialize the Repository by passing -init or --initialize in Arguments"})

  def LOAD_COMMUNICATION_CODES(self):
      COMMUNICATION_CODES_FILE_PATH = os.path.join(os.environ["APP_FOLDER_PATH"],"Communication_Codes.json")
      # LOAD THE COMMUNICATION CODES
      with open(COMMUNICATION_CODES_FILE_PATH,"r") as file_:
          CCODES = json.load(file_)

      return CCODES

  # CREATE EMPTY FILES AND FOLDERS
  def PRE_initialize_repository(self):
      if(os.path.exists(self.REPOSITORY_PATH)):
          return {"code":self.CCODES["FOLDER_EXISTS"],"msg":"An Existing Repository Folder Already Exist"}

      try:
          os.mkdir(self.REPOSITORY_PATH)
          os.mkdir(self.REPOSITORY_DATA_FOLDER_PATH)
          os.mkdir(self.REPOSITORY_LOG_FOLDER_PATH)
          os.mkdir(self.REPOSITORY_CLOUD_STORAGE_FOLDER_PATH)
          os.mkdir(self.GID_FOLDER_PATH)

          with open(self.REPOSITORY_SETTINGS_PATH,"w") as file_:
              json.dump({'abs_path':os.getcwd()},file_)
              # json.dump({"directory":"./"},file_)

          with open(self.COMMIT_FILE_PATH,"w") as file_:
              json.dump({"total":0},file_)

      except Exception as e:
          return {"code":self.CCODES["ERROR"],"msg":e}

      return {"code":self.CCODES["PRE_INIT"], "msg":"Created Necessary Files and Folders inorder to run the App"}

  def commit(self,MD_FILE_INFO):
      COMMIT = None

      with open(self.COMMIT_FILE_PATH,"r") as file_:
          COMMIT = json.load(file_)

      # CHECK IF LATEST COMMIT EXIST , IF YES THEN MAKE IT PREVIOUS COMMIT INORDER TO MAKE CURRENT COMMIT the LATEST COMMIT, SRY IF MY GRAMMER IS SAD
      try:
          COMMIT["previous"] += [COMMIT["latest"]]
      except KeyError:
          pass

      self.createLOG(MD_FILE_INFO=MD_FILE_INFO)

      # UPDATE THE COMMIT DICT
      COMMIT["latest"] = {    "filePath":MD_FILE_INFO["filePath"],
                              "fileName":MD_FILE_INFO["fileName"],
                              "commitTime":str(int(time.time()))
                              }
      COMMIT["total"] += 1

      # WRITE THE LATEST COMMIT IN THE FILE
      with open(self.COMMIT_FILE_PATH,'w') as file_:
          json.dump(COMMIT,file_)

      output({"code":self.CCODES["COMMIT_DONE"],"data":COMMIT,"msg":"Commited Data Successfully"})

  def createLOG(self,MD_FILE_INFO):
      FILE_NAME = MD_FILE_INFO["fileName"] + self.APP_SETTINGS["log_fileExtension"]
      FILE_PATH = os.path.join(self.REPOSITORY_LOG_FOLDER_PATH,FILE_NAME)
      with open(FILE_PATH,"w") as file_:
          json.dump(MD_FILE_INFO,file_)

      output({"code":self.CCODES["LOG_CREATED"],"data":{"filePath":FILE_PATH},"msg":"Log Created Successfully"})
      return FILE_PATH

  def GEN_MetaData(self,showOutput=True,indent=None):
      ignores = self.LOAD_IGNORE_DATA()
      MD_FILE_NAME = str(int(time.time()))+self.APP_SETTINGS["data_fileExtension"]
      MD_ = generateMetaData( EXPORT_DIRECTORY=self.REPOSITORY_DATA_FOLDER_PATH,
                              FILE_NAME=MD_FILE_NAME,
                              REPOSITORY_PATH=self.REPOSITORY_PATH,
                              HASH="xxh3_64",
                              ignore=ignores)

      with open(os.path.join(self.REPOSITORY_DIR_DATA_PATH),'w') as RepositoryDirDataFile_:
        for outputData in MD_.generate(RepositoryDirDataFile_): continue
              # output_direct(f"{{\"code\":{tmp},\"data\":{{{outputData}}}}}")
              # output({"code":self.CCODES["FILE_DATA_CREATED"],"data":data})

      return MD_.getInfo()

  def LOAD_IGNORE_DATA(self):

      IGNORE_FILE_PATH_OUTSIDE_REPO = ".uspignore"
      IGNORE_FILE_PATH_INSIDE_REPO = os.path.join(self.REPOSITORY_PATH,".uspignore")
      ignores = self.APP_SETTINGS["defaultIgnores"]

      # JUST INCASE
      if not ignores: ignores = []

      # shut the fuck up...sry, my head is paining | it's a generator
      def generate_ignore(path_):
        if os.path.exists(path_):
          file_= open(path_,"r")
          for line in file_.readlines():
            line = line.strip()

            if line.startswith("./") or line.startswith(".\\"):
              line = os.path.normpath(line)

              if line.endswith('**'):
                if not os.path.exists(line[:-2]): line = None
                else: line = os.path.join('.',line)
              else:
                line = os.path.join(".",line)
                if not os.path.exists(line): line = None

            if line: yield line

          file_.close()

      ignores.extend([ignore for ignore in generate_ignore(IGNORE_FILE_PATH_INSIDE_REPO)])
      ignores.extend([ignore for ignore in generate_ignore(IGNORE_FILE_PATH_OUTSIDE_REPO)])

      if ignores: output({"code":self.CCODES["IGNORE_DATA_LOAD"],"msg":"Loaded Ignore Settings"})

      return ignores

  def Get_latest_commit_info(self):
      with open(self.COMMIT_FILE_PATH,"r") as file_:
          COMMIT = json.load(file_)

      return COMMIT["latest"]

  def Get_log(self,FILE_NAME):
      LOG_FILE_PATH = os.path.join(self.REPOSITORY_LOG_FOLDER_PATH,FILE_NAME+self.APP_SETTINGS["log_fileExtension"])
      with open(LOG_FILE_PATH,"r") as file_:
          LOG_FILE_INFO = json.load(file_)
      return LOG_FILE_INFO

  def LOAD_META_DATA_FILE(self,FILE_PATH):
      file_ = open(FILE_PATH,'r')
      data = json.load(file_)
      file_.close()
      return data

  def update(self):
      self.LOAD_REPOSITORY_SETTINGS()

      # GENERATE NEW META DATA
      NEW_FILE_INFO = self.GEN_MetaData(showOutput=False)

      NEW_FILE_HASH = generateFileHash(NEW_FILE_INFO["filePath"])

      LATEST_COMMIT_FILE = self.Get_latest_commit_info()

      LATEST_FILE_HASH = self.Get_log(LATEST_COMMIT_FILE["fileName"])["fileHash"]

      # IF BOTH HASHES ARE SIMILAR THEN REMOVE THE NEW GENERATED META DATA
      if(NEW_FILE_HASH==LATEST_FILE_HASH):
          os.remove(NEW_FILE_INFO["filePath"])
          output({"code":self.CCODES["NO_CHANGE"],"msg":"No Changes are Detected"})
      else:
          output({"code":self.CCODES["CHANGE_DETECTED"],"msg":"Changes Detected"})
          # COMMIT FIRST
          self.commit(MD_FILE_INFO=NEW_FILE_INFO)

          # CHANGES ARE DETECTED, NOW LATEST_COMMIT_FILE BECOMES OLD DATA AND NEWLY GENERATED META DATA BECOMES UPDATED DATA (use NEW_FILE_INFO["filePath"] to get new metadata file path)
          for CHANGES in self.detectChange(NEW_MD_FILE_PATH=NEW_FILE_INFO["filePath"],OLD_MD_FILE_PATH=LATEST_COMMIT_FILE["filePath"]):
              output(CHANGES)

  def detectChange(self,NEW_MD_FILE_PATH,OLD_MD_FILE_PATH):
      new_Data = self.LOAD_META_DATA_FILE(NEW_MD_FILE_PATH)
      old_Data = self.LOAD_META_DATA_FILE(OLD_MD_FILE_PATH)

      new_Data_FILE_PATHS = set(new_Data.keys())
      old_Data_FILE_PATHS = set(old_Data.keys())

      NEW_FILES = new_Data_FILE_PATHS.difference(old_Data_FILE_PATHS)
      DELETED_FILES = old_Data_FILE_PATHS.difference(new_Data_FILE_PATHS)


      del old_Data_FILE_PATHS

      # cFfilter means common File Hash Filter
      # cFHfilter = new_Data_FILE_PATHS - (NEW_FILES | DELETED_FILES) # "NEW_FILES | DELETED_FILES" <--- means two sets are combined
      cFHfilter = new_Data_FILE_PATHS - (NEW_FILES | DELETED_FILES)
      del new_Data_FILE_PATHS

      for filePath_ in NEW_FILES:
          yield {"code":self.CCODES["NEW_FILE_DETECTED"],"data":{"filePath":filePath_,"fileName":new_Data[filePath_]["fileName"]}}

      for filePath_ in DELETED_FILES:
          yield {"code":self.CCODES["DELETED_FILE_DETECTED"],"data":{"filePath":filePath_,"fileName":old_Data[filePath_]["fileName"]}}

      del NEW_FILES
      del DELETED_FILES

      # MODIFIED FILES
      for cHKey in cFHfilter:
          if old_Data[cHKey]["hash"] != new_Data[cHKey]["hash"]:
              yield {"code":self.CCODES["MODIFIED_FILE_DETECTED"],"data":{"filePath":cHKey,"fileName":new_Data[cHKey]["fileName"]}}

      del cFHfilter
      del new_Data
      del old_Data

  def initialize(self):
      # Checks if a Folder / Repo is already Initialized

      result = self.PRE_initialize_repository()

      if(result["code"]!=self.CCODES["PRE_INIT"]):
          output(result)
      else:
          # First Commit
          FILE_INFO = self.GEN_MetaData()
          self.commit(MD_FILE_INFO=FILE_INFO)

          currentPath = os.getcwd().replace('\\','/')

          output({"code":self.CCODES["INIT"],"msg":"Repository Initialization Completed","data":{"folderName":currentPath[currentPath.rindex('/')+1:],"localPath":currentPath}})

  def setGDriveService(self,service):
    self.Gservice = service

  def getGDriveService(self):
    if(self.Gservice): return self.Gservice
    else:
      service = GoogleDrive.get_gdrive_service(self.CCODES)
      self.setGDriveService(service)
      return service

  def startGoogleLogin(self):
    Gservice = GoogleDrive.startLogin(self.CCODES)
    if(Gservice): self.setGDriveService(Gservice)

  def getGoogleUserInfo(self):
    userInfo = GoogleDrive.getUSERInfo(self.CCODES,self.getGDriveService())
    output({"code":self.CCODES["GOOGLE_USER_INFO"],"msg":"Google User Data","data":userInfo})
    return userInfo

if __name__ == "__main__":
  App()

