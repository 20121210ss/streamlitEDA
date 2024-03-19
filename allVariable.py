import streamlit as st

# 設定固定高度(圖、表格、report皆可用)
Height=1100

# 初始化變數-資料集
df = None

# 此次上傳過資料了嗎
isUpload = False

# 初始化變數-OpenAI key
key = ""

# 此次輸入過key了嗎
isKey = False
    
# 初始化變數-完整EDA報告
fullReport = None
    
# 初始化變數-簡短EDA報告  
minReport = None
    
# 初始化變數-輸出呈現的程式碼
outputCode = ""
    
# 初始化變數-使用者輸入的程式碼
inputCode = ""
    
# 初始化變數-資料集的所有特徵欄位
colList  = None
    
# 初始化變數-使用者選擇要了解的一個欄位
selectCol = None
    
# 初始化變數-使用者選擇要了解的一個欄位的Report
OneColReport = None
    
# 初始化變數-單一欄位的預測結果
OneColresult = None
    
# 初始化變數-三張圖片的預測結果
ThreePicResult = None
    
# 初始化對話session
messages = []

# 初始化開關，是否進行過刪除遺漏值
deleteRun = False


def setDataframe(new_df):
   global df 
   df = new_df
    
@st.cache_resource
def getDataframe():
    return df





