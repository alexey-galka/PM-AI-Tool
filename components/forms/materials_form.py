import streamlit as st


def render_materials_form():
    """Render materials form (articles and tasks) with delete functionality"""

    # ==================== ARTICLES SECTION ====================
    st.markdown("**Articles and links**")

    if 'articles_list' not in st.session_state:
        st.session_state.articles_list = [{"title": "", "url": ""}]

    if 'articles_to_delete' not in st.session_state:
        st.session_state.articles_to_delete = [
            False] * len(st.session_state.articles_list)

    # Sync delete flags
    if len(st.session_state.articles_to_delete) != len(st.session_state.articles_list):
        st.session_state.articles_to_delete = [
            False] * len(st.session_state.articles_list)

    updated_articles = []
    for i, article in enumerate(st.session_state.articles_list):
        col1, col2, col3 = st.columns([2, 3, 1])
        with col1:
            title = st.text_input("Title", value=article.get('title', ''),
                                  key=f"article_title_{i}", label_visibility="collapsed")
        with col2:
            url = st.text_input("Link", value=article.get('url', ''),
                                key=f"article_url_{i}", label_visibility="collapsed")
        with col3:
            delete_flag = st.checkbox("Delete", key=f"del_article_check_{i}",
                                      value=st.session_state.articles_to_delete[i] if i < len(st.session_state.articles_to_delete) else False)
            if i < len(st.session_state.articles_to_delete):
                st.session_state.articles_to_delete[i] = delete_flag

        if not st.session_state.articles_to_delete[i]:
            updated_articles.append({"title": title, "url": url})

    st.session_state.articles_list = updated_articles
    st.session_state.articles_to_delete = [False] * len(updated_articles)

    col1, col2 = st.columns(2)
    with col1:
        if st.form_submit_button("Add article", width='stretch'):
            st.session_state.articles_list.append({"title": "", "url": ""})
            st.session_state.articles_to_delete = [
                False] * len(st.session_state.articles_list)
            st.rerun()
    with col2:
        if len(st.session_state.articles_list) > 0 and st.form_submit_button("Delete marked articles", width='stretch'):
            # Articles already filtered above
            st.rerun()

    # ==================== TASKS SECTION ====================
    st.divider()
    st.markdown("**Tasks (backlog)**")

    # AI button for tasks generation
    from services.tasks_service import render_ai_tasks_button

    if 'tasks_list' not in st.session_state:
        st.session_state.tasks_list = [{"title": "", "description": ""}]

    if 'tasks_to_delete' not in st.session_state:
        st.session_state.tasks_to_delete = [
            False] * len(st.session_state.tasks_list)

    # Sync delete flags
    if len(st.session_state.tasks_to_delete) != len(st.session_state.tasks_list):
        st.session_state.tasks_to_delete = [
            False] * len(st.session_state.tasks_list)

    updated_tasks = []
    for i, task in enumerate(st.session_state.tasks_list):
        col1, col2, col3 = st.columns([2, 3, 1])
        with col1:
            title = st.text_input("Task title", value=task.get('title', ''),
                                  key=f"task_title_{i}", label_visibility="collapsed")
        with col2:
            description = st.text_input("Description", value=task.get('description', ''),
                                        key=f"task_desc_{i}", label_visibility="collapsed")
        with col3:
            delete_flag = st.checkbox("Delete", key=f"del_task_check_{i}",
                                      value=st.session_state.tasks_to_delete[i] if i < len(st.session_state.tasks_to_delete) else False)
            if i < len(st.session_state.tasks_to_delete):
                st.session_state.tasks_to_delete[i] = delete_flag

        if not st.session_state.tasks_to_delete[i]:
            updated_tasks.append({"title": title, "description": description})

    st.session_state.tasks_list = updated_tasks
    st.session_state.tasks_to_delete = [False] * len(updated_tasks)

    col1, col2 = st.columns(2)
    with col1:
        if st.form_submit_button("Add task", width='stretch'):
            st.session_state.tasks_list.append(
                {"title": "", "description": ""})
            st.session_state.tasks_to_delete = [
                False] * len(st.session_state.tasks_list)
            st.rerun()
    with col2:
        if len(st.session_state.tasks_list) > 0 and st.form_submit_button("Delete marked tasks", width='stretch'):
            # Tasks already filtered above
            st.rerun()

    return st.session_state.articles_list, st.session_state.tasks_list


