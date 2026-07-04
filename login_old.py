import streamlit as st
from auth import signup, login


def login_page():

    st.title("🔐 Financial AI Advisor")

    menu = st.radio(
        "Choose",
        ["Login", "Sign Up"]
    )

    # ----------------------------
    # LOGIN
    # ----------------------------

    if menu == "Login":

        st.subheader("Login")

        email = st.text_input("Email")

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            success, user = login(
                email,
                password
            )

            if success:

                st.session_state.logged_in = True
                st.session_state.user = user

                st.success("Login Successful!")

                st.rerun()

            else:

                st.error("Invalid Email or Password")

    # ----------------------------
    # SIGNUP
    # ----------------------------

    else:

        st.subheader("Create Account")

        name = st.text_input("Full Name")

        email = st.text_input("Email Address")

        password = st.text_input(
            "Password",
            type="password"
        )

        confirm = st.text_input(
            "Confirm Password",
            type="password"
        )

        if st.button("Create Account"):

            if password != confirm:

                st.error("Passwords do not match.")

            elif len(password) < 6:

                st.error("Password should be at least 6 characters.")

            else:

                success, msg = signup(
                    name,
                    email,
                    password
                )

                if success:

                    st.success(msg)

                else:

                    st.error(msg)