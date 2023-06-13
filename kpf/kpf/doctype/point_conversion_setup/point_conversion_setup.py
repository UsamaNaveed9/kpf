# Copyright (c) 2023, pukat and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PointConversionSetup(Document):
	def before_save(self):
		if self.active == 1 and frappe.db.exists(dict(doctype="Point Conversion Setup", active=1)):
			filters = {
				"active": 1
			}
			name = frappe.db.get_value("Point Conversion Setup", filters, "name")
			doc = frappe.get_doc("Point Conversion Setup", name)
			doc.db_set("active", 0)
			doc.save()


