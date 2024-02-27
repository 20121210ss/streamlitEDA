import streamlit as st
import allVariable

def DataFrame():
    
    featureChoice = st.empty()
    showData = st.empty()

    allVariable.colList = list(allVariable.df.columns)
    
    col = featureChoice.selectbox(
        "想了解哪個欄位",
        allVariable.colList,
        index=None,
        placeholder="選擇欲分析的特徵欄位"
    )
    allVariable.selectCol = col
    if allVariable.selectCol is not None:
        allVariable.selectCol = allVariable.colList.index(allVariable.selectCol)+1
    
    showData.data_editor(allVariable.df)
    # allVariable.df = edited_df
    
    