import streamlit as st
import sections.app
import sections.about
import sections.claim

menu_list = {"app": "Bot App",
             "claim": "Claim Rewards",
             "about": "About"}


def get_app_code(menu_id):
    global menu_list
    return menu_list.get(menu_id)


def main():
    selected_app = st.sidebar.selectbox("Main Menu",
                                        options=list(menu_list.keys()),
                                        format_func=lambda x: get_app_code(x))
    # st.header(getAppCode(selected_app))
    if selected_app == "app":
        sections.app.main()
    elif selected_app == "claim":
        sections.claim.main()
    elif selected_app == "about":
        sections.about.main()

    # eval(selected_app + "()")


if __name__ == '__main__':
    # st.set_page_config(page_title="PancakeSwap Prediction V2",
    #                    page_icon=None,
    #                    layout="wide",
    #                    initial_sidebar_state="auto",
    #                    menu_items=None)
    main()
