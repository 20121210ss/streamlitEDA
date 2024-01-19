import os
import streamlit as st
import pandas as pd
from ydata_profiling import ProfileReport 
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from streamlit.components.v1 import html
from pygwalker.api.streamlit import StreamlitRenderer, init_streamlit_comm
from langchain.chat_models import ChatOpenAI

if 'df' not in st.session_state:
    st.session_state.df = None
    
if 'fullReport' not in st.session_state:
    st.session_state.fullReport = None
    
if 'minReport' not in st.session_state:
    st.session_state.minReport = None
    
if 'genCode' not in st.session_state:
    st.session_state.genCode = None

if 'QC' not in st.session_state:
    st.session_state.QC = "\n"
    
if 'cd' not in st.session_state:
    st.session_state.cd = None

if 'colList ' not in st.session_state:
    st.session_state.colList  = None

if 'selectCol' not in st.session_state:
    st.session_state.selectCol = None
    
if 'OneColReport' not in st.session_state:
    st.session_state.OneColReport = None

st.set_page_config(layout="wide")

i=1
Height=450
    
# 在主頁面上顯示的內容
def main():
    
    st.subheader("測試EDA程式")
    key = st.text_input('openAI key:')
    upload()
            
    if st.session_state.df is not None:    
        col1, col2 = st.columns(spec=[0.7,0.3])
        with col1:
            tab1_1, tab1_2, tab1_3 = st.tabs(['Dataframe','EDA report','Visualization'])
            with tab1_1:
                DataFrame()
                st.download_button(
                label="Download data as CSV",
                data=convert_df(st.session_state.df),
                file_name='edited_df.csv',
                mime='text/csv'
                )
            with tab1_2:
                if st.session_state.fullReport is not None:
                    html(st.session_state.fullReport,height=Height,scrolling=True)
                else:
                    reRunEDAfullreport()
                    
                if st.button("生成報告"):
                    st.session_state.fullReport = None

            with tab1_3:
                st.write(predictThreePic(str(st.session_state.colList),key))
                Visualization()
            
        with col2:
            tab2_1, tab2_2 = st.tabs(['EDA內容','建議操作'])
            with tab2_1:
                if st.session_state.minReport is not None:
                    if st.session_state.selectCol is not None:
                        reRunOneColEDAreport(st.session_state.selectCol)
                    else:
                        html(st.session_state.minReport,height=Height,scrolling=True)
                else:
                    reRunEDAminreport()
                if st.button("重新生成報告"):
                    st.session_state.minReport = None
                    
            with tab2_2:
                st.text("建議操作頁籤")
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
            code_placeholder.code(st.session_state.genCode, language="python", line_numbers=True)
            st.text_area("輸入自行撰寫python code",key='cd', on_change=inputCode(code_placeholder))
        with tab1_5:
            st.text("Prompt頁籤")

def upload():
     # 上傳檔案
    uploaded_file = st.file_uploader("上傳檔案", type=["csv", "xlsx", "json"])
    if uploaded_file is not None:
        try:
            # 自動推斷檔案格式
            st.session_state.df = pd.read_csv(uploaded_file, encoding='utf-8') 
            
        except Exception as e:
            st.error(f"讀取檔案時發生錯誤: {e}")
    
     
def inputCode(code_placeholder):
    if st.session_state.QC and st.session_state.cd and st.session_state.genCode is not None:
        st.session_state.QC = st.session_state.QC+st.session_state.cd+"\n"
        st.session_state.genCode += st.session_state.QC
        st.session_state.cd = ''
        code_placeholder.code(st.session_state.genCode, language="python", line_numbers=True)

# 完整EDA報告
def reRunEDAfullreport():
    if st.session_state.df is not None:
        # 創建 Profile 報告
        profile = ProfileReport(st.session_state.df)
        st.session_state.fullReport = profile.to_html()
        html(st.session_state.fullReport,height=Height,scrolling=True)
            
def reRunEDAminreport():
    if st.session_state.df is not None:    
        sr = '''<div class="row header">'''
        # 創建 Profile 報告
        profile = ProfileReport(st.session_state.df,minimal=True)
        st.session_state.minReport = profile.to_html()
        # 使用split方法切割字串
        split_result = st.session_state.minReport.split(sr)
        result = split_result[0]+sr+split_result[2]
        st.session_state.minReport = result
        html(result,height=Height,scrolling=True)

def reRunOneColEDAreport(selindex):
    if st.session_state.df is not None:
        sr12 = '''<div class="row spacing">'''
        sr2 = '''<div class=variable>'''
        
        split_result = result.split(sr12,2)
        result = split_result[0]+sr12+split_result[-1]
        split_result = result.split(sr2)
        result = split_result[0]+sr2+split_result[selindex+1]+sr2+split_result[-1]
        st.session_state.OneColReport = result
        html(result,height=Height,scrolling=True)
            
def remove_html_tags(input_text):
    soup = BeautifulSoup(input_text, 'html.parser')
    text_without_tags = soup.get_text()
    return text_without_tags

def splitOneCol(selindex):
    if selindex is not None:
        sr2 = '''<div class=variable>'''
        split_result = st.session_state.minReport.split(sr2)
        result = remove_html_tags(split_result[1])
    else:
        result="請點選要針對哪個特徵進行建議"
    return result

def predictOneCol(text,key):
    OPENAI_MODEL = "gpt-3.5-turbo"
    llm = ChatOpenAI(openai_api_key=key,model=OPENAI_MODEL)
    result = llm.predict("以下是我的資料集中其中一個特徵欄位的分析\n"+text+"\n可以幫我列點這個欄位可能可以做哪些資料前處理的操作嗎，若不需要進行的操作則不用列出")
    return result

def predictThreePic(text,key):
    OPENAI_MODEL = "gpt-3.5-turbo"
    llm = ChatOpenAI(openai_api_key=key,model=OPENAI_MODEL)
    result = llm.predict("以下是我的資料集中的所有特徵欄位名稱\n"+text+"\n請列給我前三個使用者根據這個資料集，最想看到的資料視覺化圖示，直接列點給我就好，並且附上他的code")
    return result

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
                
def display_messages(messages):
    # 显示所有消息
    ordered_messages = sorted(messages, key=lambda x: x["content"])
    for message in ordered_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

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
    
   
if __name__ == "__main__":
    main()
    

# streamlit run tryStreamlit.py
# test="<h3 style='color:White'>上傳檔案</h3>"
# st.markdown(test, unsafe_allow_html=True)
# 虛擬環境 .\.env\Scripts\Activate