from warnings import deprecated
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'])