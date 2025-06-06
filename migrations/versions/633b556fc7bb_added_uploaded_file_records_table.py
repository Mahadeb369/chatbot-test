"""Added uploaded_file_records table

Revision ID: 633b556fc7bb
Revises: fb333b0dd8db
Create Date: 2025-03-20 09:14:06.048812

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '633b556fc7bb'
down_revision = 'fb333b0dd8db'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('media_property_occupancy_report',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('agency_related_to', sa.String(length=50), nullable=True),
    sa.Column('created_date', sa.Date(), nullable=True),
    sa.Column('offer_number', sa.String(length=50), nullable=True),
    sa.Column('property_name', sa.String(length=200), nullable=True),
    sa.Column('offer_vertical', sa.String(length=100), nullable=True),
    sa.Column('owner_new_vertical', sa.String(length=100), nullable=True),
    sa.Column('owner_full_name', sa.String(length=200), nullable=True),
    sa.Column('agency_or_direct', sa.String(length=200), nullable=True),
    sa.Column('agency_name', sa.String(length=500), nullable=True),
    sa.Column('brand_name', sa.String(length=500), nullable=True),
    sa.Column('client_name', sa.String(length=500), nullable=True),
    sa.Column('client_category', sa.String(length=100), nullable=True),
    sa.Column('is_gov', sa.String(length=20), nullable=True),
    sa.Column('finance_offer_type', sa.String(length=100), nullable=True),
    sa.Column('type_of_business', sa.String(length=100), nullable=True),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('media_property_occupancy_status',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('site', sa.String(length=300), nullable=False),
    sa.Column('ros_status', sa.String(length=50), nullable=True),
    sa.Column('site_details', sa.Text(), nullable=True),
    sa.Column('level', sa.String(length=50), nullable=True),
    sa.Column('package_name', sa.String(length=500), nullable=True),
    sa.Column('site_type', sa.String(length=500), nullable=True),
    sa.Column('lighting_type', sa.String(length=500), nullable=True),
    sa.Column('sitetype_info', sa.String(length=500), nullable=True),
    sa.Column('media_type', sa.String(length=500), nullable=True),
    sa.Column('width_feet', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('width_inches', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('height_feet', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('height_inches', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('color_bleed_area', sa.String(length=500), nullable=True),
    sa.Column('no_of_sites', sa.Integer(), nullable=True),
    sa.Column('active', sa.String(length=50), nullable=True),
    sa.Column('announcement_date', sa.Date(), nullable=True),
    sa.Column('expiration_date', sa.Date(), nullable=True),
    sa.Column('remarks', sa.String(length=200), nullable=True),
    sa.Column('material_code', sa.String(length=50), nullable=True),
    sa.Column('rate_card', sa.Integer(), nullable=True),
    sa.Column('type_of_display', sa.String(length=500), nullable=True),
    sa.Column('location', sa.String(length=500), nullable=True),
    sa.Column('sub_location', sa.String(length=500), nullable=True),
    sa.Column('landmark', sa.String(length=500), nullable=True),
    sa.Column('width', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('height', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('area', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('towards', sa.String(length=500), nullable=True),
    sa.Column('property', sa.String(length=500), nullable=True),
    sa.Column('sales_manager', sa.String(length=500), nullable=True),
    sa.Column('offer_status', sa.String(length=50), nullable=True),
    sa.Column('offer_number', sa.String(length=50), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('blocking_status', sa.String(length=50), nullable=True),
    sa.Column('advance_booking_status', sa.String(length=50), nullable=True),
    sa.Column('advance_book_start_date', sa.Date(), nullable=True),
    sa.Column('advance_book_end_date', sa.Date(), nullable=True),
    sa.Column('advance_book_client_name', sa.String(length=500), nullable=True),
    sa.Column('remaining_days', sa.Integer(), nullable=True),
    sa.Column('agency', sa.String(length=500), nullable=True),
    sa.Column('client_code', sa.BigInteger(), nullable=True),
    sa.Column('current_client', sa.String(length=500), nullable=True),
    sa.Column('category', sa.String(length=500), nullable=True),
    sa.Column('campaign_start_date', sa.Date(), nullable=True),
    sa.Column('campaign_end_date', sa.Date(), nullable=True),
    sa.Column('verification_comments', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('site')
    )
    op.create_table('report_test',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('agency_related_to', sa.String(length=50), nullable=True),
    sa.Column('created_date', sa.Date(), nullable=True),
    sa.Column('offer_number', sa.String(length=50), nullable=True),
    sa.Column('property_name', sa.String(length=200), nullable=True),
    sa.Column('offer_vertical', sa.String(length=100), nullable=True),
    sa.Column('owner_new_vertical', sa.String(length=100), nullable=True),
    sa.Column('owner_full_name', sa.String(length=200), nullable=True),
    sa.Column('agency_or_direct', sa.String(length=200), nullable=True),
    sa.Column('agency_name', sa.String(length=500), nullable=True),
    sa.Column('brand_name', sa.String(length=500), nullable=True),
    sa.Column('client_name', sa.String(length=500), nullable=True),
    sa.Column('client_category', sa.String(length=100), nullable=True),
    sa.Column('is_gov', sa.String(length=20), nullable=True),
    sa.Column('finance_offer_type', sa.String(length=100), nullable=True),
    sa.Column('type_of_business', sa.String(length=100), nullable=True),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('times_test',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('site', sa.String(length=300), nullable=False),
    sa.Column('ros_status', sa.String(length=50), nullable=True),
    sa.Column('site_details', sa.Text(), nullable=True),
    sa.Column('level', sa.String(length=50), nullable=True),
    sa.Column('package_name', sa.String(length=500), nullable=True),
    sa.Column('site_type', sa.String(length=500), nullable=True),
    sa.Column('lighting_type', sa.String(length=500), nullable=True),
    sa.Column('sitetype_info', sa.String(length=500), nullable=True),
    sa.Column('media_type', sa.String(length=500), nullable=True),
    sa.Column('width_feet', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('width_inches', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('height_feet', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('height_inches', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('color_bleed_area', sa.String(length=500), nullable=True),
    sa.Column('no_of_sites', sa.Integer(), nullable=True),
    sa.Column('active', sa.String(length=50), nullable=True),
    sa.Column('announcement_date', sa.Date(), nullable=True),
    sa.Column('expiration_date', sa.Date(), nullable=True),
    sa.Column('remarks', sa.String(length=200), nullable=True),
    sa.Column('material_code', sa.String(length=50), nullable=True),
    sa.Column('rate_card', sa.Integer(), nullable=True),
    sa.Column('type_of_display', sa.String(length=500), nullable=True),
    sa.Column('location', sa.String(length=500), nullable=True),
    sa.Column('sub_location', sa.String(length=500), nullable=True),
    sa.Column('landmark', sa.String(length=500), nullable=True),
    sa.Column('width', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('height', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('area', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('towards', sa.String(length=500), nullable=True),
    sa.Column('property', sa.String(length=500), nullable=True),
    sa.Column('sales_manager', sa.String(length=500), nullable=True),
    sa.Column('offer_status', sa.String(length=50), nullable=True),
    sa.Column('offer_number', sa.String(length=50), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('blocking_status', sa.String(length=50), nullable=True),
    sa.Column('advance_booking_status', sa.String(length=50), nullable=True),
    sa.Column('advance_book_start_date', sa.Date(), nullable=True),
    sa.Column('advance_book_end_date', sa.Date(), nullable=True),
    sa.Column('advance_book_client_name', sa.String(length=500), nullable=True),
    sa.Column('remaining_days', sa.Integer(), nullable=True),
    sa.Column('agency', sa.String(length=500), nullable=True),
    sa.Column('client_code', sa.BigInteger(), nullable=True),
    sa.Column('current_client', sa.String(length=500), nullable=True),
    sa.Column('category', sa.String(length=500), nullable=True),
    sa.Column('campaign_start_date', sa.Date(), nullable=True),
    sa.Column('campaign_end_date', sa.Date(), nullable=True),
    sa.Column('verification_comments', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('site')
    )
    op.create_table('uploaded_file_records',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('file_name', sa.String(length=500), nullable=True),
    sa.Column('file_path', sa.String(length=500), nullable=True),
    sa.Column('uploaded_at', sa.DateTime(), nullable=True),
    sa.Column('ip_address', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_ip_address',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ip_address', sa.String(length=100), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('ip_address')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_ip_address')
    op.drop_table('uploaded_file_records')
    op.drop_table('times_test')
    op.drop_table('report_test')
    op.drop_table('media_property_occupancy_status')
    op.drop_table('media_property_occupancy_report')
    # ### end Alembic commands ###
