import streamlit as st
st.set_page_config(page_title="EDA App",layout="wide")

import allVariable

def download():
    
    # 大標
    st.subheader("匯出🗳️")
    
    showData = st.empty()
    showData.data_editor(allVariable.df)
    
    # 提供下載資料的按鈕
    st.download_button(label="Download data as CSV", data=convert_df(allVariable.df), file_name='edited_df.csv', mime='text/csv')
         
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')
        
if allVariable.df is not None:
    download()
else:
    st.error("請匯入資料集")

    
    
    