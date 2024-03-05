import streamlit as st

# 設定streamlit排版
st.set_page_config(layout="wide")

import pandas as pd
import allVariable
from dataframe import DataFrame
from EDAfull import EDAfull
from Visualization import Visualization
from EDAmin import EDAmin
from advice import advice
from codePage import codePage
from chat import chat

# # 初始化變數-資料集
# if 'df' not in st.session_state:
#     st.session_state.df = None
#     allVariable.df = st.session_state.df


    
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
        
        # 整個頁面拆成7:3的分布   
        col1, col2 = st.columns(spec=[0.7,0.3])
        
        # 左半部分col1(佔70%)
        with col1:
            tab1_1, tab1_2, tab1_3 = st.tabs(['Dataframe','EDA report','Visualization'])
            
            # Dataframe頁籤:表格呈現目前資料集
            with tab1_1: 
                DataFrame()
                # 提供下載資料的按鈕
                st.download_button(label="Download data as CSV", data=convert_df(allVariable.df), file_name='edited_df.csv', mime='text/csv')
                
            # EDA report頁籤，呈現完整report
            with tab1_2:
                EDAfull()
                    
            # Visualization頁籤，呈現可能會用到的三張圖，以及提供使用者自行拖拉產圖的介面
            with tab1_3:
                Visualization()
                
        # 右半部分col1(佔30%)   
        with col2:
            tab2_1, tab2_2 = st.tabs(['各特徵的分析','建議操作'])
            
            # 各特徵的分析:呈現各特徵欄位的EDA
            with tab2_1:
                EDAmin()
                    
            # 建議操作頁籤:呈現建議使用者的操作  
            with tab2_2:
                advice()
                        
        st.tabs(['Code'])
        codePage()
            
        st.tabs(['Prompt'])
        chat(allVariable.key)     
                
# 上傳檔案
def upload():
    st.file_uploader("上傳檔案", type=["csv", "xlsx", "json"],key='df')
    if st.session_state.df is not None:
        try:
            # 自動推斷檔案格式
            allVariable.df = pd.read_csv(st.session_state.df, encoding='utf-8') 
            
        except Exception as e:
            st.error(f"讀取檔案時發生錯誤: {e}")
    

@st.cache_resource
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')
        

if __name__ == "__main__":
    main()
    
# 虛擬環境 .\.env\Scripts\Activate  
# streamlit run main.py