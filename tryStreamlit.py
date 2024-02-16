import os
import streamlit as st
import pandas as pd
from ydata_profiling import ProfileReport 
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from streamlit.components.v1 import html
from pygwalker.api.streamlit import StreamlitRenderer, init_streamlit_comm
import openai
from pandasai.llm import OpenAI
from pandasai import SmartDataframe
import re
import geopandas as gpd
import seaborn as sns 

OPENAI_MODEL = "gpt-3.5-turbo"

# 初始化變數-資料集
if 'df' not in st.session_state:
    st.session_state.df = None
    
# 初始化變數-完整EDA報告
if 'fullReport' not in st.session_state:
    st.session_state.fullReport = None
    
# 初始化變數-簡短EDA報告  
if 'minReport' not in st.session_state:
    st.session_state.minReport = None
    
# 初始化變數-輸出呈現的程式碼
if 'outputCode' not in st.session_state:
    st.session_state.outputCode = ""
    
# 初始化變數-使用者輸入的程式碼
if 'inputCode' not in st.session_state:
    st.session_state.inputCode = ""
    
# 初始化變數-資料集的所有特徵欄位
if 'colList ' not in st.session_state:
    st.session_state.colList  = None
    
# 初始化變數-使用者選擇要了解的一個欄位
if 'selectCol' not in st.session_state:
    st.session_state.selectCol = None
    
# 初始化變數-使用者選擇要了解的一個欄位的Report
if 'OneColReport' not in st.session_state:
    st.session_state.OneColReport = None
    
# 初始化變數-單一欄位的預測結果
if 'OneColresult' not in st.session_state:
    st.session_state.OneColresult = None
    
# 初始化變數-三張圖片的預測結果
if 'ThreePicResult' not in st.session_state:
    st.session_state.ThreePicResult = None
    
# 初始化對話session
if "messages" not in st.session_state:
    st.session_state.messages = []

# 設定streamlit排版
st.set_page_config(layout="wide")

# 設定固定高度(圖、表格、report皆可用)
Height=450
    
