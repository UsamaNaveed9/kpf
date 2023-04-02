# Copyright (c) 2023, pukat and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Member(Document):
	def before_save(self):
		if self.customer:
			doc = frappe.get_doc('Customer',self.customer)
			doc.is_member_customer = 1
			doc.save()

