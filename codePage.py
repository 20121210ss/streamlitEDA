import streamlit as st
import allVariable 
from dataframe import DataFrame
import os
import matplotlib.pyplot as plt
import geopandas as gpd
import seaborn as sns
import pandas as pd

def codePage():
    st.text("code內容")
    
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
    allVariable.inputCode = inputArea_placeholder.text_area("輸入自行撰寫python code",allVariable.inputCode)
    
    if st.button("送出"):
        refreshCode(code_placeholder,ans_placeholder,inputArea_placeholder)
    
    
# 重整code頁籤     
def refreshCode(code_placeholder,ans_placeholder,inputArea_placeholder):
    codeDict = {}
    if allVariable.inputCode is not "":
        index = str(allVariable.inputCode).find("df")
        if index != -1:
            try:
                cc = allVariable.inputCode.replace("df","allVariable.df")
                exec(cc+"""\naa = allVariable.df""",globals(),codeDict)
                allVariable.test = codeDict['aa']
                st.write(codeDict)
                tip = "# code執行成功"
            except:
                tip = "# 無法執行"
            allVariable.outputCode = allVariable.outputCode+"\n"+tip+"\n"+allVariable.inputCode+"\n"
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
            
