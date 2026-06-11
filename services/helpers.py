import streamlit as st


def format_multiline_text(text):
    """Converts line breaks to markdown line breaks"""
    if not text or text == '—' or text == '':
        return '—'
    # Replace \n with two spaces + \n (markdown line break)
    return text.replace('\n', '  \n')


def render_multiline_field(label, value, use_markdown=True):
    """Renders a field with line break support"""
    if not value or value == '—' or value == '':
        st.write(f"**{label}:** —")
    else:
        if use_markdown:
            st.markdown(f"**{label}:**")
            st.markdown(format_multiline_text(value))
        else:
            st.write(f"**{label}:** {value}")


def render_list_field(label, items):
    """Renders a list with bullets"""
    if not items:
        # If label is empty, don't output a colon
        if label:
            st.write(f"**{label}:** —")
        else:
            st.write("—")
    else:
        if label:
            st.markdown(f"**{label}:**")
        for item in items:
            st.markdown(f"- {item}")