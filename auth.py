rom __future__ import annotations

from typing import Any
from pathlib import Path
import base64

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



def _logo_data_uri() -> str:
    """Return the local 7C logo as an embeddable data URI."""
    logo_path = Path(__file__).with_name("7c_logo.jpg")
    if not logo_path.exists():
        return ""

    encoded = base64.b64encode(logo_path.read_bytes()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


def _auth_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --seven-purple:#8b3dff;
            --seven-purple-soft:#b56cff;
            --seven-gold:#f4c542;
            --seven-gold-light:#ffe991;
            --seven-bg:#07050c;
            --seven-panel:#100c18;
            --seven-line:rgba(244,197,66,.16);
            --seven-muted:#9b94aa;
        }

        .stApp {
            background:
                radial-gradient(circle at 16% 5%, rgba(139,61,255,.13), transparent 31%),
                radial-gradient(circle at 88% 0%, rgba(244,197,66,.07), transparent 25%),
                linear-gradient(180deg,#08060d,#050408 70%);
        }

        .block-container {
            max-width:980px;
            padding-top:2.1rem;
        }

        .auth-shell {
            max-width:520px;
            margin:2.5vh auto 20px;
            padding:22px 26px 24px;
            border:1px solid var(--seven-line);
            border-radius:24px;
            background:
                linear-gradient(145deg,rgba(25,16,39,.96),rgba(8,7,12,.98));
            box-shadow:
                0 30px 90px rgba(0,0,0,.48),
                0 0 50px rgba(139,61,255,.08);
            text-align:center;
            overflow:hidden;
            position:relative;
        }

        .auth-shell:before {
            content:"";
            position:absolute;
            inset:0;
            pointer-events:none;
            background:linear-gradient(115deg,transparent 25%,rgba(255,255,255,.035),transparent 60%);
        }

        .auth-logo-img {
            width:118px;
            height:118px;
            object-fit:cover;
            border-radius:24px;
            border:1px solid rgba(244,197,66,.30);
            box-shadow:
                0 12px 38px rgba(0,0,0,.45),
                0 0 34px rgba(139,61,255,.18);
            margin-bottom:12px;
        }

        .auth-brand {
            font-size:23px;
            font-weight:950;
            letter-spacing:.14em;
            color:#fff;
        }

        .auth-brand span {
            color:var(--seven-gold);
        }

        .auth-product {
            margin-top:5px;
            color:var(--seven-purple-soft);
            font-size:11px;
            font-weight:900;
            letter-spacing:.18em;
        }

        .auth-subtitle {
            color:var(--seven-muted);
            font-size:9px;
            letter-spacing:.13em;
            margin-top:5px;
        }

        .auth-note {
            margin-top:12px;
            padding:11px 12px;
            border:1px solid rgba(244,197,66,.10);
            border-radius:12px;
            background:rgba(11,8,16,.86);
            color:#aaa3b5;
            font-size:10px;
            line-height:1.45;
        }

        .locked-card {
            max-width:620px;
            margin:7vh auto 0;
            padding:30px;
            text-align:center;
            border:1px solid var(--seven-line);
            border-radius:24px;
            background:linear-gradient(145deg,rgba(25,16,39,.97),rgba(8,7,12,.98));
            box-shadow:0 28px 85px rgba(0,0,0,.45);
        }

        .locked-title {
            font-size:23px;
            font-weight:950;
            color:#fff;
            letter-spacing:.06em;
        }

        .locked-plan {
            display:inline-block;
            color:#110c18;
            background:linear-gradient(90deg,var(--seven-gold),var(--seven-gold-light));
            border-radius:999px;
            padding:5px 10px;
            font-size:10px;
            font-weight:950;
            margin-top:10px;
        }

        .locked-copy {
            color:#aaa3b5;
            font-size:11px;
            line-height:1.55;
            margin:14px 0 18px;
        }

        [data-testid="stTabs"] button {
            font-size:10px;
            font-weight:850;
            letter-spacing:.04em;
        }

        [data-testid="stTabs"] [aria-selected="true"] {
            color:var(--seven-gold) !important;
        }

        [data-testid="stTextInput"] input {
            min-height:46px;
            border-radius:12px;
            background:#100d17;
            border:1px solid rgba(255,255,255,.10);
        }

        [data-testid="stTextInput"] input:focus {
            border-color:rgba(139,61,255,.70);
            box-shadow:0 0 0 1px rgba(139,61,255,.26);
        }

        [data-testid="stForm"] {
            border:0;
            padding:0;
        }

        [data-testid="stFormSubmitButton"] button,
        [data-testid="stButton"] button,
        [data-testid="stLinkButton"] a {
            min-height:44px;
            border-radius:12px;
            font-weight:950;
            letter-spacing:.04em;
            border:1px solid rgba(244,197,66,.25);
            background:linear-gradient(90deg,#6f27ce,#953fff);
            color:#fff;
        }

        [data-testid="stFormSubmitButton"] button:hover,
        [data-testid="stButton"] button:hover,
        [data-testid="stLinkButton"] a:hover {
            border-color:var(--seven-gold);
            box-shadow:0 0 22px rgba(139,61,255,.22);
        }

        .account-chip {
            display:flex;
            align-items:center;
            gap:8px;
            padding:7px 10px;
            border:1px solid rgba(244,197,66,.16);
            border-radius:999px;
            background:rgba(16,12,24,.88);
            font-size:9px;
            color:#c8c1d2;
        }

        .account-plan {
            color:var(--seven-gold);
            font-weight:950;
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

    logo_uri = _logo_data_uri()
    logo_html = (
        f'<img class="auth-logo-img" src="{logo_uri}" alt="7th Capital logo">'
        if logo_uri else ""
    )

    st.markdown(
        f"""
        <div class="auth-shell">
            {logo_html}
            <div class="auth-brand"><span>7TH</span> CAPITAL</div>
            <div class="auth-product">TRINITY TERMINAL</div>
            <div class="auth-subtitle">INSTITUTIONAL OPTIONS INTELLIGENCE</div>
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
    """Branded account bar for authenticated users."""
    email = str(profile.get("email") or "")
    plan = str(profile.get("subscription") or "member").upper()

    left, right = st.columns([5, 1])

    with left:
        st.markdown(
            f'<div class="account-chip">7TH CAPITAL MEMBER · '
            f'<span class="account-plan">{plan}</span> · {email}</div>',
            unsafe_allow_html=True,
        )

    with right:
        if st.button("LOG OUT", key="top_logout", use_container_width=True):
            sign_out()