# 在主頁面上顯示的內容
def main():
    
    # 大標
    st.subheader("測試EDA程式")
    
    # 請使用者輸入openAI api key
    key = st.text_input('openAI key:')
    
    # 若使用者有輸入好key，才可以開始上傳資料集
    if key != "":
        upload()
    
    # 若使用者有上傳資料集
    if (st.session_state.df is not None) and (key is not None): 
        
        # 整個頁面拆成7:3的分布   
        col1, col2 = st.columns(spec=[0.7,0.3])
        
        # 左半部分col1(佔70%)
        with col1:
            tab1_1, tab1_2, tab1_3 = st.tabs(['Dataframe','EDA report','Visualization'])
            
            # Dataframe頁籤:表格呈現目前資料集
            with tab1_1: 
                DataFrame()
                # 提供下載資料的按鈕
                st.download_button(label="Download data as CSV", data=convert_df(st.session_state.df), file_name='edited_df.csv', mime='text/csv')
            
            # EDA report頁籤，呈現完整report
            with tab1_2:
                # 若以生成過報告，則調用生成好的報告
                if st.session_state.fullReport is not None:
                    html(st.session_state.fullReport,height=Height,scrolling=True)
                # 否則生成報告
                else:
                    reRunEDAfullreport()
                # 若user有更動資料集，點選以重新生成報告
                if st.button("生成報告"):
                    st.session_state.fullReport = None
                    reRunEDAfullreport()
                    
            # Visualization頁籤，呈現可能會用到的三張圖，以及提供使用者自行拖拉產圖的介面
            with tab1_3:
                if st.session_state.ThreePicResult == None: 
                    rel = predictThreePic(str(st.session_state.colList),key)
                    st.session_state.ThreePicResult = regularResponse(rel)

                if st.button("顯示預測產圖結果"):
                    vs = st.container()
                    for item in st.session_state.ThreePicResult:
                        vs.text(item[0])
                        visualPic(item[1],vs)
                
                # 若覺得產圖不準確，可以輸入資料集的用途及特徵意義等，便於提升預測準確率
                # if st.button("重新產圖"):
                #     if hint is not None:
                #         rel = repredictThreePic(str(st.session_state.colList),key,hint)
                #         st.session_state.ThreePicResult = regularResponse(rel)
                #     else:
                #         st.text("請輸入上方資料集用途，以提升預測結果")
                        
                Visualization()
                
                
        # 右半部分col1(佔30%)   
        with col2:
            tab2_1, tab2_2 = st.tabs(['各特徵的分析','建議操作'])
            
            # 各特徵的分析:呈現各特徵欄位的EDA
            with tab2_1:
                # 若已有各特徵的分析報告
                if st.session_state.minReport is not None:
                    # 已有各特徵的分析報告有點選單一欄位，則顯示該特徵欄位的EDA
                    if st.session_state.selectCol is not None:
                        reRunOneColEDAreport(st.session_state.selectCol)
                    # 已有報告未選欄位，則調用已有的分析報告
                    else:
                        html(st.session_state.minReport,height=Height,scrolling=True)
                        
                # 若沒有各特徵的分析報告，生成報告    
                else:
                    reRunEDAminreport()
                    
                # 若user有更動資料集，點選以重新生成報告
                if st.button("重新生成報告"):
                    st.session_state.minReport = None
                    reRunEDAminreport()
                    
            # 建議操作頁籤:呈現建議使用者的操作  
            with tab2_2:
                with st.expander("建議操作如下", expanded=True):
                    
                    if st.session_state.OneColresult is not None:
                        st.write(st.session_state.OneColresult)
                    else:
                        if st.session_state.selectCol is not None:
                            test = splitOneCol(st.session_state.selectCol)
                            test = remove_html_tags(test)
                            st.session_state.OneColresult = predictOneCol(st.session_state.selectCol,test,key)
                            regu = regularResponse(st.session_state.OneColresult)
                            part = str(regu[0]).split(":",1)
                            regu[0] = (str(part[1]), regu[0][1])
                            st.text(part[0])
                            for item in regu:
                                st.text(str(item[0]).replace(":"," "))
                                st.code(item[1])
                        else:
                            st.write("請選擇欲分析的欄位")
                            
                    if st.button("重新建議"):
                        st.session_state.OneColresult = None
                        
        st.tabs(['Code'])
        codePage()
            
        st.tabs(['Prompt'])
        chat(key)        
                
# 上傳檔案
def upload():
   
    uploaded_file = st.file_uploader("上傳檔案", type=["csv", "xlsx", "json"])
    if uploaded_file is not None:
        try:
            # 自動推斷檔案格式
            st.session_state.df = pd.read_csv(uploaded_file, encoding='utf-8') 
            
        except Exception as e:
            st.error(f"讀取檔案時發生錯誤: {e}")

def codePage():
    st.text("code內容")
    
    # 创建一个空的占位符
    code_placeholder = st.empty()
    ans_placeholder = st.empty()
    
    # 显示代码内容
    code_placeholder.code(st.session_state.outputCode, language="python", line_numbers=True)
    ans_placeholder.write("")
         
    if st.button("新增資料集變數(若程式碼中需使用資料集時點選)"):
        st.session_state.inputCode = st.session_state.inputCode + "df"
    
    if st.button("新增結果變數(若希望程式碼回傳結果時點選，以儲存並顯示欲回傳的結果)"):
        st.session_state.inputCode = st.session_state.inputCode + "result"
    
    inputArea_placeholder = st.empty()
    st.session_state.inputCode = inputArea_placeholder.text_area("輸入自行撰寫python code",st.session_state.inputCode)
    
    if st.button("送出"):
        refreshCode(code_placeholder,ans_placeholder)
    
