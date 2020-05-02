from devpotato_bot.helpers import developer_only


@developer_only
def command_callback(_update, _context):
    """Generate error to be handled in error_handler"""
    assert not 'a banana'
