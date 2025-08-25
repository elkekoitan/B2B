-- Migration: create_rls_policies
-- Created at: 1755955522

-- RLS Policies for data security

-- Companies policies
CREATE POLICY "Users can view companies" ON companies 
FOR SELECT USING (true); -- Companies are public for discovery

CREATE POLICY "Users can update their own company" ON companies
FOR UPDATE USING (
  id IN (
    SELECT company_id FROM users WHERE auth_user_id = auth.uid()
  )
);

-- Users policies
CREATE POLICY "Users can view users from same company" ON users
FOR SELECT USING (
  company_id IN (
    SELECT company_id FROM users WHERE auth_user_id = auth.uid()
  )
);

CREATE POLICY "Users can update their own profile" ON users
FOR UPDATE USING (auth_user_id = auth.uid());

CREATE POLICY "New users can insert their profile" ON users
FOR INSERT WITH CHECK (auth_user_id = auth.uid());

-- Suppliers policies
CREATE POLICY "Anyone can view verified suppliers" ON suppliers
FOR SELECT USING (verified = true);

CREATE POLICY "Suppliers can view their own profile" ON suppliers
FOR SELECT USING (
  company_id IN (
    SELECT company_id FROM users WHERE auth_user_id = auth.uid()
  )
);

CREATE POLICY "Suppliers can update their own profile" ON suppliers
FOR UPDATE USING (
  company_id IN (
    SELECT company_id FROM users WHERE auth_user_id = auth.uid()
  )
);

CREATE POLICY "New suppliers can create their profile" ON suppliers
FOR INSERT WITH CHECK (
  company_id IN (
    SELECT company_id FROM users WHERE auth_user_id = auth.uid()
  )
);

-- RFQs policies
CREATE POLICY "Users can view RFQs from their company or public RFQs" ON rfqs
FOR SELECT USING (
  company_id IN (
    SELECT company_id FROM users WHERE auth_user_id = auth.uid()
  ) OR status = 'published'
);

CREATE POLICY "Users can create RFQs for their company" ON rfqs
FOR INSERT WITH CHECK (
  requester_id = auth.uid() AND 
  company_id IN (
    SELECT company_id FROM users WHERE auth_user_id = auth.uid()
  )
);

CREATE POLICY "Users can update their own RFQs" ON rfqs
FOR UPDATE USING (requester_id = auth.uid());

-- Offers policies
CREATE POLICY "Users can view offers related to their RFQs or their offers" ON offers
FOR SELECT USING (
  rfq_id IN (
    SELECT id FROM rfqs WHERE requester_id = auth.uid()
  ) OR 
  supplier_id IN (
    SELECT id FROM suppliers WHERE company_id IN (
      SELECT company_id FROM users WHERE auth_user_id = auth.uid()
    )
  )
);

CREATE POLICY "Suppliers can create offers" ON offers
FOR INSERT WITH CHECK (
  supplier_id IN (
    SELECT id FROM suppliers WHERE company_id IN (
      SELECT company_id FROM users WHERE auth_user_id = auth.uid()
    )
  )
);

CREATE POLICY "Suppliers can update their own offers" ON offers
FOR UPDATE USING (
  supplier_id IN (
    SELECT id FROM suppliers WHERE company_id IN (
      SELECT company_id FROM users WHERE auth_user_id = auth.uid()
    )
  )
);

-- Email logs policies
CREATE POLICY "Users can view email logs related to their activities" ON email_logs
FOR SELECT USING (
  rfq_id IN (
    SELECT id FROM rfqs WHERE requester_id = auth.uid()
  ) OR
  offer_id IN (
    SELECT id FROM offers WHERE supplier_id IN (
      SELECT id FROM suppliers WHERE company_id IN (
        SELECT company_id FROM users WHERE auth_user_id = auth.uid()
      )
    )
  ) OR
  sender_email IN (
    SELECT email FROM users WHERE auth_user_id = auth.uid()
  )
);

-- Notifications policies
CREATE POLICY "Users can view their own notifications" ON notifications
FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can update their own notifications" ON notifications
FOR UPDATE USING (user_id = auth.uid());

-- Attachments policies
CREATE POLICY "Users can view attachments related to their RFQs or offers" ON attachments
FOR SELECT USING (
  rfq_id IN (
    SELECT id FROM rfqs WHERE requester_id = auth.uid()
  ) OR 
  offer_id IN (
    SELECT id FROM offers WHERE supplier_id IN (
      SELECT id FROM suppliers WHERE company_id IN (
        SELECT company_id FROM users WHERE auth_user_id = auth.uid()
      )
    )
  ) OR
  uploaded_by = auth.uid()
);

CREATE POLICY "Users can upload attachments" ON attachments
FOR INSERT WITH CHECK (uploaded_by = auth.uid());

-- RFQ invitations policies
CREATE POLICY "Users can view invitations related to their RFQs or company" ON rfq_invitations
FOR SELECT USING (
  rfq_id IN (
    SELECT id FROM rfqs WHERE requester_id = auth.uid()
  ) OR 
  supplier_id IN (
    SELECT id FROM suppliers WHERE company_id IN (
      SELECT company_id FROM users WHERE auth_user_id = auth.uid()
    )
  )
);

-- Awards policies
CREATE POLICY "Users can view awards related to their activities" ON awards
FOR SELECT USING (
  rfq_id IN (
    SELECT id FROM rfqs WHERE requester_id = auth.uid()
  ) OR 
  offer_id IN (
    SELECT id FROM offers WHERE supplier_id IN (
      SELECT id FROM suppliers WHERE company_id IN (
        SELECT company_id FROM users WHERE auth_user_id = auth.uid()
      )
    )
  )
);

CREATE POLICY "RFQ owners can create awards" ON awards
FOR INSERT WITH CHECK (
  selected_by = auth.uid() AND 
  rfq_id IN (
    SELECT id FROM rfqs WHERE requester_id = auth.uid()
  )
);;