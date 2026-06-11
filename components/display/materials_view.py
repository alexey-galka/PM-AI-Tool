import streamlit as st


def render_materials(project):
    """Display articles and tasks"""
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Articles")
        articles = project.get('articles', [])

        if not articles:
            st.info("No articles")
        else:
            for article in articles:
                title = article.get('title', 'Untitled')
                url = article.get('url', '')
                if url:
                    st.markdown(f"- [{title}]({url})")
                else:
                    st.write(f"- {title}")

    with col2:
        st.subheader("Tasks")
        tasks = project.get('tasks', [])

        if not tasks:
            st.info("No tasks")
        else:
            for task in tasks:
                status_emoji = {
                    'TODO': '',
                    'IN_PROGRESS': '',
                    'DONE': ''
                }.get(task.get('status', 'TODO'), '⭕')

                st.write(
                    f"{status_emoji} **{task.get('title', 'Untitled')}**")
                if task.get('description'):
                    st.caption(f"_{task.get('description')}_")