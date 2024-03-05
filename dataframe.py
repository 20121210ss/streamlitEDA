import streamlit as st
import allVariable

def DataFrame():
    
    featureChoice = st.empty()
    showData = st.empty()
    
    if allVariable.df is not None:
        showData.data_editor(allVariable.df)
        
        allVariable.colList = list(allVariable.df.columns)
        
        featureChoice.selectbox(
            "想了解哪個欄位",
            allVariable.colList,
            index=None,
            placeholder="選擇欲分析的特徵欄位",
            key='selectCol',
            on_change=reCol(),
        )
        
def reCol():
    try:
        allVariable.selectCol = st.session_state.selectCol
        if allVariable.selectCol is not None:
            allVariable.selectCol = allVariable.colList.index(allVariable.selectCol)+1
    except:
        pass
    
    
    