import streamlit as st
st.set_page_config(page_title="EDA App",layout="wide")

from streamlit.components.v1 import html
from ydata_profiling import ProfileReport
import re
from wordcloud import WordCloud
import allVariable

from bs4 import BeautifulSoup
import openai
import os
import matplotlib.pyplot as plt
import geopandas as gpd
import seaborn as sns
import pandas as pd
from main import getDataframe

df = None

wordcloud = WordCloud("C:\\Windows\\Fonts\\msyh.ttc")

def EDAmin():
    df = getDataframe()
    
    # 大標
    st.subheader("單一欄位處理🖋️")
    
    chooseCol()
    
    col1, col2 = st.columns(spec=[0.5,0.5])
    with col1:
        st.tabs(['該欄位的分析報告'])
        minreport = st.empty()
        
        with minreport :
            # 若已有各特徵的分析報告
            if allVariable.minReport is not None:
                if allVariable.OneColReport is not None:
                    html(allVariable.OneColReport,height=allVariable.Height,scrolling=True)
                # 已有各特徵的分析報告有點選單一欄位，則顯示該特徵欄位的EDA
                    if allVariable.selectCol is not None:
                        reRunOneColEDAreport(allVariable.selectCol)
                        html(allVariable.OneColReport,height=allVariable.Height,scrolling=True)
                    # 已有報告未選欄位，則調用已有的分析報告
                    else:
                        html(allVariable.minReport,height=allVariable.Height,scrolling=True)
                                
            # 若沒有各特徵的分析報告，生成報告    
            else:
                reRunEDAminreport(df)
                            
        # 若user有更動資料集，點選以重新生成報告
        if st.button("重新生成報告"):
            allVariable.minReport = None
            with minreport :
                reRunEDAminreport()
    with col2:
        st.tabs(['該欄位的建議操作如下'])       
        advice()

def chooseCol():
    featureChoice = st.empty()
    featureChoice.selectbox(
        "想了解哪個欄位",
        allVariable.colList,
        index=None,
        placeholder="選擇欲分析的特徵欄位",
        key='selectCol',
        on_change=reCol(),
    )
    
def reCol():
    try:
        allVariable.selectCol = st.session_state.selectCol
        if allVariable.selectCol is not None:
            allVariable.selectCol = allVariable.colList.index(allVariable.selectCol)+1
        reRunOneColEDAreport(allVariable.selectCol)
    except:
        pass

      
# 單一欄位的EDA報告，欲輸入值為選擇第幾個特徵欄位
def reRunOneColEDAreport(selindex):
    if allVariable.minReport is not None:
        # 使用split方法切割字串，以拆出單一特徵欄位的報告
        sr12 = '''<div class="row spacing">'''
        sr2 = '''<div class=variable>'''
        split_result = allVariable.minReport.split(sr12,2)
        result = split_result[0]+sr12+split_result[-1]
        split_result = result.split(sr2)
        result = split_result[0]+sr2+split_result[selindex]+sr2+split_result[-1]
        allVariable.OneColReport = result
        
# 各特徵欄位的EDA報告            
def reRunEDAminreport(df):
    try:
        if df is not None:    
            # 創建 Profile 報告
            profile = ProfileReport(df,minimal=True)
            allVariable.minReport = profile.to_html()
            
            # 使用split方法切割字串，僅保留顯示各變數分析的部分
            sr = '''<div class="row header">'''
            split_result = allVariable.minReport.split(sr)
            result = split_result[0]+sr+split_result[2]
            allVariable.minReport = result
            html(result,height=allVariable.Height,scrolling=True)
    except:
        st.text("EDA簡略報告生成有誤")

