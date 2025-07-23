"""
CSS Styling for Telmi - SURGICAL FIX ONLY
Only fixes the specific issues without touching working elements
Based on your existing GitHub repository design
"""

import streamlit as st

def apply_custom_styling():
    """Apply SURGICAL fixes while preserving all existing working design."""

    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Root variables for consistent theming */
    :root {
        --primary-color: #4299e1;
        --primary-hover: #3182ce;
        --primary-light: #63b3ed;
        --background-color: #ffffff;
        --surface-color: #f7fafc;
        --text-primary: #1a202c;
        --text-secondary: #4a5568;
        --text-muted: #a0aec0;
        --border-color: #e2e8f0;
        --success-color: #48bb78;
        --error-color: #f56565;
        --shadow-sm: 0 1px 3px 0 rgb(0 0 0 / 0.1);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
        --radius-md: 8px;
        --radius-lg: 12px;
    }

    /* Global styles */
    .main {
        padding: 0;
        max-width: none;
    }

    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background-color: var(--background-color);
    }

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    .stActionButton {display: none;}

    /* ===============================================
       SURGICAL FIX 1: REMOVE ALL OVERLAPPING BORDERS COMPLETELY
       =============================================== */
    
    /* RESET: Remove ALL borders and styling from container divs to eliminate double borders */
    .stTextInput > div,
    .stTextInput > div > div,
    .stTextInput > label,
    .stTextInput [data-testid="stTextInput-RootElement"] {
        border: none !important;
        border-radius: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
        outline: none !important;
    }

    /* ===============================================
       SURGICAL FIX 2: PERFECT HEIGHT MATCHING & CENTERING
       =============================================== */
    
    /* UNIVERSAL: All inputs get EXACT button height and perfect centering */
    .stTextInput > div > div > input {
        border: 2px solid var(--border-color) !important;
        border-radius: 8px !important;
        background: #ffffff !important;
        color: var(--text-primary) !important;
        font-size: 15px !important;
        font-weight: 400 !important;
        font-family: 'Inter', sans-serif !important;
        
        /* MATCH BUTTON HEIGHT EXACTLY - Reduced from 46px to 42px */
        height: 42px !important;
        line-height: 42px !important;  /* Perfect vertical centering */
        padding: 0 16px !important;    /* Only horizontal padding for perfect centering */
        
        /* LAYOUT FIXES */
        box-sizing: border-box !important;
        width: 100% !important;
        margin: 0 !important;
        display: block !important;
        vertical-align: middle !important;
        transition: all 0.2s ease !important;
        outline: none !important;
    }

    /* Perfect focus state - no height change */
    .stTextInput > div > div > input:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1) !important;
        outline: none !important;
        /* Height stays exactly the same */
        height: 42px !important;
        line-height: 42px !important;
    }

    /* Ensure input container matches exactly */
    .stTextInput > div {
        min-height: 42px !important;
        height: 42px !important;
        overflow: visible !important;
        position: relative !important;
    }

    /* ===============================================
       SURGICAL FIX 3: COMPLETELY FIX PASSWORD FIELD OVERLAP
       =============================================== */

    /* COMPLETELY HIDE the overlapping "Please fill form" message */
    .stTextInput > div > div > div[data-testid="InputInstructions"],
    .stTextInput div[data-testid="InputInstructions"],
    .stTextInput [data-testid="InputInstructions"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        position: absolute !important;
        top: -9999px !important;
        left: -9999px !important;
    }

    /* Position show/hide button properly and make it visible */
    .stTextInput > div > div > button[kind="tertiary"] {
        position: absolute !important;
        right: 12px !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        z-index: 20 !important;
        background: transparent !important;
        border: none !important;
        color: #718096 !important;
        font-size: 12px !important;
        padding: 4px 6px !important;
        border-radius: 4px !important;
        cursor: pointer !important;
        height: auto !important;
        min-height: auto !important;
        width: auto !important;
        margin: 0 !important;
    }

    /* Show/hide button hover state */
    .stTextInput > div > div > button[kind="tertiary"]:hover {
        background: #f7fafc !important;
        color: #4a5568 !important;
    }

    /* Add proper padding for password fields to make space for button */
    .stTextInput > div > div > input[type="password"] {
        padding-right: 50px !important;  /* More space for button */
    }

    /* Keep auth forms clean - hide show/hide buttons for login/register */
    .login-container .stTextInput button[kind="tertiary"],
    .stForm .stTextInput button[kind="tertiary"] {
        display: none !important;
    }

    /* Also hide instructions for auth forms */
    .login-container .stTextInput > div > div > div[data-testid="InputInstructions"],
    .stForm .stTextInput > div > div > div[data-testid="InputInstructions"],
    .login-container .stTextInput div[data-testid="InputInstructions"],
    .stForm .stTextInput div[data-testid="InputInstructions"] {
        display: none !important;
    }

    /* ===============================================
       PRESERVE ALL EXISTING WORKING STYLES
       =============================================== */

    /* === ENHANCED AUTHENTICATION STYLING === */

    /* Tab styling for login/register */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: #f8fafc;
        border-radius: 10px;
        padding: 4px;
        margin-bottom: 1.5rem;
        width: 100%;
        justify-content: center;
    }

    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 8px;
        background: transparent;
        border: none;
        color: #718096;
        font-weight: 500;
        font-size: 15px;
        padding: 0 20px;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        flex: 1;
        min-width: 120px;
    }

    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #2d3748 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        font-weight: 600;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: #edf2f7;
        color: #4a5568;
    }

    /* Login container */
    .login-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        margin: 2rem 0;
        animation: slideUp 0.6s ease-out;
    }

    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }

    .login-header h1 {
        font-size: 3rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        background: linear-gradient(135deg, #4299e1, #63b3ed, #90cdf4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.02em;
    }

    .login-header p {
        color: #718096;
        font-size: 1.2rem;
        margin: 0.8rem 0 0 0;
        font-weight: 400;
    }

    /* ===============================================
       SURGICAL FIX 4: AUTH FORMS - MATCH ACTUAL BUTTON HEIGHT
       =============================================== */

    /* Auth form inputs - EXACT same height as actual auth buttons */
    .login-container .stTextInput > div > div > input,
    .stForm .stTextInput > div > div > input {
        border: 2px solid #e2e8f0 !important;
        border-radius: 10px !important;
        background: #ffffff !important;
        color: #2d3748 !important;
        font-size: 15px !important;
        font-weight: 400 !important;
        font-family: 'Inter', sans-serif !important;
        
        /* MATCH ACTUAL AUTH BUTTON HEIGHT - Reduced to match visual button size */
        height: 44px !important;
        line-height: 44px !important;  /* Perfect centering */
        padding: 0 16px !important;    /* Only horizontal padding */
        
        /* LAYOUT */
        box-sizing: border-box !important;
        width: 100% !important;
        margin: 0 !important;
        display: block !important;
        vertical-align: middle !important;
        transition: all 0.2s ease !important;
        outline: none !important;
    }

    /* Auth form focus - maintain exact height */
    .login-container .stTextInput > div > div > input:focus,
    .stForm .stTextInput > div > div > input:focus {
        border-color: #4299e1 !important;
        box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1) !important;
        outline: none !important;
        /* Keep exact same height as button */
        height: 44px !important;
        line-height: 44px !important;
    }

    /* Auth form containers */
    .login-container .stTextInput > div,
    .stForm .stTextInput > div {
        min-height: 44px !important;
        height: 44px !important;
        overflow: visible !important;
        position: relative !important;
    }

    /* ===============================================
       SURGICAL FIX 5: CHAT FORM - MATCH ACTUAL BUTTON HEIGHT  
       =============================================== */

    /* Chat inputs - EXACT same height as actual send button */
    .main .stTextInput > div > div > input:not(.login-container .stTextInput > div > div > input):not(.stForm .stTextInput > div > div > input) {
        border: 2px solid #e2e8f0 !important;
        border-radius: 8px !important;
        background: #ffffff !important;
        color: #2d3748 !important;
        font-size: 15px !important;
        
        /* MATCH ACTUAL SEND BUTTON HEIGHT - Reduced to match visual button size */
        height: 38px !important;
        line-height: 38px !important;  /* Perfect centering */
        padding: 0 16px !important;    /* Only horizontal padding */
        
        /* LAYOUT */
        box-sizing: border-box !important;
        width: 100% !important;
        margin: 0 !important;
        display: block !important;
        vertical-align: middle !important;
        transition: all 0.2s ease !important;
    }

    /* Chat input focus - maintain exact height */
    .main .stTextInput > div > div > input:not(.login-container .stTextInput > div > div > input):not(.stForm .stTextInput > div > div > input):focus {
        border-color: #4299e1 !important;
        box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1) !important;
        outline: none !important;
        /* Keep exact same height as send button */
        height: 38px !important;
        line-height: 38px !important;
    }

    /* Chat form containers */
    .main .stTextInput > div:not(.login-container .stTextInput > div):not(.stForm .stTextInput > div) {
        min-height: 38px !important;
        height: 38px !important;
        overflow: visible !important;
        position: relative !important;
    }

    /* ===============================================
       SURGICAL FIX 6: BUTTONS MATCH VISUAL SIZE EXACTLY
       =============================================== */

    /* Auth buttons - MATCH the visual size you see (44px) */
    .login-container .stButton > button,
    .stForm .stButton > button {
        background: linear-gradient(135deg, #4299e1, #3182ce) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        
        /* EXACT HEIGHT MATCH WITH AUTH INPUTS - Visual button size */
        height: 44px !important;
        min-height: 44px !important;
        line-height: 44px !important;
        padding: 0 24px !important;
        
        /* LAYOUT */
        width: 100% !important;
        box-sizing: border-box !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(66, 153, 225, 0.3) !important;
        cursor: pointer !important;
        margin: 0 !important;
    }

    /* Auth button hover - maintain height */
    .login-container .stButton > button:hover,
    .stForm .stButton > button:hover {
        background: linear-gradient(135deg, #3182ce, #2c5aa0) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(66, 153, 225, 0.4) !important;
        color: white !important;
        /* Keep exact same height */
        height: 44px !important;
        line-height: 44px !important;
    }

    /* Chat send button - MATCH the visual size you see (38px) */
    .main form[data-testid="stForm"]:not(.login-container form):not(.stForm form) .stButton > button {
        background: #4299e1 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        
        /* EXACT HEIGHT MATCH WITH CHAT INPUTS - Visual button size */
        height: 38px !important;
        min-height: 38px !important;
        line-height: 38px !important;
        padding: 0 20px !important;
        
        /* LAYOUT */
        box-sizing: border-box !important;
        margin: 0 !important;
        white-space: nowrap !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 4px rgba(66, 153, 225, 0.2) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Chat button hover - maintain height */
    .main form[data-testid="stForm"]:not(.login-container form):not(.stForm form) .stButton > button:hover {
        background: #3182ce !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(66, 153, 225, 0.3) !important;
        /* Keep exact same height */
        height: 38px !important;
        line-height: 38px !important;
    }

    /* Ensure button text is white and properly centered */
    .login-container .stButton > button p,
    .stForm .stButton > button p,
    .login-container .stButton > button span,
    .stForm .stButton > button span,
    .login-container .stButton > button div,
    .stForm .stButton > button div {
        color: white !important;
        margin: 0 !important;
        font-weight: 600 !important;
        text-align: center !important;
        line-height: 1 !important;
    }

    /* Remove conflicting placeholder text for auth forms */
    .login-container .stTextInput > div > div > div[data-testid="InputInstructions"],
    .stForm .stTextInput > div > div > div[data-testid="InputInstructions"] {
        display: none !important;
    }



    /* PRESERVE: Chat form layout - perfect alignment */
    .main form[data-testid="stForm"]:not(.login-container form):not(.stForm form) {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important; /* Prevent wrapping */
        gap: 8px !important;
        align-items: center !important;
        width: 100% !important;
        overflow: hidden !important; /* Prevent mobile overflow-induced wrapping */
    }

    .main form[data-testid="stForm"]:not(.login-container form):not(.stForm form) > div:first-child {
        flex: 1 1 auto !important;
        min-width: 0 !important; /* Prevents overflowing on small screens */
        margin: 0 !important;
    }
    
    .main form[data-testid="stForm"]:not(.login-container form):not(.stForm form) > div:last-child {
        flex-shrink: 0 !important;
        margin: 0 !important;
    }



    /* ===============================================
       PRESERVE ALL EXISTING CHAT INTERFACE STYLES
       =============================================== */

    /* === PRESERVE CHAT INTERFACE === */

    /* Chat header */
    .chat-header {
        text-align: center;
        padding: 1.5rem 0;
        border-bottom: 1px solid var(--border-color);
        background: var(--background-color);
        margin-bottom: 1rem;
    }

    .chat-header h1 {
        font-size: 2rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
        background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .chat-header p {
        color: var(--text-secondary);
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
    }

    /* PRESERVE: Message containers EXACTLY as they are */
    .message-container {
        display: flex;
        margin: 1rem 0;
        gap: 0.75rem;
        max-width: 100%;
        align-items: flex-start;
    }

    .message-container.user-message {
        flex-direction: row-reverse;
        margin-left: 2rem;
    }

    .message-container.agent-message {
        flex-direction: row;
        margin-right: 2rem;
    }

    .message-bubble {
        padding: 1rem 1.25rem;
        border-radius: var(--radius-lg);
        max-width: 70%;
        word-wrap: break-word;
        position: relative;
        box-shadow: var(--shadow-sm);
    }

    .user-bubble {
        background: var(--primary-color);
        color: white;
        border-bottom-right-radius: 6px;
    }

    .agent-bubble {
        background: var(--surface-color);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        border-bottom-left-radius: 6px;
    }

    .message-avatar {
        width: 2.5rem;
        height: 2.5rem;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        flex-shrink: 0;
        align-self: flex-start;
        margin-top: 0.5rem;
    }

    .user-avatar {
        background: var(--primary-color);
        color: white;
    }

    .agent-avatar {
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        color: var(--text-primary);
    }

    /* Section titles */
    .message-bubble h3,
    .message-bubble strong,
    h3, h4 {
        font-size: 1.25rem !important;
        font-weight: 600;
        color: var(--text-primary);
        margin: 1rem 0 0.5rem 0;
        line-height: 1.3;
    }

    .message-bubble h3:first-child,
    .message-bubble strong:first-child {
        margin-top: 0.5rem;
    }

    /* PRESERVE: Welcome message */
    .welcome-message {
        text-align: center;
        padding: 2rem;
        background: var(--surface-color);
        border-radius: var(--radius-lg);
        margin: 2rem auto;
        max-width: 600px;
        border: 1px solid var(--border-color);
    }

    .welcome-message h3 {
        color: var(--text-primary);
        margin-bottom: 1rem;
        font-weight: 600;
    }

    .welcome-message p {
        color: var(--text-secondary);
        margin-bottom: 1rem;
        line-height: 1.6;
    }

    .welcome-message ul {
        text-align: left;
        color: var(--text-secondary);
        margin: 1rem 0;
        padding-left: 1.5rem;
    }

    .welcome-message li {
        margin: 0.5rem 0;
        line-height: 1.5;
    }

    /* === PRESERVE SIDEBAR STYLING === */

    .sidebar-header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 1rem;
    }

    .sidebar-header h2 {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
        background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .sidebar-header p {
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin: 0.25rem 0 0 0;
    }

    /* Sidebar section headers */
    .streamlit-expanderHeader {
        font-weight: 700 !important;
        font-size: 17px !important;
        color: #2d3748 !important;
        background: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        margin: 8px 0 !important;
        padding: 12px 16px !important;
    }

    .streamlit-expanderHeader:hover {
        background: #edf2f7 !important;
        border-color: #cbd5e0 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }

    .streamlit-expanderContent {
        border: 1px solid #e2e8f0 !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
        background: #ffffff !important;
        padding: 16px !important;
        margin-bottom: 8px !important;
    }

    /* === PRESERVE BUTTONS STYLING === */

    .stButton > button:not(.login-container .stButton > button):not(.stForm .stButton > button) {
        background: var(--primary-color) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .stButton > button:not(.login-container .stButton > button):not(.stForm .stButton > button):hover {
        background: var(--primary-hover) !important;
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-1px) !important;
    }

    /* === PRESERVE SUCCESS/ERROR MESSAGES === */

    .stSuccess {
        background: #f0fdf4 !important;
        border: 1px solid #bbf7d0 !important;
        color: #166534 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
        font-weight: 500 !important;
    }

    .stError {
        background: #fef2f2 !important;
        border: 1px solid #fecaca !important;
        color: #dc2626 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
        font-weight: 500 !important;
    }

    .stInfo {
        background: #eff6ff !important;
        border: 1px solid #bfdbfe !important;
        color: #1d4ed8 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
        font-weight: 500 !important;
    }

    .stWarning {
        background: #fffbeb !important;
        border: 1px solid #fed7aa !important;
        color: #d97706 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
        font-weight: 500 !important;
    }

    /* === PRESERVE DOWNLOAD BUTTONS === */

    .stDownloadButton > button {
        background: var(--success-color) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease !important;
        box-shadow: var(--shadow-sm) !important;
        margin: 0.25rem 0 !important;
    }

    .stDownloadButton > button:hover {
        background: #38a169 !important;
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow-md) !important;
    }

    /* === PRESERVE RESPONSIVE DESIGN === */

    @media (max-width: 768px) {
        .login-container .stTextInput > div > div > input,
        .stForm .stTextInput > div > div > input {
            height: 46px !important;
            font-size: 14px !important;
            padding: 12px 14px !important;
        }

        .login-container .stButton > button,
        .stForm .stButton > button {
            height: 46px !important;
            font-size: 14px !important;
        }

        .main .stTextInput > div > div > input:not(.login-container .stTextInput > div > div > input):not(.stForm .stTextInput > div > div > input) {
            height: 42px !important;
            font-size: 14px !important;
        }

        .main form[data-testid="stForm"]:not(.login-container form):not(.stForm form) .stButton > button {
            height: 42px !important;
            min-height: 42px !important;
            font-size: 13px !important;
            padding: 0 16px !important;
        }

        .message-bubble {
            max-width: 85%;
        }

        .message-container.user-message {
            margin-left: 1rem;
        }

        .message-container.agent-message {
            margin-right: 1rem;
        }

        .login-header h1 {
            font-size: 2.2rem;
        }

        .chat-header h1 {
            font-size: 1.5rem;
        }
    }

    /* === PRESERVE ANIMATIONS === */

    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* === PRESERVE SCROLLBAR === */

    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--surface-color);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }

    /* === PRESERVE LAYOUT FIXES === */

    .block-container {
        padding-top: 0;
        padding-bottom: 0;
        max-width: none;
    }

    </style>
    """, unsafe_allow_html=True)