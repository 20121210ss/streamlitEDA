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
    if (allVariable.df is not None) and (allVariable.key is not None): 
        
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
   
    uploaded_file = st.file_uploader("上傳檔案", type=["csv", "xlsx", "json"])
    if uploaded_file is not None:
        try:
            # 自動推斷檔案格式
            allVariable.df = pd.read_csv(uploaded_file, encoding='utf-8') 
            
        except Exception as e:
            st.error(f"讀取檔案時發生錯誤: {e}")

@st.cache_resource
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')
        

if __name__ == "__main__":
    main()
    
# streamlit run main.py
# 虛擬環境 .\.env\Scripts\Activate