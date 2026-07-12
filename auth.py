
from __future__ import annotations

from typing import Any

import streamlit as st
from supabase import Client, create_client


SESSION_KEYS = (
    "sb_access_token",
    "sb_refresh_token",
    "sb_user_id",
    "sb_user_email",
    "sb_profile",
)


def _client() -> Client:
    """Create a Supabase client and restore this browser tab's auth session."""
    client = create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"],
    )

    access_token = st.session_state.get("sb_access_token")
    refresh_token = st.session_state.get("sb_refresh_token")

    if access_token and refresh_token:
        try:
            response = client.auth.set_session(access_token, refresh_token)
            if response.session:
                _save_session(response.session, response.user)
        except Exception:
            _clear_local_session()

    return client


def _save_session(session: Any, user: Any) -> None:
    if session:
        st.session_state["sb_access_token"] = session.access_token
        st.session_state["sb_refresh_token"] = session.refresh_token

    if user:
        st.session_state["sb_user_id"] = str(user.id)
        st.session_state["sb_user_email"] = user.email or ""


def _clear_local_session() -> None:
    for key in SESSION_KEYS:
        st.session_state.pop(key, None)


def _error_text(exc: Exception) -> str:
    text = str(exc)

    friendly = {
        "Invalid login credentials": "Incorrect email or password.",
        "Email not confirmed": "Confirm your email before signing in.",
        "User already registered": "An account already exists for this email.",
        "Password should be at least 6 characters": "Password must be at least 6 characters.",
    }

    for raw, message in friendly.items():
        if raw.lower() in text.lower():
            return message

    return text