def advice():
    advice = st.empty()
    
    with advice.container(): 
        if allVariable.OneColresult is not None:
            arr = [item[0] for item in allVariable.OneColresult]
            st.radio("選擇欲執行的操作",arr,key='radio_item')
            if st.button("執行code"):
                index = arr.index(st.session_state.radio_item)
                tryCode(st.session_state.radio_item,allVariable.OneColresult[index][1])   

        else:
            if allVariable.selectCol is not None:
                reAdvice()
                arr = [item[0] for item in allVariable.OneColresult]
                st.radio("選擇欲執行的操作",arr,key='radio_item')
                if st.button("執行code"):
                    index = arr.index(st.session_state.radio_item)
                    tryCode(st.session_state.radio_item,allVariable.OneColresult[index][1])   
            else:
                advice.write("請選擇欲分析的欄位")
                    
    if st.button("重新建議"):
        advice.empty()
        with advice.container():
            reAdvice()
            arr = [item[0] for item in allVariable.OneColresult]
            st.radio("選擇欲執行的操作",arr,key='radio_item')
            if st.button("執行code"):
                index = arr.index(st.session_state.radio_item)
                tryCode(st.session_state.radio_item,allVariable.OneColresult[index][1])   


def reAdvice():
    test = splitOneCol(allVariable.selectCol)
    test = remove_html_tags(test)
    allVariable.OneColresult = predictOneCol(allVariable.selectCol,test,allVariable.key)
    allVariable.OneColresult = regularResponse(allVariable.OneColresult)
    
    
# 移除HTML標籤，防止EDA進入prompt時文件過大           
def remove_html_tags(input_text):
    soup = BeautifulSoup(input_text, 'html.parser')
    text_without_tags = soup.get_text()
    return text_without_tags

# 清除不需要資料的單一欄位EDA，防止EDA進入prompt時文件過大
def splitOneCol(selindex):
    if selindex is not None:
        sr2 = '''<div class=variable>'''
        split_result = allVariable.minReport.split(sr2)
        result = remove_html_tags(split_result[1])
    else:
        result="請點選要針對哪個特徵進行建議"
    return result

# 預測單一特徵欄位要進行那些前處理動作
def predictOneCol(selindex,text,key):
    OPENAI_MODEL = "gpt-3.5-turbo"
    sel = allVariable.colList[selindex-1]
    schema = """
        #Insert description of data processing operation1

        Insert the code of data processing operation1

        #Insert description of data processing operation2
        
        Insert the code of data processing operation2
        ....
    """+"""
for example:

#1. Remove missing value

```python(.*?)```
import pandas as pd

df = df.dropna()
...
"""
    CoT = f"""
        Step 1 - The user will provide you with a feature report of Exploratory Data Analysis, summarize this text.
        Step 2 - Based on the summary from Step 1, list the data preprocessing operations and their Python codes.
        Step 3 - Format the result from Step 2 like this schema:{schema}
        Step 4 - The dataframe is not call 'df', is call 'allVariable.df',from Step 3, Replace all 'df' with 'allVariable.df'
    """
    # Step 5 - Translate the results of step 4 into Traditional Chinese.
    system = f"""You are a data scientist assistant. When given data write the data processing advice and the proper code.
        Use the following step-by-step instructions to respond to user inputs.
        {CoT}
    """
    prompt = "Here is the analysis report of feature :" + sel + ",\n"+ text + "\nlist the data preprocessing operations and their Python codes."
    
    openai.api_key = key
    result = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )

    return str(result.choices[0].message.content)

# 透過正則化拆分回傳的結果，分為Code及敘述部分。
def regularResponse(ad):
    # 使用正則表達式提取程式碼和描述
    pattern = re.compile(r'(\S.*?)[ \t]*```python(.*?)```', re.DOTALL)
    matches = pattern.findall(ad)
        
    return matches

# 執行code     
def tryCode(aa,cc):
    codeDict = {}
    try:
        exec(cc+"""\ndt = allVariable.df""",globals(),codeDict)
        allVariable.df = codeDict['dt']
        tip = "code執行成功"
        st.warning(tip)
        cc = cc.replace("allVariable.df","df")
        aa = aa.replace("\n"," ")
        allVariable.outputCode = allVariable.outputCode+"\n# "+tip+"\n"+aa+cc
    except Exception as e:
        tip = "無法執行,因:"+str(e)
        st.error(tip)
        st.code(cc)

if allVariable.df is not None:
    EDAmin()
else:
    st.error("請匯入資料集")
    