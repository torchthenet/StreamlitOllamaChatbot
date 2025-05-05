# StreamlitOllamaChatbot

Streamlit interface for Ollama hosted LLM chatbot

Web based inteface for Ollama using Streamlit framework

Check the current version of Streamlit using: streamlit version

The latest release notes are [here](https://docs.streamlit.io/develop/quick-reference/release-notes)

Update Streamlit using instructions [here](https://docs.streamlit.io/knowledge-base/using-streamlit/how-upgrade-latest-version-streamlit)

## Installation

You must have a working version of Ollama installed

Install the latest version of Streamlit

Install version 0.3.3 of the ollama package.

$ pip install streamlit
$ pip install ollama==0.3.3

Download the files for the desired application, navigate to that directory, and execute

$ streamlit run ChatbotSimple.py

Note that newer versions of the ollama package do not provide default system messages for models, use a different data schema, and don't include the response metrics. For now, use the latest 0.3.x release instead of upgrading to the latest 0.4.x release. If you have an incompatible version, remove it using "pip uninstall ollama" and then "pip install ollama=0.3.3". Check your current version using "pip show ollama".

## ChatbotSimple

Basic chatbot using ollama models. Download the ChatbotSimple.py file.

## Chatbot

Increasingly complex chatbot with single session and multi-session chats. Includes a Wrangler module, providing basic data grooming for text. Requires Chatbot.py, ChatbotUtilities.py, and ChatbotWrangler.py files.

## ChatbotPages

Hold multiple conversations with Ollama models. Each page and each question may use a different LLM. Requires ChatbotPages.py, and ChatbotUtilities.py files.

## ChatbotTabs

Hold multiple conversations with Ollama models. Each tab and each question may use a different LLM. Incomplete.