def _auth_css() -> None:
    st.markdown(
        """
        <style>
        .auth-shell {
            max-width:470px;
            margin:5vh auto 0;
            padding:28px;
            border:1px solid rgba(255,255,255,.10);
            border-radius:20px;
            background:
                radial-gradient(circle at 20% 0%, rgba(245,221,79,.09), transparent 35%),
                linear-gradient(180deg, rgba(16,21,28,.98), rgba(7,10,14,.98));
            box-shadow:0 24px 70px rgba(0,0,0,.36);
        }

        .auth-logo {
            text-align:center;
            font-size:28px;
            font-weight:950;
            letter-spacing:.08em;
            color:#f4f6f8;
        }

        .auth-logo span {
            color:#f5dd4f;
        }

        .auth-subtitle {
            text-align:center;
            color:#8e98a7;
            font-size:11px;
            letter-spacing:.08em;
            margin:5px 0 20px;
        }

        .auth-note {
            margin-top:12px;
            padding:10px 11px;
            border:1px solid rgba(255,255,255,.08);
            border-radius:11px;
            background:#090d12;
            color:#9da7b5;
            font-size:10px;
            line-height:1.45;
        }

        .locked-card {
            max-width:620px;
            margin:7vh auto 0;
            padding:28px;
            text-align:center;
            border:1px solid rgba(255,255,255,.10);
            border-radius:20px;
            background:linear-gradient(180deg, rgba(16,21,28,.98), rgba(7,10,14,.98));
            box-shadow:0 24px 70px rgba(0,0,0,.34);
        }

        .locked-title {
            font-size:24px;
            font-weight:950;
            color:#f4f6f8;
        }

        .locked-plan {
            color:#f5dd4f;
            font-size:12px;
            font-weight:900;
            margin-top:8px;
        }

        .locked-copy {
            color:#9da7b5;
            font-size:11px;
            line-height:1.5;
            margin:12px 0 18px;
        }

        [data-testid="stForm"] {
            border:0;
            padding:0;
        }

        [data-testid="stTextInput"] input {
            min-height:44px;
            border-radius:11px;
        }

        [data-testid="stFormSubmitButton"] button,
        [data-testid="stButton"] button {
            min-height:42px;
            border-radius:11px;
            font-weight:900;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _profile_for_user(client: Client, user_id: str) -> dict[str, Any] | None:
    response = (
        client.table("profiles")
        .select("id,email,subscription,active,created_at")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )
    return response.data


def sign_out() -> None:
    try:
        _client().auth.sign_out({"scope": "local"})
    except Exception:
        pass

    _clear_local_session()
    st.rerun()


def _login_form(client: Client) -> None:
    with st.form("trinity_login", clear_on_submit=False):
        email = st.text_input("Email", placeholder="you@email.com")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("ENTER TRINITY", use_container_width=True)

    if submitted:
        if not email.strip() or not password:
            st.error("Enter your email and password.")
            return

        try:
            response = client.auth.sign_in_with_password(
                {
                    "email": email.strip().lower(),
                    "password": password,
                }
            )

            if not response.session or not response.user:
                st.error("Unable to create a login session.")
                return

            _save_session(response.session, response.user)
            st.rerun()
        except Exception as exc:
            st.error(_error_text(exc))


def _signup_form(client: Client) -> None:
    with st.form("trinity_signup", clear_on_submit=False):
        email = st.text_input("Email", placeholder="you@email.com", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        confirm = st.text_input("Confirm password", type="password")
        submitted = st.form_submit_button("CREATE ACCOUNT", use_container_width=True)

    if submitted:
        email = email.strip().lower()

        if not email or not password:
            st.error("Enter an email and password.")
            return

        if password != confirm:
            st.error("Passwords do not match.")
            return

        if len(password) < 8:
            st.error("Use at least 8 characters.")
            return

        try:
            response = client.auth.sign_up(
                {
                    "email": email,
                    "password": password,
                }
            )

            # Email confirmation is enabled in Supabase, so session is normally None.
            if response.session and response.user:
                _save_session(response.session, response.user)
                st.rerun()
            else:
                st.success("Account created. Check your email to confirm it, then sign in.")
        except Exception as exc:
            st.error(_error_text(exc))


def _reset_form(client: Client) -> None:
    with st.form("trinity_reset"):
        email = st.text_input("Email", placeholder="you@email.com", key="reset_email")
        submitted = st.form_submit_button("SEND RESET EMAIL", use_container_width=True)

    if submitted:
        if not email.strip():
            st.error("Enter your email.")
            return

        try:
            options = {}
            app_url = st.secrets.get("APP_URL", "")
            if app_url:
                options["redirect_to"] = app_url

            if options:
                client.auth.reset_password_for_email(email.strip().lower(), options)
            else:
                client.auth.reset_password_for_email(email.strip().lower())

            st.success("Password reset email sent.")
        except Exception as exc:
            st.error(_error_text(exc))


def _login_screen() -> None:
    _auth_css()
    client = _client()

    st.markdown(
        """
        <div class="auth-shell">
            <div class="auth-logo"><span>7C</span> TRINITY</div>
            <div class="auth-subtitle">INSTITUTIONAL GEX TERMINAL</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    login_tab, signup_tab, reset_tab = st.tabs(
        ["SIGN IN", "CREATE ACCOUNT", "RESET PASSWORD"]
    )

    with login_tab:
        _login_form(client)

    with signup_tab:
        _signup_form(client)
        st.markdown(
            '<div class="auth-note">After signup, confirm the email from Supabase before signing in.</div>',
            unsafe_allow_html=True,
        )

    with reset_tab:
        _reset_form(client)


def _inactive_screen(profile: dict[str, Any]) -> None:
    _auth_css()

    plan = str(profile.get("subscription") or "trial").upper()
    email = str(profile.get("email") or st.session_state.get("sb_user_email", ""))

    st.markdown(
        f"""
        <div class="locked-card">
            <div class="locked-title">TRINITY ACCESS LOCKED</div>
            <div class="locked-plan">{plan}</div>
            <div class="locked-copy">
                Signed in as {email}. Your account exists, but dashboard access
                is not active yet. Complete your subscription or contact 7th Capital.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        payment_link = st.secrets.get("STRIPE_PAYMENT_LINK", "")
        if payment_link:
            st.link_button(
                "ACTIVATE SUBSCRIPTION",
                payment_link,
                use_container_width=True,
            )
        else:
            st.info("Stripe checkout will be connected next.")

    with col2:
        if st.button("LOG OUT", use_container_width=True):
            sign_out()

    st.stop()


def require_active_subscription() -> dict[str, Any]:
    """
    Gate the dashboard.

    Returns the authenticated user's profile only when profile.active is true.
    Otherwise renders login or locked-subscription UI and stops the app.
    """
    _auth_css()

    if not st.session_state.get("sb_access_token"):
        _login_screen()
        st.stop()

    client = _client()
    user_id = st.session_state.get("sb_user_id")

    if not user_id:
        _clear_local_session()
        st.rerun()

    try:
        profile = _profile_for_user(client, user_id)
    except Exception as exc:
        st.error(f"Unable to verify your subscription: {_error_text(exc)}")
        if st.button("LOG OUT"):
            sign_out()
        st.stop()

    if not profile:
        st.warning("Your account is still being provisioned. Refresh in a few seconds.")
        if st.button("REFRESH"):
            st.rerun()
        if st.button("LOG OUT"):
            sign_out()
        st.stop()

    st.session_state["sb_profile"] = profile

    if not bool(profile.get("active")):
        _inactive_screen(profile)

    return profile


def account_bar(profile: dict[str, Any]) -> None:
    """Small account bar for authenticated users."""
    email = str(profile.get("email") or "")
    plan = str(profile.get("subscription") or "member").upper()

    left, right = st.columns([5, 1])

    with left:
        st.caption(f"{email} · {plan}")

    with right:
        if st.button("LOG OUT", key="top_logout", use_container_width=True):
            sign_out()
