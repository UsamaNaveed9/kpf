# Copyright (c) 2023, pukat and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class BlockUsers(Document):
	def on_submit(self):
		if self.action == "Block":
			for usr in self.users:
				doc = frappe.get_doc('User', usr.user)
				doc.enabled = 0
				doc.save()