# 重整code頁籤     
def refreshCode(code_placeholder,ans_placeholder):
    codeDict = {}
    if st.session_state.inputCode is not "":
        try:
            cc = st.session_state.inputCode.replace("df","st.session_state.df")
            exec(cc,globals(),codeDict)
            tip = "# code執行成功"
        except:
            tip = "# 無法執行"
        
        st.session_state.outputCode = st.session_state.outputCode+"\n"+tip+"\n"+st.session_state.inputCode+"\n"
        st.session_state.inputCode = ""
        code_placeholder.code(st.session_state.outputCode, language="python", line_numbers=True)
        
        try:
            ans = codeDict['result']
        except:
            ans = ""
        if ans is not "":
            ans_placeholder.write(ans)
     
# 完整EDA報告
def reRunEDAfullreport():
    if st.session_state.df is not None:
        try:
            # 創建 Profile 報告
            profile = ProfileReport(st.session_state.df)
            st.session_state.fullReport = profile.to_html()
            html(st.session_state.fullReport,height=Height,scrolling=True)
        except:
            st.text("完整報告出錯")

# 各特徵欄位的EDA報告            
def reRunEDAminreport():
    try:
        if st.session_state.df is not None:    
            # 創建 Profile 報告
            profile = ProfileReport(st.session_state.df,minimal=True)
            st.session_state.minReport = profile.to_html()
            
            # 使用split方法切割字串，僅保留顯示各變數分析的部分
            sr = '''<div class="row header">'''
            split_result = st.session_state.minReport.split(sr)
            result = split_result[0]+sr+split_result[2]
            st.session_state.minReport = result
            html(result,height=Height,scrolling=True)
    except:
        st.text("EDA簡略報告生成有誤")

# 單一欄位的EDA報告，欲輸入值為選擇第幾個特徵欄位
def reRunOneColEDAreport(selindex):
    if st.session_state.df is not None:
        # 使用split方法切割字串，以拆出單一特徵欄位的報告
        sr12 = '''<div class="row spacing">'''
        sr2 = '''<div class=variable>'''
        split_result = st.session_state.minReport.split(sr12,2)
        result = split_result[0]+sr12+split_result[-1]
        split_result = result.split(sr2)
        result = split_result[0]+sr2+split_result[selindex]+sr2+split_result[-1]
        st.session_state.OneColReport = result
        html(result,height=Height,scrolling=True)

# 移除HTML標籤，防止EDA進入prompt時文件過大           
def remove_html_tags(input_text):
    soup = BeautifulSoup(input_text, 'html.parser')
    text_without_tags = soup.get_text()
    return text_without_tags

# 清除不需要資料的單一欄位EDA，防止EDA進入prompt時文件過大
def splitOneCol(selindex):
    if selindex is not None:
        sr2 = '''<div class=variable>'''
        split_result = st.session_state.minReport.split(sr2)
        result = remove_html_tags(split_result[1])
    else:
        result="請點選要針對哪個特徵進行建議"
    return result

# 預測單一特徵欄位要進行那些前處理動作
def predictOneCol(selindex,text,key):
    sel = st.session_state.colList[selindex-1]
    schema = """
        {describe data processing operation1}

        {data processing code 1}

        {describe data processing operation2}
        
        {data processing code 2}
        
        {describe data processing operation3}
        
        {data processing code 3}
        ....
    """
    CoT = f"""
        Step 1 - The user will provide you with a feature report of Exploratory Data Analysis, summarize this text.
        Step 2 - Based on the summary from Step 1, list the data preprocessing operations and their Python codes.
        Step 3 - Format the result from Step 2 like this schema:{schema}
        Step 4 - The dataframe is not call 'df', is call 'st.session_state.df',from Step 3, Replace all 'df' with 'st.session_state.df'
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
    

# 預測前三個使用者可能會想看的資料視覺化圖
def predictThreePic(text,key):
    OPENAI_MODEL = "gpt-3.5-turbo"
    openai.api_key = key
    result = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a data scientist assistant. When given data and a query, write the proper code and create the proper visualization"},
            {"role": "user", "content": "我的資料集為st.session_state.df，以下是我的資料集中的所有特徵欄位名稱\n"+text+"\n請列給我使用者根據這個資料集，最想看到的三個資料視覺化圖示，並且附上他該如何在python產圖的code"},
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
        Step 4 - The dataframe is not call 'df', is call 'st.session_state.df',from Step 3, Replace all 'df' with 'st.session_state.df'
    """
    # Step 5 - Translate the results of step 4 into Traditional Chinese.
    system = f"""You are a data scientist assistant. When given data write the data visualization advice and the proper code.
        Use the following step-by-step instructions to respond to user inputs.
        {CoT}
    """
    prompt = "Introduction of my dataset: " + text + ",\n"+  "All of the feature:\n"+colList+"\nAdvice three data visualizations that users most want to see based on this dataset, and attach the code for how to generate the images in Python."
    
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

    OPENAI_MODEL = "gpt-3.5-turbo"
    openai.api_key = key
    result = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a data scientist assistant. When given data and a query, write the proper code and create the proper visualization"},
            {"role": "user", "content": "我的資料集為st.session_state.df，我的資料集簡介:"+text+"\n以下是我的資料集中的所有特徵欄位名稱\n"+colList+"\n請列給我使用者根據這個資料集，最想看到的三個資料視覺化圖示，並且附上他該如何在python產圖的code"},
        ],
        temperature=0,
    )
    return result.choices[0].message.content

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
    
