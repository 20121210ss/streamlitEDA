import os
import streamlit as st
import pandas as pd

from ydata_profiling import ProfileReport 
from streamlit_pandas_profiling import st_profile_report
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from mitosheet.streamlit.v1 import spreadsheet
from mitosheet.enterprise.api.code_snippets_utils import create_success_return_obj, get_custom_code_snippets
from mitosheet.types import CodeSnippet, StepsManagerType

if 'df' not in st.session_state:
    st.session_state.df = None
    
if 'fullReport' not in st.session_state:
    st.session_state.fullReport = None
    
if 'minReport' not in st.session_state:
    st.session_state.minReport = None
    
if 'code' not in st.session_state:
    st.session_state.code = None

st.set_page_config(layout="wide")


Height=400

def setsheet():
    """
        預設情況下： new_dfs, code = spreadsheet()
            new_dfs: 資料表
            code: 對應產出的code
            
        ex : analysis = spreadsheet(return_type='analysis')
            analysis : 重新運行分析mitosheet會用到，回傳目前的mito資料表?
            selection :  mito中目前選取的儲存格
            code : 回傳目前執行的code
            dfs_list : 回傳目前的dataframe
    """
    

# 在主頁面上顯示的內容
def main():
    
    st.subheader("測試EDA程式")
    
    # 上傳檔案
    uploaded_file = st.file_uploader("上傳檔案", type=["csv", "xlsx", "json"])
    if uploaded_file is not None:
        try:
            # 自動推斷檔案格式
            st.session_state.df = pd.read_csv(uploaded_file, encoding='utf-8') 
            
        except Exception as e:
            st.error(f"讀取檔案時發生錯誤: {e}")
            
    if st.session_state.df is not None:    
        col1, col2 = st.columns(spec=[0.7,0.3])
        with col1:
            tab1_1, tab1_2, tab1_3 = st.tabs(['Dataframe','EDA report','Visualization'])
            with tab1_1:
                
                DataFrame()
            with tab1_2:
                EDAfullreport()
            with tab1_3:
                Visualization()
            
        with col2:
            tab2_1, tab2_2 = st.tabs(['EDA內容','建議操作'])
            with tab2_1:
                EDAminreport()
            with tab2_2:
                st.text("建議操作頁籤")
                with st.expander("建議操作如下", expanded=True):
                    st.write("建議操作1")
                    st.write("建議操作2")
                    st.write("建議操作3")
                    st.write("建議操作4")
                    st.write("建議操作5")
                
        tab1_4, tab1_5= st.tabs(['code','Prompt'])
        with tab1_4:
            st.text("code頁籤")
            st.code(st.session_state.code, language="python", line_numbers=True)
        with tab1_5:
            st.text("Prompt頁籤")
    

# 完整EDA報告
def EDAfullreport():
    
    if st.session_state.fullReport is not None:
        st_profile_report(st.session_state.fullReport,height=Height)
    else:
        if st.session_state.df is not None:
            # 創建 Profile 報告
            profile = ProfileReport(st.session_state.df)
            st.session_state.fullReport = profile
            st_profile_report(st.session_state.fullReport,height=Height)

# 簡單EDA報告
def EDAminreport():
    if st.session_state.minReport is not None:
        st_profile_report(st.session_state.minReport,height=Height)
    else:
        if st.session_state.df is not None:
            # 創建 Profile 報告
            profile = ProfileReport(st.session_state.df,minimal=True)
            st.session_state.minReport = profile
            st_profile_report(st.session_state.minReport,height=Height)

def remove_html_tags(input_text):
    soup = BeautifulSoup(input_text, 'html.parser')
    text_without_tags = soup.get_text()
    return text_without_tags

def splitChunk(input_text):
    delimiters = ["Overview", "Variables", "Interactions", "Correlations", "Missing values", "Sample", "Duplicate rows"]
    chunks = []

    for i in range(1, len(delimiters)):
        start_idx = input_text.find(delimiters[i], input_text.find(delimiters[i-1]))
        end_idx = input_text.find(delimiters[i], start_idx + 1)

        if start_idx != -1 and end_idx != -1:
            chunks.append(input_text[start_idx:end_idx].strip() + "RRRR")

    # 处理最后一个部分
    last_delimiter = delimiters[-1]
    last_start_idx = input_text.find(last_delimiter)
    if last_start_idx != -1:
        chunks.append(input_text[last_start_idx:].strip())

    return chunks

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
        # The second return value is Mito generated code
        # new_dfs, code = spreadsheet(st.session_state.df,key='df1')
        a , code = spreadsheet(st.session_state.df,key='df1')
        # selection = a.return_type='selection'
        st.write(a)
        # Display the code
        st.session_state.code=code
        
def Visualization():  
    if st.session_state.df is not None:
        # 顯示資料集的圖表
        st.subheader("資料集分佈圖")
        st.scatter_chart(st.session_state.df,height=Height)

if __name__ == "__main__":
    main()
    

# streamlit run tryStreamlit.py
# test="<h3 style='color:White'>上傳檔案</h3>"
# st.markdown(test, unsafe_allow_html=True)