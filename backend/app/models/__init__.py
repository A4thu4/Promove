try:
    from app.db.session import Base
except ImportError:
    from backend.app.db.session import Base

from .user import User
from .history import History
