import streamlit as st

st.set_page_config(
    page_title="About | Automated Student Performance Analysis",
    layout="wide"
)

left_pad, content, right_pad = st.columns([1, 3, 1])

with content:
    st.title("About the Application")

    st.markdown(
        """
        Automated Student Performance Analysis is a web-based application designed
        to make academic data easier to understand, explore, and act upon.

        Instead of manually working through spreadsheets,
        the system transforms raw student records into
        meaningful insights and interactive visualizations.
        """
    )

    st.divider()

    st.markdown(
        """
        ### Why this application exists

        Academic data is often stored in spreadsheets that differ in structure,
        naming conventions, and formatting.
        This makes consistent analysis difficult and time-consuming.

        This application bridges that gap by accepting real-world datasets,
        cleaning them automatically, and presenting performance insights
        in a clear and intuitive format.

        The goal is not just analysis — but clarity.
        """
    )

    st.divider()

    st.markdown("### What you can do")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            """
            **Prepare data effortlessly**

            Upload CSV or Excel files.
            The system detects columns, cleans values,
            and reshapes the data for analysis.
            """
        )

    with c2:
        st.markdown(
            """
            **Understand performance trends**

            Analyze subject-wise performance,
            rankings, and attendance patterns
            using interactive charts.
            """
        )

    c3, c4 = st.columns(2)

    with c3:
        st.markdown(
            """
            **Dive into individual students**

            View subject-level marks,
            strengths, weaknesses,
            and attendance summaries.
            """
        )

    with c4:
        st.markdown(
            """
            **Identify at-risk students**

            Automatically flag students
            based on academic and
            attendance thresholds.
            """
        )

    st.divider()

    st.markdown(
        """
        ### What kind of data does this application expect?

        The application works with student academic performance data
        stored in CSV or Excel format.

        Each row in the uploaded dataset should represent a student,
        with columns describing identification details and subject marks.
        """
    )

    st.markdown(
        """
        **Required information**

        - Student identifier (registration number or roll number)
        - Student name
        - Class or grade
        - Term, semester, or assessment name
        - Attendance (percentage or decimal form)
        """
    )

    st.markdown(
        """
        **Subject marks**

        Subject columns can be named freely
        (for example: Maths, Physics, English).
        These are automatically interpreted
        as individual subjects by the system.
        """
    )

    st.markdown(
        """
        **Flexible formatting**

        The system is designed to handle:
        - Different column naming conventions
        - Marks and attendance stored as text or numbers
        - Missing or partially filled records

        This makes it suitable for real-world academic datasets.
        """
    )

    st.divider()

    st.markdown(
        """
        ### Smart features built into the system

        Several features are intentionally designed
        to handle common academic data issues.
        """
    )

    st.markdown(
        """
        **Automatic column detection**

        Recognizes common aliases such as
        Roll No, Reg No, Student Name, and Attendance %
        without requiring manual renaming.
        """
    )

    st.markdown(
        """
        **Dual data cleaning modes**

        Users can choose between:
        - Automatic cleaning for quick analysis
        - Manual column mapping for full control
        """
    )

    st.markdown(
        """
        **Wide-to-long data transformation**

        Subject columns are reshaped into a long format,
        enabling subject-wise analysis without a fixed schema.
        """
    )

    st.markdown(
        """
        **Robust validation rules**

        The system:
        - Removes invalid or non-numeric marks
        - Normalizes attendance values
        - Drops duplicate or unusable records

        All cleaning actions are summarized transparently.
        """
    )

    st.divider()

    st.markdown(
        """
        ### Design decisions

        This application prioritizes interpretability
        over black-box automation.

        Instead of machine learning models,
        it focuses on clear metrics,
        visual explanations,
        and reproducible results.

        This ensures insights are easy to understand
        and explain in an academic context.
        """
    )

    st.divider()

    st.markdown(
        """
        ### Limitations and future scope

        Currently, the application focuses on
        descriptive and diagnostic analysis.

        Potential future enhancements include:
        - Predictive academic risk analysis
        - Multi-term performance tracking
        - Role-based dashboards
        - Exportable reports and alerts
        """
    )

    st.divider()

    st.markdown("### Get started")

    st.markdown(
        """
        👉 **[Upload data and begin analysis →](/)**  
        👉 **[View overall performance summary →](/Total_Summary)**  
        👉 **[Explore individual student insights →](/Student_Summary)**
        """
    )

    st.markdown(
        "<p style='text-align:center; color: gray; margin-top: 3rem;'>"
        "Automated Student Performance Analysis</p>",
        unsafe_allow_html=True
    )