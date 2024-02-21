import streamlit as st
import openai
from pandasai.llm import OpenAI
from pandasai import SmartDataframe
import os
import matplotlib.pyplot as plt
import allVariable

# prompt頁聊天功能
def chat(key):      
    if allVariable.df is not None:
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
                
                response, genCode = predictDF(user_input,key) 
                
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
    result2 = df.last_code_executed
    allVariable.df = df
    return result1,result2