import streamlit as st
import app
import about.app

st.set_page_config(page_title="PancakeSwap Prediction V2",
                   page_icon=None,
                   layout="wide", initial_sidebar_state="auto",
                   menu_items=None)

menu_list = {"app": "Bot App",
             "about": "About"}


def getAppCode(menu_id):
    global menu_list
    return menu_list.get(menu_id)


def main():
    selected_app = st.sidebar.selectbox("Main Menu",
                                        options=list(menu_list.keys()),
                                        format_func=lambda x: getAppCode(x))
    # st.header(getAppCode(selected_app))
    if selected_app == "app":
        app.main()
    elif selected_app == "about":
        about.app.main()

    # eval(selected_app + "()")


if __name__ == '__main__':
    main()
