import streamlit as st
st.set_page_config(layout="wide")

import pandas as pd
import allVariable
from main import getDataframe,setMyDataframe

df = None

def preprocessing():
    
    df = getDataframe()
    
    # 大標
    st.subheader("簡易資料處理☑️")
    
    col1, col2 = st.columns(spec=[0.7,0.3])
    with col1:
        st.tabs(['資料集'])
        show = st.empty()
        show.data_editor(df)

    with col2:
        st.tabs(['前處理動作'])
                
        with st.expander("填補遺漏值"):
            missingList = df.isnull().any()
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
            
        with st.expander("刪除遺漏值"):
            if st.button("執行", disabled=allVariable.deleteRun):
                delete_MissingValue()
                allVariable.deleteRun = True
                
        with st.expander("處理離群值"):
            outlierList = df.select_dtypes(include=['int', 'float']).columns.tolist()
            st.selectbox(
                "選擇欲處理離群值的特徵欄位",
                outlierList,
                index=None,
                key='outlierCol',
            )
            
            st.radio("請選擇透過何種方式修改離群值",["平均值","中位數","眾數","向前填充","向後填充"],key="change")
            if st.button("透過"+str(st.session_state.change)+"來修改離群值"):
                change_outlier(st.session_state.outlierCol,st.session_state.change)
        
        with st.expander("新增欄位"):
            st.selectbox(
                "選擇新欄位的來源欄位",
                allVariable.colList,
                index=None,
            )                
                
def delete_MissingValue():
    codeDict = {}
    code = """df = allVariable.df.dropna(axis=0)"""
    try:
        exec(code,globals(),codeDict)
        setMyDataframe(codeDict['df'])
        st.success("已成功刪除遺漏值")
        code = code.replace("allVariable.df","df")
        allVariable.outputCode += "\n"+"# 刪除遺漏值"+"\n"+code
        st.session_state.deleteRun = True
    except Exception as e:
        st.error("無法執行，因:"+str(e))
        
def fill_MissingValue(column):
    if str(st.session_state.fill) == "平均值":
        code = f"""mean = allVariable.df['{column}'].mean()\ndf = allVariable.df['{column}'].fillna(mean)"""

    elif str(st.session_state.fill) == "中位數":
        code = f"""median = allVariable.df['{column}'].median()\ndf = allVariable.df['{column}'].fillna(median)"""
        
    elif str(st.session_state.fill) == "眾數":
        code = f"""mode = allVariable.df['{column}'].mode()\ndf = allVariable.df['{column}'].fillna(mode)"""
        
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
    
def change_outlier(column,howto):
    
    code = f"""
# 找到 {column} 欄位的平均值和標準差
mean = allVariable.df['{column}'].mean()
std_dev = allVariable.df['{column}'].std()

# 計算上下限
lower_limit = mean - 3 * std_dev
upper_limit = mean + 3 * std_dev

# 找到超出上下限的離群值
outliers = allVariable.df[(allVariable.df['{column}'] < lower_limit) | (allVariable.df['{column}'] > upper_limit)]

"""    
    if str(howto) == "平均值":
        code += f"""
# 計算平均值
mean = allVariable.df['{column}'].mean()

# 將離群值替換為{howto}
for index, row in outliers.iterrows():
    allVariable.df.at[index, '{column}'] = mean

df = allVariable.df
"""

    elif str(howto) == "中位數":
        code += f"""
# 計算中位數
median = allVariable.df['{column}'].median()

# 將離群值替換為{howto}
for index, row in outliers.iterrows():
    allVariable.df.at[index, '{column}'] = median

df = allVariable.df
"""     

    elif str(howto) == "眾數":
        code += f"""
# 計算眾數
mode = allVariable.df['{column}'].mode()

# 將離群值替換為{howto}
for index, row in outliers.iterrows():
    allVariable.df.at[index, '{column}'] = mode

df = allVariable.df
"""
            
    codeDict = {}
    try:
        exec(code,globals(),codeDict)
        setMyDataframe(codeDict['df'])
        st.success("已成功修改離群值")
        code = code.replace("allVariable.df","df")
        allVariable.outputCode += "\n"+f"# 透過{str(howto)}修改特徵{column}的離群值"+"\n"+code
    except Exception as e:
        st.error("無法執行，因:"+str(e))

if allVariable.df is not None:
    preprocessing()
else:
    st.error("請匯入資料集")


    