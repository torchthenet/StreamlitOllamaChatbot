set STREAMLIT_APP=Chatbot.py
if exist "%USERPROFILE%\anaconda3\Scripts\activate.bat" (
    %USERPROFILE%\anaconda3\Scripts\activate.bat %USERPROFILE%\anaconda3 && streamlit run %STREAMLIT_APP%
) else (
    if exist "%USERPROFILE%\Documents\GitHub\StreamlitExamples\.venv\Scripts\activate.bat" (
        %USERPROFILE%\Documents\GitHub\StreamlitExamples\.venv\Scripts\activate.bat && streamlit run %STREAMLIT_APP%
    ) else (
        streamlit run %STREAMLIT_APP%
    )
)