from career_weights import score_tracks, get_skill_gaps, build_roadmap_ai
import streamlit as st
import joblib
import pandas as pd

st.set_page_config(
    page_title="AI Career Compass",
    page_icon="🧭",
    layout="wide"
)

st.title("AI Career Compass")
st.write("Career Readiness & Placement Intelligence")
st.divider()
col1, col2, col3 = st.columns(3)
col1.metric("ML Models Compared", "3")
col2.metric("Career Tracks", "12")
col3.metric("Training Records", "10,000")

model = joblib.load("models/placement_model.pkl")

X_columns = ["IQ", "Prev_Sem_Result", "CGPA", "Academic_Performance",
             "Internship_Experience", "Extra_Curricular_Score",
             "Communication_Skills", "Projects_Completed"]

feature_ranges = pd.DataFrame({
    "IQ": [41, 158], "Prev_Sem_Result": [5.0, 10.0], "CGPA": [4.54, 10.46],
    "Academic_Performance": [1, 10], "Internship_Experience": [0, 1],
    "Extra_Curricular_Score": [0, 10], "Communication_Skills": [1, 10],
    "Projects_Completed": [0, 5]
}, index=["min", "max"])

with st.sidebar:
    st.header("Enter your profile")
    iq = st.slider("IQ", min_value=40, max_value=160, value=100)
    prev_sem_result = st.slider("Previous Semester Result (CGPA)", 4.0, 10.0, 7.5)
    cgpa = st.slider("Current CGPA", 4.0, 10.0, 7.5)
    academic_performance = st.slider("Academic Performance (1-10)", 1, 10, 5)
    internship_experience = st.radio("Internship Experience?", ["No", "Yes"])
    extra_curricular = st.slider("Extra-Curricular Score (0-10)", 0, 10, 5)
    communication = st.slider("Communication Skills (1-10)", 1, 10, 5)
    projects_completed = st.slider("Projects Completed", 0, 5, 2)

    st.header("Rate your skills (0-10)")
    dsa = st.slider("DSA / Problem Solving", 0, 10, 0)
    python_skill = st.slider("Python", 0, 10, 0)
    java_node = st.slider("Java / Node.js", 0, 10, 0)
    html_css_js = st.slider("HTML/CSS/JS", 0, 10, 0)
    react = st.slider("React", 0, 10, 0)
    sql_skill = st.slider("SQL", 0, 10, 0)
    excel_powerbi = st.slider("Excel / Power BI", 0, 10, 0)
    ml_skill = st.slider("Machine Learning", 0, 10, 0)
    dl_skill = st.slider("Deep Learning", 0, 10, 0)
    cloud = st.slider("Cloud (AWS/Azure)", 0, 10, 0)
    devops = st.slider("Docker/Kubernetes/CI-CD", 0, 10, 0)
    security = st.slider("Networking/Security", 0, 10, 0)
    mobile = st.slider("Mobile (Flutter/Kotlin/RN)", 0, 10, 0)

    submit = st.button("Analyze My Profile")

if submit:
    internship_value = 1 if internship_experience == "Yes" else 0

    input_data = [[
        iq, prev_sem_result, cgpa, academic_performance,
        internship_value, extra_curricular, communication, projects_completed
    ]]

    probability = model.predict_proba(input_data)[0][1]
    readiness_score = round(probability * 100, 1)

    tab1, tab2 = st.tabs(["📊 Readiness Score", "🎯 Career Match"])

    with tab1:
        st.header(f"Career Readiness Score: {readiness_score}%")
        warnings = []
        values = dict(zip(X_columns, input_data[0]))
        for col in X_columns:
            min_val, max_val = feature_ranges.loc["min", col], feature_ranges.loc["max", col]
            if values[col] < min_val or values[col] > max_val:
                warnings.append(f"{col} = {values[col]} is outside the training range ({min_val}-{max_val})")
        if warnings:
            st.warning("⚠️ Some inputs are unusual compared to our training data — treat this score as an early estimate.")
            for w in warnings:
                st.caption(w)

    with tab2:
        skill_profile = {
            "dsa": dsa, "python": python_skill, "java_node": java_node,
            "html_css_js": html_css_js, "react": react, "sql": sql_skill,
            "excel_powerbi": excel_powerbi, "ml": ml_skill, "dl": dl_skill,
            "cloud": cloud, "devops": devops, "security": security,
            "mobile": mobile, "communication": communication,
            "projects": projects_completed, "internships": 1 if internship_experience == "Yes" else 0,
        }
        track_matches = score_tracks(skill_profile)

        st.header("Career Track Match")
        for track, pct in track_matches.items():
            st.write(f"**{track}** — {pct}%")
            st.progress(int(pct))

        top_track = list(track_matches.keys())[0]
        gaps = get_skill_gaps(top_track, skill_profile)
        st.subheader(f"Closest match: {top_track}")
        st.write("**Skills you have:**", ", ".join(gaps["has"]) if gaps["has"] else "None yet")
        st.write("**Skills to build:**", ", ".join(gaps["needs"]) if gaps["needs"] else "None — strong fit!")
        st.subheader("Your Roadmap")
        roadmap_text = build_roadmap_ai(top_track, gaps["needs"])
        st.write(roadmap_text)