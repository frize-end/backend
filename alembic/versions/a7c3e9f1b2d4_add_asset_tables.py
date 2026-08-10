"""add asset tables

Revision ID: a7c3e9f1b2d4
Revises: bda93baefd22
Create Date: 2026-08-10 23:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7c3e9f1b2d4'
down_revision: Union[str, Sequence[str], None] = 'bda93baefd22'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - 创建资产分类表和资产表"""
    # 资产分类表
    op.create_table(
        'asset_categories',
        sa.Column('id', sa.Integer(), nullable=False, comment='分类ID'),
        sa.Column('name', sa.String(length=64), nullable=False, comment='分类名称'),
        sa.Column('code', sa.String(length=32), nullable=False, comment='分类编码，用于资产编号前缀'),
        sa.Column('parent_id', sa.Integer(), nullable=True, comment='父分类ID，支持二级分类'),
        sa.Column('sort', sa.Integer(), nullable=True, comment='排序权重，数字越小越靠前'),
        sa.Column('is_delete', sa.SmallInteger(), nullable=True, comment='是否删除：0正常 1已删除'),
        sa.Column('create_time', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.ForeignKeyConstraint(['parent_id'], ['asset_categories.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # 资产表
    op.create_table(
        'assets',
        sa.Column('id', sa.Integer(), nullable=False, comment='资产ID'),
        sa.Column('asset_code', sa.String(length=32), nullable=False, comment='资产编号，业务唯一键'),
        sa.Column('name', sa.String(length=128), nullable=False, comment='资产名称'),
        sa.Column('category_id', sa.Integer(), nullable=False, comment='所属分类ID'),
        sa.Column('brand', sa.String(length=64), nullable=True, comment='品牌'),
        sa.Column('model', sa.String(length=64), nullable=True, comment='型号规格'),
        sa.Column('status', sa.String(length=16), nullable=False, comment='状态：idle闲置/in_use使用中/maintenance维修中/scrapped已报废'),
        sa.Column('purchase_date', sa.Date(), nullable=True, comment='购入日期'),
        sa.Column('purchase_price', sa.Numeric(precision=10, scale=2), nullable=True, comment='购入价格'),
        sa.Column('location', sa.String(length=128), nullable=True, comment='存放位置'),
        sa.Column('current_user_id', sa.Integer(), nullable=True, comment='当前使用人ID'),
        sa.Column('remark', sa.Text(), nullable=True, comment='备注'),
        sa.Column('is_delete', sa.SmallInteger(), nullable=True, comment='是否删除：0正常 1已删除'),
        sa.Column('create_time', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.ForeignKeyConstraint(['category_id'], ['asset_categories.id'], ),
        sa.ForeignKeyConstraint(['current_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('asset_code')
    )
    op.create_index(op.f('ix_assets_asset_code'), 'assets', ['asset_code'], unique=True)


def downgrade() -> None:
    """Downgrade schema - 删除资产表和分类表"""
    op.drop_index(op.f('ix_assets_asset_code'), table_name='assets')
    op.drop_table('assets')
    op.drop_table('asset_categories')
