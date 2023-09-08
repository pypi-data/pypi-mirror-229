import streamlit as st
from utils.import_utils import *
from utils.visuals_utils import *
from stqdm import stqdm


def prompt_setup():
    st.file_uploader('upload csv file', accept_multiple_files=True)


def main():
    files = [st.session_state[f'fnames_condition_{n + 1}'] for n in range(st.session_state['num_condition'])]
    if not st.session_state.extracted:
        if not all(files):
            st.markdown(f" <h1 style='text-align: left; color: #EEEEEE; font-size:16px; "
                        f"font-family:Avenir; font-weight:normal'>Please Upload Files...</h1> "
                        , unsafe_allow_html=True)
        elif all(files):
            text_prompt = "Extract features, split by:" \
                          f" {' & '.join([str(i + 1) for i in range(st.session_state['num_condition'])])}"
            st.markdown(f" <h1 style='text-align: left; color: #EEEEEE; font-size:16px; "
                        f"font-family:Avenir; font-weight:normal'>{text_prompt}</h1> "
                        , unsafe_allow_html=True)
            action_space = st.empty()

            if action_space.button("Start analysis"):
                with action_space.status("Working on data...", expanded=True) as status:
                    data_raw = []

                    for c in range(st.session_state['num_condition']):
                        status.update(label=f"Getting features from condition {c + 1}...", state="running",
                                      expanded=False)
                        if f'filt_pose_condition_{c + 1}' not in st.session_state:
                            st.session_state[f'filt_pose_condition_{c + 1}'] = None
                        if f'feats_condition_{c + 1}' not in st.session_state:
                            st.session_state[f'feats_condition_{c + 1}'] = None
                        data_raw.append(read_csvfiles(st.session_state[f'pose_{c + 1}']))
                        filtered_pose = []
                        for f in range(len(data_raw[c])):
                            if c == 0 and f == 0:
                                bp_level = 1
                                p = get_bodyparts(data_raw[c][0], lvl=bp_level)
                                if 'bodypart_names' not in st.session_state or 'bodypart' not in st.session_state:
                                    st.session_state['bodypart_names'] = p
                                    # st.session_state['bodypart_idx'] = pose_chosen
                                bp_index_list = []
                                for bp in p:
                                    bp_index = np.argwhere(data_raw[c][0].columns.get_level_values(bp_level) == bp)
                                    bp_index_list.append(bp_index)
                                selected_pose_idx = np.sort(np.array(bp_index_list).flatten())
                                # get rid of likelihood columns for deeplabcut
                                idx_llh = selected_pose_idx[2::3]
                                # the loaded sleap file has them too, so exclude for both
                                idx_selected = [i for i in selected_pose_idx if i not in idx_llh]
                            filt_pose, _ = adp_filt(data_raw[c][f], idx_selected, idx_llh, llh_value=0.1)
                            filtered_pose.append(filt_pose)

                        # features.append(feature_extraction(filtered_pose, len(filtered_pose), framerate=60))
                        st.session_state[f'filt_pose_condition_{c + 1}'] = filtered_pose
                        st.session_state[f'feats_condition_{c + 1}'] = \
                            feature_extraction(filtered_pose, len(filtered_pose), framerate=60)
                    status.update(label=f"All complete!", state="complete",
                                  expanded=False)
                    st.session_state.extracted = True
                st.toast('Extracted!', icon='🎉')
    option_expander = st.expander("Configure colors",
                                  expanded=False)
    behavior_colors = {key: [] for key in st.session_state["annotated_behaviors"]}
    all_c_options = list(mcolors.CSS4_COLORS.keys())
    np.random.seed(42)
    selected_idx = np.random.choice(np.arange(len(all_c_options)),
                                    len(st.session_state["annotated_behaviors"]),
                                    replace=False)
    default_colors = [all_c_options[s] for s in selected_idx]
    col1, col2, col3, col4 = option_expander.columns(4)
    for i, class_id in enumerate(st.session_state["annotated_behaviors"]):
        if i % 4 == 0:
            behavior_colors[class_id] = col1.selectbox(f'select color for {st.session_state["annotated_behaviors"][i]}',
                                                       all_c_options,
                                                       index=all_c_options.index(default_colors[i]),
                                                       key=f'color_option{i}'
                                                       )

        elif i % 4 == 1:
            behavior_colors[class_id] = col2.selectbox(f'select color for {st.session_state["annotated_behaviors"][i]}',
                                                       all_c_options,
                                                       index=all_c_options.index(default_colors[i]),
                                                       key=f'color_option{i}'
                                                       )
        elif i % 4 == 2:
            behavior_colors[class_id] = col3.selectbox(f'select color for {st.session_state["annotated_behaviors"][i]}',
                                                       all_c_options,
                                                       index=all_c_options.index(default_colors[i]),
                                                       key=f'color_option{i}'
                                                       )
        elif i % 4 == 3:
            behavior_colors[class_id] = col4.selectbox(f'select color for {st.session_state["annotated_behaviors"][i]}',
                                                       all_c_options,
                                                       index=all_c_options.index(default_colors[i]),
                                                       key=f'color_option{i}'
                                                       )
    if 'behavior_colors' not in st.session_state:
        st.session_state['behavior_colors'] = None
    st.session_state['behavior_colors'] = behavior_colors
    # condition_kinematix_plot()
    try:
        if st.session_state.extracted:
            st.markdown(f" <h1 style='text-align: left; color: #EEEEEE; font-size:16px; "
                        f"font-family:Avenir; font-weight:normal'>&nbspChoose analysis method</h1> "
                        , unsafe_allow_html=True)
            analysis_chosen = st.radio('Analysis method', ['behavioral ratio'.capitalize(),
                                                           'frequency'.capitalize(),
                                                           'duration'.capitalize(),
                                                           'location'.capitalize(),
                                                           'kinematics'.capitalize(),
                                                           'transition'.capitalize()],
                                       horizontal=True, index=0,
                                       label_visibility='collapsed')
            if analysis_chosen == 'behavioral ratio'.capitalize():
                condition_pie_plot()
            elif analysis_chosen == 'frequency'.capitalize():
                condition_bar_plot()
            elif analysis_chosen == 'duration'.capitalize():
                condition_ridge_plot()
            elif analysis_chosen == 'location'.capitalize():
                condition_location_plot()
            elif analysis_chosen == 'kinematics'.capitalize():
                condition_kinematix_plot()
            elif analysis_chosen == 'transition'.capitalize():
                # condition_transmat_plot()
                st.markdown(f" <h1 style='text-align: left; color: #EEEEEE; font-size:24px; "
                            f"font-family:Avenir; font-weight:normal'>UNDER CONSTRUCTION...</h1> "
                            , unsafe_allow_html=True)

    except:
        pass

    bottom_cont = st.container()
    with bottom_cont:
        st.markdown("""---""")
        st.markdown(f" <h1 style='text-align: left; color: gray; font-size:16px; "
                    f"font-family:Avenir; font-weight:normal'>"
                    f"LUPE is developed by Alexander Hsu and Justin James</h1> "
                    , unsafe_allow_html=True)
