-- Migration: create_performance_indexes
-- Created at: 1755955491

-- Performance indexes for better query performance

-- Users table indexes
CREATE INDEX IF NOT EXISTS idx_users_auth_user_id ON users (auth_user_id);
CREATE INDEX IF NOT EXISTS idx_users_company_id ON users (company_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);

-- Companies table indexes
CREATE INDEX IF NOT EXISTS idx_companies_name ON companies (name);
CREATE INDEX IF NOT EXISTS idx_companies_email ON companies (email);

-- Suppliers table indexes
CREATE INDEX IF NOT EXISTS idx_suppliers_company_id ON suppliers (company_id);
CREATE INDEX IF NOT EXISTS idx_suppliers_verified ON suppliers (verified);
CREATE INDEX IF NOT EXISTS idx_suppliers_rating ON suppliers (rating);

-- RFQs table indexes
CREATE INDEX IF NOT EXISTS idx_rfqs_requester_id ON rfqs (requester_id);
CREATE INDEX IF NOT EXISTS idx_rfqs_company_id ON rfqs (company_id);
CREATE INDEX IF NOT EXISTS idx_rfqs_status ON rfqs (status);
CREATE INDEX IF NOT EXISTS idx_rfqs_category ON rfqs (category);
CREATE INDEX IF NOT EXISTS idx_rfqs_created_at ON rfqs (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_rfqs_deadline_date ON rfqs (deadline_date);

-- Offers table indexes
CREATE INDEX IF NOT EXISTS idx_offers_rfq_id ON offers (rfq_id);
CREATE INDEX IF NOT EXISTS idx_offers_supplier_id ON offers (supplier_id);
CREATE INDEX IF NOT EXISTS idx_offers_status ON offers (status);
CREATE INDEX IF NOT EXISTS idx_offers_created_at ON offers (created_at DESC);

-- Email logs table indexes
CREATE INDEX IF NOT EXISTS idx_email_logs_rfq_id ON email_logs (rfq_id);
CREATE INDEX IF NOT EXISTS idx_email_logs_offer_id ON email_logs (offer_id);
CREATE INDEX IF NOT EXISTS idx_email_logs_sender_email ON email_logs (sender_email);
CREATE INDEX IF NOT EXISTS idx_email_logs_recipient_email ON email_logs (recipient_email);
CREATE INDEX IF NOT EXISTS idx_email_logs_status ON email_logs (status);
CREATE INDEX IF NOT EXISTS idx_email_logs_sent_at ON email_logs (sent_at DESC);

-- Notifications table indexes
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications (user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications (read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications (created_at DESC);

-- Attachments table indexes
CREATE INDEX IF NOT EXISTS idx_attachments_rfq_id ON attachments (rfq_id);
CREATE INDEX IF NOT EXISTS idx_attachments_offer_id ON attachments (offer_id);
CREATE INDEX IF NOT EXISTS idx_attachments_uploaded_by ON attachments (uploaded_by);

-- RFQ invitations table indexes
CREATE INDEX IF NOT EXISTS idx_rfq_invitations_rfq_id ON rfq_invitations (rfq_id);
CREATE INDEX IF NOT EXISTS idx_rfq_invitations_supplier_id ON rfq_invitations (supplier_id);
CREATE INDEX IF NOT EXISTS idx_rfq_invitations_status ON rfq_invitations (status);

-- Awards table indexes
CREATE INDEX IF NOT EXISTS idx_awards_rfq_id ON awards (rfq_id);
CREATE INDEX IF NOT EXISTS idx_awards_offer_id ON awards (offer_id);
CREATE INDEX IF NOT EXISTS idx_awards_selected_by ON awards (selected_by);;