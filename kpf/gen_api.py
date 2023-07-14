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
def get_membership_details(customer_name):
	if frappe.db.exists("Customer", {"name": customer_name}):
		cust = frappe.get_doc("Customer",customer_name)
		if cust.is_member_customer == 1:
			member_details = frappe.db.sql('''select name,customer_type,customer_group,identification_number,gender,marital_status,
									member_category,race,occupation,register_location,member_home_address,email,phone_number
									member_mailing_address,credit_limit,remaining_balance,points,points_expiry_date
									from `tabCustomer` where name = %s; ''',(customer_name),as_dict=1 )
			for m in member_details:
				m["error"] = False

			return member_details							
		else:
			response = [] 
			msg = {
				"error": True,
				"message": "Customer is not Member Customer"
			}
			response.append(msg)
			return response
	else:
		response = [] 
		msg = {
			"error": True,
			"message": "Customer not exist of this Name"
		}
		response.append(msg)
		return response


@frappe.whitelist()
def update_credit_limit_points_of_member(customer_name,remaining_balance=None,points=None):
	if frappe.db.exists("Customer", {"name": customer_name}):
		cust = frappe.get_doc("Customer",customer_name)
		if cust.is_member_customer == 1:
			if customer_name and remaining_balance and points:
				SETfilters = {
					"active": 1
				}
				days = frappe.db.get_value("Point Conversion Setup", SETfilters, "days")
				doc = frappe.get_doc("Customer", customer_name)
				doc.remaining_balance = remaining_balance
				doc.points = points
				doc.points_expiry_date = datetime.now().date() + timedelta(days=days)
				doc.save()

				response = [] 
				msg = {
					"error": False,
					"message": "Remaining Balance and Points of Member updated successfully"
				}
				response.append(msg)
				return response
			elif customer_name and remaining_balance:
				doc = frappe.get_doc("Customer", customer_name)
				doc.remaining_balance = remaining_balance
				doc.save()

				response = [] 
				msg = {
					"error": False,
					"message": "Remaining Balance of Member updated successfully"
				}
				response.append(msg)
				return response
			elif customer_name and points:
				SETfilters = {
					"active": 1
				}
				days = frappe.db.get_value("Point Conversion Setup", SETfilters, "days")
				doc = frappe.get_doc("Customer", customer_name)
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
					"message": "Credit Limit and Points are None"
				}
				response.append(msg)
				return response
		else:
			response = [] 
			msg = {
				"error": True,
				"message": "Customer is not Member Customer"
			}
			response.append(msg)
			return response
	else:
		response = [] 
		msg = {
			"error": True,
			"message": "Customer not exist of this Name"
		}
		response.append(msg)
		return response			


@frappe.whitelist()
def get_stock_details(warehouse):
	data = frappe.db.sql(f'''select b.item_code,b.warehouse,b.actual_qty,b.stock_uom,b.valuation_rate,b.stock_value,p.price_list_rate
				from `tabBin` as b LEFT JOIN `tabItem Price` as p ON b.item_code = p.item_code and p.selling = 1
				where b.warehouse='{warehouse}'; ''',as_dict=1 )
	return data


@frappe.whitelist()
def get_items_master():
	items = frappe.db.sql('''select i.item_code,i.item_name,i.is_discounted_item,i.item_group,i.stock_uom,i.purchase_uom,i.sales_uom,i.end_of_life,
				p.price_list_rate,b.barcode,b.barcode_type
				 	from `tabItem` as i LEFT JOIN `tabItem Price` as p ON i.item_code = p.item_code and p.selling = 1
				LEFT JOIN `tabItem Barcode` as b ON i.item_code = b.parent; ''',as_dict=1 )
				  
	return items

@frappe.whitelist()
def get_selling_price():
	items = frappe.db.sql('''select item_code,price_list_rate
				 from `tabItem Price` where selling =1 ; ''',as_dict=1 )
				  
	return items
	
@frappe.whitelist()
def get_customer_details():
	customers = frappe.db.sql('''select name as id,customer_name,customer_type,customer_group,territory,is_member_customer,
					identification_number,marital_status,member_category,race,occupation,register_location,email,phone_number,
					member_home_address,member_mailing_address,credit_limit,remaining_balance,points,points_expiry_date
				 	from `tabCustomer` where disabled = 0;''',as_dict=1 )
				  
	return customers

