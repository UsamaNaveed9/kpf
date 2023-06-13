import frappe
from frappe.utils import today, get_first_day, get_last_day, getdate
from datetime import date, timedelta, datetime

@frappe.whitelist()
def get_point_conversion_setup():
	setup = frappe.db.sql('''select name,posting_date,active,shopping_amount_for_points,points_on_shopping_amount,
							points_for_amount,amount_on_points,days as expiry_in_days
							from `tabPoint Conversion Setup` where active = 1; ''',as_dict=1 )
				  
	return setup

@frappe.whitelist()
def get_membership_details(identification_number):
	member_details = frappe.db.sql('''select name as id,member_name,identification_number,gender,marital_status,member_group,
							member_category,race,occupation,email,phone_number,register_location,member_home_address,
							member_mailing_address,credit_limit,points,points_expiry_date
							from `tabMembership` where identification_number = %s; ''',(identification_number),as_dict=1 )
				  
	return member_details    

@frappe.whitelist()
def update_credit_limit_points_of_member(identification_number,credit_limit=None,points=None):
	if identification_number and credit_limit and points:
		if frappe.db.exists("Membership", {"identification_number": identification_number}):
			filters = {
				"identification_number": identification_number
			}
			name = frappe.db.get_value("Membership", filters, "name")
			SETfilters = {
				"active": 1
			}
			days = frappe.db.get_value("Point Conversion Setup", SETfilters, "days")
			doc = frappe.get_doc("Membership", name)
			doc.credit_limit = credit_limit
			doc.points = points
			doc.points_expiry_date = datetime.now().date() + timedelta(days=days)
			doc.save()

			response = [] 
			msg = {
				"error": False,
				"message": "Credit Limit and Points of Member updated successfully"
			}
			response.append(msg)
			return response
		else:
			response = [] 
			msg = {
				"error": True,
				"message": "Membership record does not exist on this Identification Number"
			}
			response.append(msg)
			return response
	elif identification_number and credit_limit:
		if frappe.db.exists("Membership", {"identification_number": identification_number}):
			filters = {
				"identification_number": identification_number
			}
			name = frappe.db.get_value("Membership", filters, "name")
			doc = frappe.get_doc("Membership", name)
			doc.credit_limit = credit_limit
			doc.save()

			response = [] 
			msg = {
				"error": False,
				"message": "Credit Limit of Member updated successfully"
			}
			response.append(msg)
			return response
		else:
			response = [] 
			msg = {
				"error": True,
				"message": "Membership record does not exist on this Identification Number"
			}
			response.append(msg)
			return response
	elif identification_number and points:
		if frappe.db.exists("Membership", {"identification_number": identification_number}):
			filters = {
				"identification_number": identification_number
			}
			name = frappe.db.get_value("Membership", filters, "name")
			SETfilters = {
				"active": 1
			}
			days = frappe.db.get_value("Point Conversion Setup", SETfilters, "days")
			doc = frappe.get_doc("Membership", name)
			doc.points = points
			doc.points_expiry_date = datetime.now().date() + timedelta(days=days)
			doc.save()

			response = [] 
			msg = {
				"error": False,
				"message": "Points of Member updated successfully"
			}
			response.append(msg)
			return response
		else:
			response = [] 
			msg = {
				"error": True,
				"message": "Membership record does not exist on this Identification Number"
			}
			response.append(msg)
			return response
	else:
		response = [] 
		msg = {
			"error": True,
			"message": "Credit Limit and Points are None"
		}
		response.append(msg)
		return response


