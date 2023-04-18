"""empty init

Revision ID: e80e6802bfb4
Revises: 
Create Date: 2023-03-15 12:37:34.129530

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e80e6802bfb4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade(engine_name: str) -> None:
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name: str) -> None:
    globals()["downgrade_%s" % engine_name]()





def upgrade_prod_engine() -> None:
    pass


def downgrade_prod_engine() -> None:
    pass


def upgrade_dev_engine() -> None:
    pass


def downgrade_dev_engine() -> None:
    pass

