import streamlit as st
from bs4 import BeautifulSoup
import openai
import re
import allVariable
import os
import matplotlib.pyplot as plt
import geopandas as gpd
import seaborn as sns
import pandas as pd

def advice():
    st.text("建議操作如下")
    advice = st.empty()
    
    with advice.container(): 
        if allVariable.OneColresult is not None:
            arr = [item[0] for item in allVariable.OneColresult]
            selected_item = st.radio("選擇欲執行的操作",arr)
            if st.button("執行code"):
                index = arr.index(selected_item)
                tryCode(selected_item,allVariable.OneColresult[index][1])   

        else:
            if allVariable.selectCol is not None:
                reAdvice()
                arr = [item[0] for item in allVariable.OneColresult]
                selected_item = st.radio("選擇欲執行的操作",arr)
                if st.button("執行code"):
                    index = arr.index(selected_item)
                    tryCode(selected_item,allVariable.OneColresult[index][1])   
            else:
                advice.write("請選擇欲分析的欄位")
                    
    if st.button("重新建議"):
        advice.empty()
        with advice.container():
            reAdvice()
            arr = [item[0] for item in allVariable.OneColresult]
            selected_item = st.radio("選擇欲執行的操作",arr)
            if st.button("執行code"):
                index = arr.index(selected_item)
                tryCode(selected_item,allVariable.OneColresult[index][1])   


def reAdvice():
    test = splitOneCol(allVariable.selectCol)
    test = remove_html_tags(test)
    allVariable.OneColresult = predictOneCol(allVariable.selectCol,test,allVariable.key)
    allVariable.OneColresult = regularResponse(allVariable.OneColresult)
    # part = str(allVariable.OneColresult[0]).split(":",1)
    # part = str(part[1]).split(",",1)
    # part[0] = str(part[0]).replace('"',"").replace('\\n',"").replace("'","")
    # allVariable.OneColresult[0] = (f"{part[0]}",allVariable.OneColresult[0][1])
    
    
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
        <#Insert description of data processing operation1>

        <Insert the code of data processing operation1>

        <#Insert description of data processing operation2>
        
        <Insert the code of data processing operation2>
        ....
    """+"""
for example:

#Remove missing value

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
        tip = "# code執行成功"
        st.warning("ok")
    except Exception:
        tip = "# 無法執行"
        st.warning("no\n"+Exception)
        
    cc = cc.replace("allVariable.df","df")
    aa = aa.replace("\n"," ")
    allVariable.outputCode = allVariable.outputCode+"\n"+tip+"\n"+aa+cc
    
    st.text(codeDict['dt'])
    