def render_edit_materials_form():
    """Render materials form for editing with delete functionality"""

    # ==================== ARTICLES SECTION ====================
    st.markdown("**Articles and links**")

    if 'edit_articles_list' not in st.session_state:
        st.session_state.edit_articles_list = []

    if 'edit_articles_to_delete' not in st.session_state:
        st.session_state.edit_articles_to_delete = []

    if not st.session_state.edit_articles_list:
        st.info("No articles. Click 'Add article'")
        if st.form_submit_button("Add first article", width='stretch'):
            st.session_state.edit_articles_list.append(
                {"title": "", "url": ""})
            st.session_state.edit_articles_to_delete = [
                False] * len(st.session_state.edit_articles_list)
            st.rerun()
    else:
        # Sync delete flags
        if len(st.session_state.edit_articles_to_delete) != len(st.session_state.edit_articles_list):
            st.session_state.edit_articles_to_delete = [
                False] * len(st.session_state.edit_articles_list)

        updated_articles = []
        for i, article in enumerate(st.session_state.edit_articles_list):
            col1, col2, col3 = st.columns([2, 3, 1])
            with col1:
                title = st.text_input("Title", value=article.get('title', ''),
                                      key=f"edit_article_title_{i}", label_visibility="collapsed")
            with col2:
                url = st.text_input("Link", value=article.get('url', ''),
                                    key=f"edit_article_url_{i}", label_visibility="collapsed")
            with col3:
                delete_flag = st.checkbox("Delete", key=f"del_edit_article_check_{i}",
                                          value=st.session_state.edit_articles_to_delete[i] if i < len(st.session_state.edit_articles_to_delete) else False)
                if i < len(st.session_state.edit_articles_to_delete):
                    st.session_state.edit_articles_to_delete[i] = delete_flag

            if not st.session_state.edit_articles_to_delete[i]:
                updated_articles.append({"title": title, "url": url})

        st.session_state.edit_articles_list = updated_articles
        st.session_state.edit_articles_to_delete = [
            False] * len(updated_articles)

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Add article", width='stretch'):
                st.session_state.edit_articles_list.append(
                    {"title": "", "url": ""})
                st.session_state.edit_articles_to_delete = [
                    False] * len(st.session_state.edit_articles_list)
                st.rerun()
        with col2:
            if len(st.session_state.edit_articles_list) > 0 and st.form_submit_button("Delete marked articles", width='stretch'):
                st.rerun()

    # ==================== TASKS SECTION ====================
    st.divider()
    st.markdown("**Tasks (backlog)**")

    if 'edit_tasks_list' not in st.session_state:
        st.session_state.edit_tasks_list = []

    if 'edit_tasks_to_delete' not in st.session_state:
        st.session_state.edit_tasks_to_delete = []

    if not st.session_state.edit_tasks_list:
        st.info("No tasks. Click 'Add task'")
        if st.form_submit_button("Add first task", width='stretch'):
            st.session_state.edit_tasks_list.append(
                {"title": "", "description": ""})
            st.session_state.edit_tasks_to_delete = [
                False] * len(st.session_state.edit_tasks_list)
            st.rerun()
    else:
        # Sync delete flags
        if len(st.session_state.edit_tasks_to_delete) != len(st.session_state.edit_tasks_list):
            st.session_state.edit_tasks_to_delete = [
                False] * len(st.session_state.edit_tasks_list)

        updated_tasks = []
        for i, task in enumerate(st.session_state.edit_tasks_list):
            col1, col2, col3 = st.columns([2, 3, 1])
            with col1:
                title = st.text_input("Task title", value=task.get('title', ''),
                                      key=f"edit_task_title_{i}", label_visibility="collapsed")
            with col2:
                description = st.text_input("Description", value=task.get('description', ''),
                                            key=f"edit_task_desc_{i}", label_visibility="collapsed")
            with col3:
                delete_flag = st.checkbox("Delete", key=f"del_edit_task_check_{i}",
                                          value=st.session_state.edit_tasks_to_delete[i] if i < len(st.session_state.edit_tasks_to_delete) else False)
                if i < len(st.session_state.edit_tasks_to_delete):
                    st.session_state.edit_tasks_to_delete[i] = delete_flag

            if not st.session_state.edit_tasks_to_delete[i]:
                updated_tasks.append(
                    {"title": title, "description": description})

        st.session_state.edit_tasks_list = updated_tasks
        st.session_state.edit_tasks_to_delete = [False] * len(updated_tasks)

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Add task", width='stretch'):
                st.session_state.edit_tasks_list.append(
                    {"title": "", "description": ""})
                st.session_state.edit_tasks_to_delete = [
                    False] * len(st.session_state.edit_tasks_list)
                st.rerun()
        with col2:
            if len(st.session_state.edit_tasks_list) > 0 and st.form_submit_button("Delete marked tasks", width='stretch'):
                st.rerun()

    return st.session_state.edit_articles_list, st.session_state.edit_tasks_list
