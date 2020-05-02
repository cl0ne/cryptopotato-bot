from contextlib import contextmanager


@contextmanager
def scoped_session(session_factory):
    """Auto-close session after exiting the scope."""
    session = session_factory()
    try:
        yield session
    except:
        session.rollback()
        raise
    finally:
        session.close()
