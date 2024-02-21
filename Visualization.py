import streamlit as st
from pygwalker.api.streamlit import StreamlitRenderer, init_streamlit_comm
import openai
import matplotlib.pyplot as plt
import geopandas as gpd
import seaborn as sns
import pandas as pd
import os
import re
import allVariable

def Visualization():
    if allVariable.ThreePicResult == None: 
        rel = predictThreePic(str(allVariable.colList),allVariable.key)
        allVariable.ThreePicResult = regularResponse(rel)

    if st.button("顯示預測產圖結果"):
        vs = st.container()
        for item in allVariable.ThreePicResult:
            vs.text(item[0])
            visualPic(item[1],vs)
            
    # 若覺得產圖不準確，可以輸入資料集的用途及特徵意義等，便於提升預測準確率
    # if st.button("重新產圖"):
    #     if hint is not None:
    #         rel = repredictThreePic(str(allVariablee.colList),key,hint)
    #         allVariable.ThreePicResult = regularResponse(rel)
    #     else:
    #         st.text("請輸入上方資料集用途，以提升預測結果")
                        
    Pyg()

# 預測前三個使用者可能會想看的資料視覺化圖
def predictThreePic(text,key):
    schema = """
        1. first plot is ... : can know what...
        plt.show()

        2. second plot is ... : can know what...
        plt.show()
        
        3. third plot is ... : can know what...
        plt.show()
    """
    CoT = f"""
        Step 1 - The user will provide you all of the feature in the dataset, Advice three data visualizations images that users most want to see
        Step 2 - Based on the Step 1, attach the code for how to generate the images in Python.
        Step 4 - Format the result from Step 2 like this schema:{schema}
        Step 4 - The dataframe is not call 'df', is call 'allVariable.df',from Step 3, Replace all 'df' with 'allVariable.df'
    """
    system = f"""You are a data scientist assistant. When given data write the data visualization advice and the proper code.
        Use the following step-by-step instructions to respond to user inputs.
        {CoT}
    """
    OPENAI_MODEL = "gpt-3.5-turbo"
    openai.api_key = key
    result = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": "All of the feature:\n"+text+"\nAdvice three data visualizations that users most want to see based on this dataset, and attach the code for how to generate the images in Python."},
        ],
        temperature=0,
    )
    return result.choices[0].message.content

# 若有資料集或特徵解釋，則一併丟入prompt以預測前三個資料視覺化圖
def repredictThreePic(colList,key,text):
    schema = """
        {describe data visualizations image1}

        {data visualizations image code1}

        {describe data visualizations image2}

        {data visualizations image code2}
        
        {describe data visualizations image3}

        {data visualizations image code3}
    """
    CoT = f"""
        Step 1 - The user will provide you with an introduction of dataset, learn from this introduction.
        Step 2 - The user will provide you all of the feature in the dataset, combine the introduction from Step 1, Advice three data visualizations images that users most want to see
        Step 3 - Based on the Step 3, attach the code for how to generate the images in Python.
        Step 4 - Format the result from Step 2 like this schema:{schema}
        Step 4 - The dataframe is not call 'df', is call 'allVariable.df',from Step 3, Replace all 'df' with 'allVariable.df'
    """
    # Step 5 - Translate the results of step 4 into Traditional Chinese.
    system = f"""You are a data scientist assistant. When given data write the data visualization advice and the proper code.
        Use the following step-by-step instructions to respond to user inputs.
        {CoT}
    """
    prompt = "Introduction of my dataset: " + text + ",\n"+  "All of the feature:\n"+colList+"\nAdvice three data visualizations that users most want to see based on this dataset, and attach the code for how to generate the images in Python."
    
    openai.api_key = key
    OPENAI_MODEL = "gpt-3.5-turbo"
    result = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )

    return str(result.choices[0].message.content)

# 執行產圖的程式碼，並顯示於前端
def visualPic(PicCode,vs):
    vs.code(PicCode)
    try:
        exec(PicCode)
        plt.savefig('temp_chart.png')
        im = plt.imread('temp_chart.png')
        vs.image(im,width=600)
        os.remove('temp_chart.png')
        plt.clf()
        
    except:
        vs.text("no pic")

# 透過正則化拆分回傳的結果，分為Code及敘述部分。
def regularResponse(ThreePic):
    # 使用正則表達式提取程式碼和描述
    pattern = re.compile(r'(\S.*?)[ \t]*```python(.*?)```', re.DOTALL)
    matches = pattern.findall(ThreePic)
        
    return matches


def Pyg():  
    if allVariable.df is not None:
        # 顯示資料集的圖表
        st.subheader("手動呈現資料集分佈")
        renderer = get_pyg_renderer(allVariable.df)
        # Render your data exploration interface. Developers can use it to build charts by drag and drop.
        renderer.render_explore(width=700,height=900)

# Establish communication between pygwalker and streamlit
init_streamlit_comm()

# pygwalker
@st.cache_resource
def get_pyg_renderer(daf) -> "StreamlitRenderer":
    df = daf
    # When you need to publish your app to the public, you should set the debug parameter to False to prevent other users from writing to your chart configuration file.
    return StreamlitRenderer(df, spec="./gw_config.json", debug=False)