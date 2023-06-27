# Copyright (c) 2023, smb and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	currency = frappe.get_cached_value(
		"Company", filters.company, "default_currency"
	)
	report_summary = get_report_summary(data,currency)
	return columns, data, None, None, report_summary

def get_columns(filters=None):
	return [
		{
			"fieldname": "cost_center",
			"label": _("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"width": 300,
		},
		{
			"fieldname": "cash_in",
			"label": _("Cash In"),
			"fieldtype": "Currency",
			"width": 200,
		},
		{
			"fieldname": "cash_out",
			"label": _("Cash Out"),
			"fieldtype": "Currency",
			"width": 200,
		},
		{
			"fieldname": "total_in_pc",
			"label": _("Total In Petty Cash"),
			"fieldtype": "Currency",
			"width": 200,
		},
	]

def get_data(filters=None):
	data = []
	cond = ""
	if filters.company:
		cond += "and company = '{0}'".format(filters.company)
	cost_center_list = frappe.db.sql("""select name as cost_center from `tabCost Center`
										where is_group = 0 {0}""".format(cond),as_dict=1)
	for row in cost_center_list:
		condition = ""
		condition += "and company = '{0}'".format(filters.company)
		entries = frappe.db.sql("""select sum(debit) as cash_in, sum(credit) as cash_out from `tabGL Entry`
								where account = "Cash - KPF" and posting_date >= '{0}' and posting_date <= '{1}' 
								and cost_center = '{2}' {3}""".format(filters.from_date,filters.to_date,row['cost_center'],condition),as_dict=1)								
		if entries:
			for entry in entries:
				entry['cost_center'] = row['cost_center']
				total_pc = frappe.db.sql("""select sum(debit + credit) as total_pc from `tabGL Entry`
								where voucher_type = "Journal Entry" and against = "Cash - KPF" and posting_date >= '{0}' and posting_date <= '{1}' 
								and cost_center = '{2}' {3}""".format(filters.from_date,filters.to_date,row['cost_center'],condition),as_dict=1)
				for tp in total_pc:
					entry['total_in_pc'] = tp['total_pc']
				data.append(entry)
	for d in data:
		if not d['cash_in']:
			d['cash_in'] = 0.0
		if not d['cash_out']:
			d['cash_out'] = 0.0	
		if not d['total_in_pc']:
			d['total_in_pc'] = 0.0	

	return data			

def get_report_summary(data,currency):
	total_cash, total_cash_in, total_cash_out, total_in_petty_cash = 0.0, 0.0, 0.0, 0.0
	frappe.errprint
	for row in data:
		total_cash += row['cash_in'] + row['cash_out']
		total_cash_in += row['cash_in']
		total_cash_out += row['cash_out']
		total_in_petty_cash += row['total_in_pc']
	
	total_cash_label = _("Total Cash")
	total_cash_in_label = _("Total Cash In")
	total_cash_out_label = _("Total Cash Out")
	total_in_petty_cash_label = _("Total In Petty Cash")

	return [
		{"value": total_cash, "label": total_cash_label , "datatype": "Currency", "currency": currency},
		{"value": total_cash_in, "label": total_cash_in_label, "datatype": "Currency", "currency": currency},
		{"value": total_cash_out, "label": total_cash_out_label , "datatype": "Currency", "currency": currency},
		{"value": total_in_petty_cash, "label": total_in_petty_cash_label, "datatype": "Currency", "currency": currency},
	]				