# 資料集呈現
def DataFrame():
    if st.session_state.df is not None:
        st.session_state.colList = list(st.session_state.df.columns)
        col = st.selectbox(
            "想了解哪個欄位",
            st.session_state.colList,
            index=None,
            placeholder="選擇欲分析的特徵欄位"
        )
        st.session_state.selectCol = col
        if st.session_state.selectCol is not None:
            st.session_state.selectCol = st.session_state.colList.index(st.session_state.selectCol)+1
        
        edited_df = st.data_editor(st.session_state.df)
        st.session_state.df = edited_df
        
@st.cache_resource
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')
        
# Establish communication between pygwalker and streamlit
init_streamlit_comm()

# 圖示頁的呈現
def Visualization():  
    if st.session_state.df is not None:
        
        # 顯示資料集的圖表
        st.subheader("手動呈現資料集分佈")
        renderer = get_pyg_renderer(st.session_state.df)
        # Render your data exploration interface. Developers can use it to build charts by drag and drop.
        renderer.render_explore(width=700,height=900)

# pygwalker
@st.cache_resource
def get_pyg_renderer(daf) -> "StreamlitRenderer":
    df = daf
    # When you need to publish your app to the public, you should set the debug parameter to False to prevent other users from writing to your chart configuration file.
    return StreamlitRenderer(df, spec="./gw_config.json", debug=False)   

# prompt頁聊天功能
def chat(key):      
    if st.session_state.df is not None:
        user_input = st.chat_input("請輸入欲對資料集執行的操作...",)
        # 接收使用者輸入
        if user_input is not None:
            # 將使用者的輸入加入紀錄
            st.session_state.messages.append({"role": "user", "content": user_input})
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(user_input)
            
            # Display assistant response
            with st.chat_message("assistant"):
                
                response, genCode = predictDF(user_input,key) 
                
                if os.path.isfile('temp_chart.png'):
                    im = plt.imread('temp_chart.png')
                    st.image(im)
                    os.remove('temp_chart.png')
                
                if response is not None:
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    st.write("No response from the assistant.")
                    st.session_state.messages.append({"role": "assistant", "content": "No response from the assistant."})           
                
                if genCode is not None:
                    st.code(genCode)

# prompt頁詢問資料集
def predictDF(text,key):
    openai.api_key = key
    llm = OpenAI(api_token=key) 
    df = SmartDataframe(st.session_state.df, config={"llm": llm})
    result1 = df.chat("我的問題是:"+text+"\n可以幫我解答並給我對應操作的code嗎")
    result2 = df.last_code_executed
    st.session_state.df = df
    return result1,result2

if __name__ == "__main__":
    main()
    
# streamlit run tryStreamlit.py
# 虛擬環境 .\.env\Scripts\Activate