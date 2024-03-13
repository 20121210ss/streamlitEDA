import streamlit as st
st.set_page_config(page_title="EDA App",layout="wide")

import allVariable 
import os
import matplotlib.pyplot as plt
import geopandas as gpd
import seaborn as sns
import pandas as pd

def codePage():
    
    # 大標
    st.subheader("自行編譯code🖥️")
    
    st.tabs(['code內容'])
    # 创建一个空的占位符
    code_placeholder = st.empty()
    ans_placeholder = st.empty()
    
    # 显示代码内容
    code_placeholder.code(allVariable.outputCode, language="python", line_numbers=True)
    ans_placeholder.write("")
         
    if st.button("新增資料集變數(若程式碼中需使用資料集時點選)"):
        allVariable.inputCode = allVariable.inputCode + "df"
    
    if st.button("新增結果變數(若希望程式碼回傳結果時點選，以儲存並顯示欲回傳的結果)"):
        allVariable.inputCode = allVariable.inputCode + "result"
    
    inputArea_placeholder = st.empty()
    inputArea_placeholder.text_area("輸入自行撰寫python code",allVariable.inputCode,key='inputCode')
    
    if st.button("送出"):
        refreshCode(code_placeholder,ans_placeholder,inputArea_placeholder)
    
    
# 重整code頁籤     
def refreshCode(code_placeholder,ans_placeholder,inputArea_placeholder):
    codeDict = {}
    if st.session_state.inputCode is not "":
        index = str(st.session_state.inputCode).find("df")
        if index != -1:
            try:
                cc = st.session_state.inputCode.replace("df","allVariable.df")
                exec(cc+"""\naa = allVariable.df""",globals(),codeDict)
                allVariable.df = codeDict['aa']
                tip = "# code執行成功"
            except Exception as e:
                tip = "# 無法執行,因:"+str(e)
            allVariable.outputCode = allVariable.outputCode+"\n"+tip+"\n"+st.session_state.inputCode+"\n"
            code_placeholder.code(allVariable.outputCode, language="python", line_numbers=True)
            
            try:
                ans = codeDict['result']
            except:
                ans = ""
            if ans is not "":
                ans_placeholder.write(ans)
            
        else:
            ans_placeholder.error("請針對資料集進行操作")

    allVariable.inputCode = ""
            
if allVariable.df is not None:
    codePage()
else:
    st.error("請匯入資料集")