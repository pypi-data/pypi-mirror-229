import base64
from pathlib import Path

import extra_streamlit_components as stx
import streamlit as st
from PIL import Image
import pickle

from app_pages import *


def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded


def img_to_html(img_path, width=500):
    img_html = f"<img src='data:image/png;base64,{img_to_bytes(img_path)}'  width='{width}px', class='img-fluid'>"
    return img_html


HERE = Path(__file__).parent.resolve()
icon_fname = HERE.joinpath("images/logo_mouse.png")
icon_img = Image.open(icon_fname)
# set webpage icon and layout
st.set_page_config(
    page_title="LUPE",
    page_icon=icon_img,
    layout="centered",
    menu_items={
    }
)
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.set_option('deprecation.showPyplotGlobalUse', False)
st.markdown(
    """
    <style>
    [data-testid="stSidebar"]{
        min-width: 320px;
        max-width: 320px;   
    }
    [data-testid="stSidebar"][aria-expanded="false"] {
        margin-left: -320px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.write('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

logo_fname = HERE.joinpath("images/logo.png")
st.markdown("<p style='text-align: center; color: grey; '>" +
            img_to_html(logo_fname, width=250) + "</p>",
            unsafe_allow_html=True)
logo_img = Image.open(logo_fname)

page_names = ['Home', 'Analyses', 'Pain-Scale']

chosen_id = stx.tab_bar(data=[
    stx.TabBarItemData(id=1, title=page_names[0], description="Model description"),
    stx.TabBarItemData(id=2, title=page_names[1], description="Descriptive stats"),
    stx.TabBarItemData(id=3, title=page_names[2], description="Composite score"),
], default=1)

with st.sidebar:
    # model initialization
    if 'classifier' not in st.session_state:
        model_name = HERE.joinpath('model/model.pkl')
        with open(model_name, 'rb') as fr:
            st.session_state['classifier'] = pickle.load(fr)
    # class names
    if 'annotated_behaviors' not in st.session_state:
        st.session_state['annotated_behaviors'] = ['still',
                                                   'walking',
                                                   'rearing',
                                                   'body groom L',
                                                   'genitalia groom R',
                                                   'body groom R',
                                                   'upright groom',
                                                   'genitalia groom',
                                                   'genitalia groom L',
                                                   'lick hindpaw L', 'lick hindpaw R']
    # csv files
    if 'num_condition' not in st.session_state:
        st.session_state['num_condition'] = None
    st.markdown(f" <h1 style='text-align: left; color: #EEEEEE; font-size:16px; "
                f"font-family:Avenir; font-weight:normal'>&nbspHow many conditions</h1> "
                , unsafe_allow_html=True)
    st.session_state['num_condition'] = st.number_input('How many conditions?', min_value=2, max_value=10, value=2,
                                                        label_visibility='collapsed')

    for n in range(st.session_state['num_condition']):
        if f'pose_condition_{n + 1}' not in st.session_state:
            st.session_state[f'pose_condition_{n + 1}'] = None
        if f'fnames_condition_{n + 1}' not in st.session_state:
            st.session_state[f'fnames_condition_{n + 1}'] = None
        if 'extracted' not in st.session_state:
            st.session_state.extracted = False
        st.divider()
        st.markdown(f" <h1 style='text-align: left; color: #EEEEEE; font-size:16px; "
                    f"font-family:Avenir; font-weight:normal'>&nbspCondition {n + 1}</h1> "
                    , unsafe_allow_html=True)

        with st.form(f"condition_{n + 1}", clear_on_submit=True):
            uploaded_csvs = st.file_uploader('Upload corresponding pose csv files',
                                             accept_multiple_files=True,
                                             type='csv',
                                             key=f'pose_{n + 1}',
                                             label_visibility='collapsed')
            if st.session_state[f'pose_condition_{n + 1}'] is None:
                submitted = st.form_submit_button("Upload")
                if submitted and uploaded_csvs is not None:
                    # csv
                    st.session_state[f'pose_condition_{n + 1}'] = uploaded_csvs
                    # filenames
                    st.session_state[f'fnames_condition_{n + 1}'] = [uploaded_csvs[i].name
                                                                     for i in range(len(uploaded_csvs))]
                    st.experimental_rerun()
            elif st.session_state[f'pose_condition_{n + 1}'] is not None:
                st.dataframe(st.session_state[f'fnames_condition_{n + 1}'])
                cleared = st.form_submit_button(":red[Delete]")
                if cleared:
                    st.session_state[f'pose_condition_{n + 1}'] = None
                    st.session_state[f'fnames_condition_{n + 1}'] = None
                    st.session_state[f'pie_{n + 1}'] = None
                    st.session_state[f'pie_table_{n + 1}'] = None
                    st.session_state[f'bar_{n + 1}'] = None
                    st.session_state[f'bar_table_{n+1}'] = None
                    st.session_state[f'dur_{n + 1}'] = None
                    st.session_state[f'dur_table_{n+1}'] = None
                    st.session_state[f'location_pred_{n + 1}'] = None
                    st.session_state[f'kine_pred_{n + 1}'] = None
                    st.session_state.extracted = False

                    st.experimental_rerun()


def main():
    st.markdown(f" <h1 style='text-align: left; color: #FFFFFF; font-size:18px; "
                f"font-family:Avenir; font-weight:normal'>"
                f"Introducing LUPE, the innovative no code website predicting pain behavior in mice. "
                f"With our platform, you can input pose and classify mice behavior inside the LUPE Box. "
                f"LUPE can further summarize a composite pain score for mice behavior."
                f"Best of all, LUPE runs without the need for a GPU. "
                f"With in-depth analysis and interactive visuals, "
                f"as well as downloadable CSVs for easy integration into your existing workflow, "
                f"Try LUPE today and unlock a new level of insights into animal behavior."
                , unsafe_allow_html=True)
    st.markdown(f" <h1 style='text-align: left; color: #EEEEEE; font-size:18px; "
                f"font-family:Avenir; font-weight:normal'>Select an example behavior</h1> "
                , unsafe_allow_html=True)
    selected_behavior = st.radio('Behaviors',
                                 options=st.session_state['annotated_behaviors'],
                                 index=0,
                                 horizontal=True,
                                 label_visibility='collapsed')

    _, mid_col, _ = st.columns([0.5, 1.5, 0.5])
    # display gif
    try:
        behav_viddir = HERE.joinpath('behavior_videos')
        mid_col.image(f'{behav_viddir}/{selected_behavior}.gif')
    except:
        pass
    bottom_cont = st.container()
    with bottom_cont:
        st.markdown("""---""")
        st.markdown(f" <h1 style='text-align: left; color: gray; font-size:16px; "
                    f"font-family:Avenir; font-weight:normal'>"
                    f"LUPE is developed by Alexander Hsu and Justin James</h1> "
                    , unsafe_allow_html=True)


if page_names[int(chosen_id) - 1] == 'Home':
    main()
elif page_names[int(chosen_id) - 1] == 'Analyses':
    analysis.main()
elif page_names[int(chosen_id) - 1] == 'Pain-Scale':
    st.markdown(f" <h1 style='text-align: left; color: #EEEEEE; font-size:24px; "
                f"font-family:Avenir; font-weight:normal'>UNDER CONSTRUCTION...</h1> "
                , unsafe_allow_html=True)
    bottom_cont = st.container()
    with bottom_cont:
        st.markdown("""---""")
        st.markdown(f" <h1 style='text-align: left; color: gray; font-size:16px; "
                    f"font-family:Avenir; font-weight:normal'>"
                    f"LUPE is developed by Alexander Hsu and Justin James</h1> "
                    , unsafe_allow_html=True)
