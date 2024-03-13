import streamlit as st
st.set_page_config(layout="wide")

import pandas as pd
import allVariable

def preprocessing():
    
    # 大標
    st.subheader("簡易資料處理☑️")
    
    col1, col2 = st.columns(spec=[0.7,0.3])
    with col1:
        st.tabs(['資料集'])
        show = st.empty()
        show.data_editor(allVariable.df)

    with col2:
        st.tabs(['前處理動作'])
        with st.expander("刪除遺漏值"):
            if st.button("執行", disabled=allVariable.deleteRun):
                delete_MissingValue()
                allVariable.deleteRun = True
                
        with st.expander("填補遺漏值"):
            missingList = allVariable.df.isnull().any()
            missingList = missingList[missingList].index.tolist()
            st.selectbox(
                "選擇欲填補遺漏值的特徵欄位",
                missingList,
                index=None,
                key='fillcol',
            )
            
            st.radio("請選擇透過何種方式填補",["平均值","中位數","眾數","向前填充","向後填充"],key="fill")
            if st.button("透過"+str(st.session_state.fill)+"來填補遺漏值"):
                fill_MissingValue(st.session_state.fillcol)
                
def delete_MissingValue():
    codeDict = {}
    code = """df = allVariable.df.dropna(axis=0)"""
    try:
        exec(code,globals(),codeDict)
        allVariable.df = codeDict['df']
        st.success("已成功刪除遺漏值")
        code = code.replace("allVariable.df","df")
        allVariable.outputCode += "\n"+"# 刪除遺漏值"+"\n"+code
        st.session_state.deleteRun = True
    except Exception as e:
        st.error("無法執行，因:"+str(e))
        
def fill_MissingValue(column):
    if str(st.session_state.fill) == "平均值":
        mean = allVariable.df[column].mean()
        code = f"""df = allVariable.df['{column}'].fillna({mean})"""

    elif str(st.session_state.fill) == "中位數":
        median = allVariable.df[column].median()
        code = f"""df = allVariable.df['{column}'].fillna({median})"""
        
    elif str(st.session_state.fill) == "眾數":
        mode = allVariable.df[column].mode()
        code = f"""df = allVariable.df['{column}'].fillna({mode})"""
        
    elif str(st.session_state.fill) == "向前填充":
        code = f"""df = allVariable.df['{column}'].fillna(method='ffill')"""
        
    elif str(st.session_state.fill) == "向後填充":
        code = f"""df = allVariable.df['{column}'].fillna(method='bfill')"""
    
    codeDict = {}
    try:
        exec(code,globals(),codeDict)
        allVariable.df[column] = codeDict['df']
        st.success("已成功填補遺漏值")
        code = code.replace("allVariable.df","df")
        allVariable.outputCode += "\n"+f"# 透過{str(st.session_state.fill)}填補特徵{column}的遺漏值"+"\n"+code
    except Exception as e:
        st.error("無法執行，因:"+str(e))
    

if allVariable.df is not None:
    preprocessing()
else:
    st.error("請匯入資料集")


    