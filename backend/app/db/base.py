# ============================================================
# FlowBoard — SQLAlchemy Declarative Base
# Todos os models herdam desta classe Base.
# ============================================================

from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import MetaData

# Convenção de nomenclatura para constraints do banco
# Isso garante que o Alembic gere nomes de constraints consistentes
# Sem isso, cada banco pode nomear constraints diferente → bugs em migrations
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """
    Base class para todos os models SQLAlchemy.
    
    - __tablename__: gerado automaticamente do nome da classe
    - metadata: usa naming convention para constraints consistentes
    """
    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Converte automaticamente o nome da classe para snake_case.
        Ex: UserProfile → user_profile
        """
        import re
        name = cls.__name__
        # Insere underscore antes de letras maiúsculas
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
        return name