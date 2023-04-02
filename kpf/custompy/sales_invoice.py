import frappe
from frappe import _, msgprint
from frappe.model.document import Document

@frappe.whitelist()
def check_credit_limit(self, limit):
    if self.is_member_customer and self.use_credit_limit:
        limit = frappe.db.get_value("Member", {"customer": self.customer}, "credit_limit")
        if self.grand_total > limit:
            frappe.throw(_("Grand Total {0} is greater than Member Credit limit {1}").format(self.grand_total,limit)) 

@frappe.whitelist()
def update_credit_limit(self, method):
    if self.is_member_customer and self.use_credit_limit:
        mbr = frappe.get_doc('Member',self.customer)
        mbr.credit_limit = mbr.credit_limit - self.grand_total
        mbr.save()