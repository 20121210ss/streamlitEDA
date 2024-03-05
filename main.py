import streamlit as st
import pandas as pd
import allVariable
from st_pages import Page, show_pages, add_page_title

# 初始化變數-資料集
if 'df' not in st.session_state:
    st.session_state.df = None
    allVariable.df = st.session_state.df

# 初始化變數-完整EDA報告
if 'fullReport' not in st.session_state:
    st.session_state.fullReport = None
    allVariable.fullReport = st.session_state.fullReport
    
# 初始化變數-簡短EDA報告  
if 'minReport' not in st.session_state:
    st.session_state.minReport = None
    allVariable.minReport = st.session_state.minReport
    
# 初始化變數-輸出呈現的程式碼
if 'outputCode' not in st.session_state:
    st.session_state.outputCode = ""
    allVariable.outputCode = st.session_state.outputCode
    
# 初始化變數-使用者輸入的程式碼
if 'inputCode' not in st.session_state:
    st.session_state.inputCode = ""
    allVariable.inputCode = st.session_state.inputCode
    
# 初始化變數-資料集的所有特徵欄位
if 'colList ' not in st.session_state:
    st.session_state.colList  = None
    allVariable.colList = st.session_state.colList
    
# 初始化變數-使用者選擇要了解的一個欄位的Report
if 'OneColReport' not in st.session_state:
    st.session_state.OneColReport = None
    allVariable.OneColReport = st.session_state.OneColReport
    
# 初始化變數-單一欄位的預測結果
if 'OneColresult' not in st.session_state:
    st.session_state.OneColresult = None
    allVariable.OneColresult = st.session_state.OneColresult
    
# 初始化變數-三張圖片的預測結果
if 'ThreePicResult' not in st.session_state:
    st.session_state.ThreePicResult = None
    allVariable.ThreePicResult  = st.session_state.ThreePicResult 
    
# 初始化對話session
if "messages" not in st.session_state:
    st.session_state.messages = []
    allVariable.messages = st.session_state.messages

show_pages(
    [
        Page("main.py", "資料集", "🏠"),
        Page("EDAfull.py", "完整分析報告", "📖"),
        Page("preprocessing.py", "簡易資料處理", "☑️"),
        Page("EDAmin.py", "單一欄位處理", "🖋️"),
        Page("chat.py", "AI對話", "🗨️"),
        Page("codePage.py", "自行編譯code", "🖥️"),
        Page("download.py", "匯出", "🗳️"),
    ]
)

# app to add indendation in the sidebar
add_page_title(page_title="EDA App", layout="wide")

# 在主頁面上顯示的內容
def main():

    # 大標
    st.subheader("測試EDA程式")
    
    # 請使用者輸入openAI api key
    allVariable.key = st.text_input('openAI key:')
    
    # 若使用者有輸入好key，才可以開始上傳資料集
    if allVariable.key != "":
        upload()
    
    # 若使用者有上傳資料集
    if allVariable.df is not None: 
        showData = st.empty()
        showData.data_editor(allVariable.df) 
        allVariable.colList = list(allVariable.df.columns)         
                
# 上傳檔案
def upload():
    st.file_uploader("上傳檔案", type=["csv", "xlsx", "json"],key='df')
    if st.session_state.df is not None:
        try:
            # 自動推斷檔案格式
            allVariable.df = pd.read_csv(st.session_state.df, encoding='utf-8') 
            
        except Exception as e:
            st.error(f"讀取檔案時發生錯誤: {e}")
    
if __name__ == "__main__":
    main()
    
# 虛擬環境 .\.env\Scripts\Activate  
# streamlit run main.py