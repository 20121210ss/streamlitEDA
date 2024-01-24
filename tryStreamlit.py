import os
import streamlit as st
import pandas as pd
from ydata_profiling import ProfileReport 
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from streamlit.components.v1 import html
from pygwalker.api.streamlit import StreamlitRenderer, init_streamlit_comm
from langchain.chat_models import ChatOpenAI

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
    if key is not None:
        upload()
    
    # 若使用者有上傳資料集
    if st.session_state.df is not None: 
        
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
                    
            # Visualization頁籤，呈現可能會用到的三張圖，以及提供使用者自行拖拉產圖的介面
            with tab1_3:
                st.write(predictThreePic(str(st.session_state.colList),key))
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
                    
            # 建議操作頁籤:呈現建議使用者的操作  
            with tab2_2:
                with st.expander("建議操作如下", expanded=True):
                    test = splitOneCol(st.session_state.selectCol)
                    test = remove_html_tags(test)
                    st.write(predictOneCol(test,key))

                
        tab1_4, tab1_5= st.tabs(['code','Prompt'])
        with tab1_4:
            # 创建一个空的占位符
            code_placeholder = st.empty()   
            # 显示代码内容
            code_placeholder.text("code內容")
            code_placeholder.code(st.session_state.outputCode, language="python", line_numbers=True)
            st.session_state.inputCode = st.text_area("輸入自行撰寫python code")
            if st.button("送出"):
                refreshCode(code_placeholder)
                
        with tab1_5:
            st.text("Prompt頁籤")
            
# 上傳檔案
def upload():
   
    uploaded_file = st.file_uploader("上傳檔案", type=["csv", "xlsx", "json"])
    if uploaded_file is not None:
        try:
            # 自動推斷檔案格式
            st.session_state.df = pd.read_csv(uploaded_file, encoding='utf-8') 
            
        except Exception as e:
            st.error(f"讀取檔案時發生錯誤: {e}")

# 重整code頁籤     
def refreshCode(cp):
    if st.session_state.inputCode is not None:
        st.session_state.outputCode = st.session_state.outputCode+"\n"+st.session_state.inputCode
        st.session_state.inputCode = ''
        cp.code(st.session_state.outputCode, language="python", line_numbers=True)

# 完整EDA報告
def reRunEDAfullreport():
    if st.session_state.df is not None:
        # 創建 Profile 報告
        profile = ProfileReport(st.session_state.df)
        st.session_state.fullReport = profile.to_html()
        html(st.session_state.fullReport,height=Height,scrolling=True)

# 各特徵欄位的EDA報告            
def reRunEDAminreport():
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
def predictOneCol(text,key):
    OPENAI_MODEL = "gpt-3.5-turbo"
    llm = ChatOpenAI(openai_api_key=key,model=OPENAI_MODEL)
    result = llm.predict("以下是我的資料集中其中一個特徵欄位的分析\n"+text+"\n可以幫我列點這個欄位可能可以做哪些資料前處理的操作嗎，若不需要進行的操作則不用列出")
    return result

# 預測前三個使用者可能會想看的資料視覺化圖
def predictThreePic(text,key):
    OPENAI_MODEL = "gpt-3.5-turbo"
    llm = ChatOpenAI(openai_api_key=key,model=OPENAI_MODEL)
    result = llm.predict("以下是我的資料集中的所有特徵欄位名稱\n"+text+"\n請列給我前三個使用者根據這個資料集，最想看到的資料視覺化圖示，直接列點給我就好，並且附上他的code")
    return result

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
        
        edited_df = st.data_editor(st.session_state.df,on_change=resetReport())
        st.session_state.df = edited_df

# 重新生成EDA Report
def resetReport():
    st.session_state.fullReport = None
    st.session_state.minReport = None
        
@st.cache_resource
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

        
# Establish communication between pygwalker and streamlit
init_streamlit_comm()

def Visualization():  
    if st.session_state.df is not None:
        # 顯示資料集的圖表
        st.subheader("資料集分佈圖")
        renderer = get_pyg_renderer(st.session_state.df)
        # Render your data exploration interface. Developers can use it to build charts by drag and drop.
        renderer.render_explore(width=740,height=900)

# pygwalker
@st.cache_resource
def get_pyg_renderer(daf) -> "StreamlitRenderer":
    df = daf
    # When you need to publish your app to the public, you should set the debug parameter to False to prevent other users from writing to your chart configuration file.
    return StreamlitRenderer(df, spec="./gw_config.json", debug=False)   

# 尚未完善的聊天功能
def chat():
    
     # 初始化對話session
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # 在應用程式重新運行時顯示歷史記錄中的聊天訊息
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if st.session_state.df is not None:
        # 接收使用者輸入
        if user_input := st.chat_input("請輸入欲對資料集執行的操作..."):
            # 將使用者的輸入加入紀錄
            st.session_state.messages.append({"role": "user", "content": user_input})
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(user_input)
            
            # Display assistant response
            with st.chat_message("assistant"):
                
                response = "Hi~ 復誦：" + user_input
                # st.write(pandas_ai.run(st.session_state.df, prompt='可以幫我列出前五列的內容嗎?'))
                
                # if os.path.isfile('temp_chart.png'):
                #     im = plt.imread('temp_chart.png')
                #     st.image(im)
                #     os.remove('temp_chart.png')
                
                if response is not None:
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    st.write("No response from the assistant.")
                    st.session_state.messages.append({"role": "assistant", "content": "No response from the assistant."})           
 
# 尚未完善的顯示聊天紀錄功能          
def display_messages(messages):
    # 显示所有消息
    ordered_messages = sorted(messages, key=lambda x: x["content"])
    for message in ordered_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
 
   
if __name__ == "__main__":
    main()
    
# streamlit run tryStreamlit.py
# 虛擬環境 .\.env\Scripts\Activate