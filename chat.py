import streamlit as st
st.set_page_config(page_title="EDA App",layout="wide")
import pandas as pd
import openai
from pandasai.llm import OpenAI
import pandasai
from pandasai import SmartDataframe
import os
import matplotlib.pyplot as plt
import allVariable

# prompt頁聊天功能
def chat():      
    if allVariable.df is not None:
        # 显示对话记录
        for message in allVariable.messages:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(message["content"])
            elif message["role"] == "assistant":
                with st.chat_message("assistant"):
                    st.markdown(message["content"])
                    
        user_input = st.chat_input("請輸入欲對資料集執行的操作...",)
        # 接收使用者輸入
        if user_input is not None:
            # 將使用者的輸入加入紀錄
            allVariable.messages.append({"role": "user", "content": user_input})
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(user_input)
            
            # Display assistant response
            with st.chat_message("assistant"):
                response, genCode = predictDF(user_input,allVariable.key) 
                
                if isinstance(response,pandasai.smart_dataframe.SmartDataframe):
                    allVariable.df = pd.DataFrame(response)
                    joinAllCode(user_input,"為資料集所示",genCode)
                else:
                    joinAllCode(user_input,response,genCode)
                
                if os.path.isfile('temp_chart.png'):
                    im = plt.imread('temp_chart.png')
                    st.image(im)
                    os.remove('temp_chart.png')
                
                if response is not None:
                    st.write(response)
                    allVariable.messages.append({"role": "assistant", "content": response})
                else:
                    st.write("No response from the assistant.")
                    allVariable.messages.append({"role": "assistant", "content": "No response from the assistant."})           
                
                if genCode is not None:
                    st.code(genCode)

# prompt頁詢問資料集
def predictDF(text,key):
    openai.api_key = key
    llm = OpenAI(api_token=key) 
    df = SmartDataframe(allVariable.df, config={"llm": llm})
    result1 = df.chat("我的問題是:"+text+"\n可以幫我解答並給我對應操作的code嗎")
    result2 = splitCode(df.last_code_executed)
    return result1,result2

def splitCode(code):
    cc = code.split('"""')
    code = cc[2].split('return')
    code = code[0].replace('\n','').replace(' ','')
    return code
    
def joinAllCode(question,result,code):
    question = "#提問："+str(question)
    result = "#答案："+str(result)
    allVariable.outputCode = allVariable.outputCode+"\n"+question+"\n"+result+"\n"+str(code)+"\n"
    
    

if allVariable.df is not None:
    chat()
else:
    st.error("請匯入資料集")