@frappe.whitelist()
def promotion_list():
	sql_query = """
				SELECT `name`,`apply_on`,`mixed_conditions`, `is_cumulative`,`apply_rule_on_other`,`other_item_code`,`other_item_group`,`other_brand`,
					`selling`,`buying`,`applicable_for`,`valid_from`,`valid_upto`,`company`,`currency`
				FROM `tabPromotion`
				WHERE `disable` = 0
				"""			

	promotion_records = frappe.db.sql(sql_query,as_dict=True)

	if promotion_records:
		for pr in promotion_records:
			if pr.apply_on == "Item Code":
				sql_query = """
						SELECT `item_code`,`uom`
						FROM `tabPricing Rule Item Code`
						WHERE `parent` = %(parent)s
						"""

				# Prepare the query parameters
				query_params = {
					'parent': pr.name
				}

				# Execute the SQL query
				apply_on_items = frappe.db.sql(sql_query, query_params, as_dict=True)

				pr["apply_on_items"] = apply_on_items
			elif pr.apply_on == "Item Group":
				sql_query = """
						SELECT `item_group`,`uom`
						FROM `tabPricing Rule Item Group`
						WHERE `parent` = %(parent)s
						"""

				# Prepare the query parameters
				query_params = {
					'parent': pr.name
				}

				# Execute the SQL query
				apply_on_item_groups = frappe.db.sql(sql_query, query_params, as_dict=True)

				pr["apply_on_item_groups"] = apply_on_item_groups
			elif pr.apply_on == "Brand":
				sql_query = """
						SELECT `brand`,`uom`
						FROM `tabPricing Rule Brand`
						WHERE `parent` = %(parent)s
						"""

				# Prepare the query parameters
				query_params = {
					'parent': pr.name
				}

				# Execute the SQL query
				apply_on_item_brands = frappe.db.sql(sql_query, query_params, as_dict=True)

				pr["apply_on_item_brands"] = apply_on_item_brands	

			if pr.applicable_for:
				if pr.applicable_for == "Customer":
					sql_query = """
							SELECT `customer`
							FROM `tabCustomer Item`
							WHERE `parent` = %(parent)s
							"""

					# Prepare the query parameters
					query_params = {
						'parent': pr.name
					}

					# Execute the SQL query
					applicable_for_customers = frappe.db.sql(sql_query, query_params, as_dict=True)

					pr["applicable_for_customers"] = applicable_for_customers
				elif pr.applicable_for == "Customer Group":
					sql_query = """
							SELECT `customer_group`
							FROM `tabCustomer Group Item`
							WHERE `parent` = %(parent)s
							"""

					# Prepare the query parameters
					query_params = {
						'parent': pr.name
					}

					# Execute the SQL query
					applicable_for_customer_groups = frappe.db.sql(sql_query, query_params, as_dict=True)

					pr["applicable_for_customer_groups"] = applicable_for_customer_groups
				elif pr.applicable_for == "Territory":
					sql_query = """
							SELECT `territory`
							FROM `tabTerritory Item`
							WHERE `parent` = %(parent)s
							"""

					# Prepare the query parameters
					query_params = {
						'parent': pr.name
					}

					# Execute the SQL query
					applicable_for_territorys = frappe.db.sql(sql_query, query_params, as_dict=True)

					pr["applicable_for_territorys"] = applicable_for_territorys
				elif pr.applicable_for == "Sales Partner":
					sql_query = """
							SELECT `sales_partner`
							FROM `tabSales Partner Item`
							WHERE `parent` = %(parent)s
							"""

					# Prepare the query parameters
					query_params = {
						'parent': pr.name
					}

					# Execute the SQL query
					applicable_for_sales_partners = frappe.db.sql(sql_query, query_params, as_dict=True)

					pr["applicable_for_sales_partners"] = applicable_for_sales_partners
				elif pr.applicable_for == "Campaign":
					sql_query = """
							SELECT `campaign`
							FROM `tabCampaign Item`
							WHERE `parent` = %(parent)s
							"""

					# Prepare the query parameters
					query_params = {
						'parent': pr.name
					}

					# Execute the SQL query
					applicable_for_campaigns = frappe.db.sql(sql_query, query_params, as_dict=True)

					pr["applicable_for_campaigns"] = applicable_for_campaigns
				elif pr.applicable_for == "Supplier":
					sql_query = """
							SELECT `supplier`
							FROM `tabSupplier Item`
							WHERE `parent` = %(parent)s
							"""

					# Prepare the query parameters
					query_params = {
						'parent': pr.name
					}

					# Execute the SQL query
					applicable_for_suppliers = frappe.db.sql(sql_query, query_params, as_dict=True)

					pr["applicable_for_suppliers"] = applicable_for_suppliers
				elif pr.applicable_for == "Supplier Group":
					sql_query = """
							SELECT `supplier_group`
							FROM `tabSupplier Group Item`
							WHERE `parent` = %(parent)s
							"""

					# Prepare the query parameters
					query_params = {
						'parent': pr.name
					}

					# Execute the SQL query
					applicable_for_supplier_groups = frappe.db.sql(sql_query, query_params, as_dict=True)

					pr["applicable_for_supplier_groupss"] = applicable_for_supplier_groups

			sql_query = """
					SELECT `rule_description`,`min_qty`,`max_qty`,`min_amount`,`max_amount`,`rate_or_discount`,`rate`,`discount_amount`,
					`discount_percentage`,`warehouse`
					FROM `tabPromotional Scheme Price Discount`
					WHERE `parent` = %(parent)s AND disable = 0
					"""

			# Prepare the query parameters
			query_params = {
				'parent': pr.name
			}

			# Execute the SQL query
			price_discount_slabs = frappe.db.sql(sql_query, query_params, as_dict=True)

			if price_discount_slabs:
				pr["price_discount_slabs"] = price_discount_slabs

			sql_query = """
					SELECT `rule_description`,`min_qty`,`max_qty`,`min_amount`,`max_amount`,`same_item`,`free_item`,`free_qty`,
					`free_item_uom`,`free_item_rate`,`warehouse`
					FROM `tabPromotional Scheme Product Discount`
					WHERE `parent` = %(parent)s AND disable = 0
					"""

			# Prepare the query parameters
			query_params = {
				'parent': pr.name
			}

			# Execute the SQL query
			product_discount_slabs = frappe.db.sql(sql_query, query_params, as_dict=True)

			if product_discount_slabs:
				pr["product_discount_slabs"] = product_discount_slabs

	return promotion_records