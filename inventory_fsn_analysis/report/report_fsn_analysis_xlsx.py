# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, _


class FsnAnalysisReportXlsx(models.AbstractModel):
    _name = 'report.inventory_fsn_analysis.report_fsn_analysis_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, stock):
        bold = workbook.add_format({'bold': True})
        date_style = workbook.add_format({'text_wrap': True, 'num_format': 'mm-dd-yyyy', 'text_wrap': True})
        table_header_left = workbook.add_format({'bg_color': '#ADADAD', 'align': 'left', 'font_size': 12, 'bold': True})
        table_row_left = workbook.add_format(
            {'align': 'left', 'font_size': 12, 'border': 1, 'text_wrap': True, 'border_color': '#ADADAD'})
        format1 = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 22, 'bg_color': '#ADADAD'})
        format2 = workbook.add_format({'align': 'center'})
        format3 = workbook.add_format({'font_size': 14, 'font_color': 'blue', 'align': 'center', 'bold': True})
        format6 = workbook.add_format({'bold': True, 'align': 'right'})
        format7 = workbook.add_format(
            {'font_size': 12, 'border': 1, 'text_wrap': True, 'align': 'right', 'border_color': '#ADADAD'})
        format8 = workbook.add_format({'text_wrap': True})
        format9 = workbook.add_format({'align': 'right'})

        for obj in stock:
            sheet = workbook.add_worksheet()
            sheet.set_column('I:I', 13)
            sheet.set_column('F:F', 23)
            sheet.set_column('K:K', 12)
            sheet.set_column('G:G', 23)
            sheet.set_column('J:J', 15)
            sheet.set_column('H:H', 14)
            sheet.set_column('L:L', 15)
            sheet.set_column('M:M', 18)

            row = 3
            sheet.set_row(3, 25)
            sheet.merge_range('F4:M4', 'Inventory FSN Analysis', format1)

            row += 2
            sheet.write(row, 7, 'Duration', format6)
            duration = f"{obj.start_date} - {obj.end_date}"
            sheet.merge_range('I6:J6', duration, date_style)

            row += 2
            sheet.write(row, 5, 'Warehouse', bold)
            sheet.write(row, 6, obj.warehouse_id.name)

            sheet.write(row, 9, 'Location', bold)
            sheet.write(row, 10, obj.location_id.display_name)

            row_count_cat = 9
            if obj.product_category:
                row += 1
                sheet.write(row, 5, 'Product Category', bold)
                for categ in obj.product_category:
                    sheet.merge_range(f'G{row_count_cat}:H{row_count_cat}', categ.display_name, format8)
                    row_count_cat += 1

            row_count_pro = 9
            if obj.product_ids:
                row = 8
                sheet.write(row, 9, 'Product', bold)
                for item in obj.product_ids:
                    sheet.merge_range(f'K{row_count_pro}:M{row_count_pro}', item.display_name, format8)
                    row_count_pro += 1
                row += 1

            row = row_count_pro + 1 if row_count_pro > row_count_cat else row_count_cat + 1
            sheet.write(row, 9, 'Fast Moving', bold)
            sheet.write(row, 10, obj.fast_moving, format9)

            row += 1
            fsn = dict(self.env['inventory.fsn.analysis']._fields['fsn_classification'].selection).get(
                stock[0].fsn_classification)
            sheet.write(row, 5, 'FNS Classification', bold)
            sheet.write(row, 6, fsn)

            sheet.write(row, 9, 'Slow Moving', bold)
            sheet.write(row, 10, obj.slow_moving, format9)

            row += 1
            sheet.write(row, 9, 'Non Moving', bold)
            sheet.write(row, 10, obj.non_moving, format9)

            row += 2
            sheet.write(row, 7, 'Opening Stock', format2)
            sheet.write(row, 8, 'Closing Stock', format2)

            row += 1
            sheet.write(row, 7, obj.total_opening_stock, format3)
            sheet.write(row, 8, obj.total_closing_stock, format3)

            row += 2
            sheet.write(row, 5, 'Product', table_header_left)
            sheet.write(row, 6, 'Product Category', table_header_left)
            sheet.write(row, 7, 'Opening Stock', table_header_left)
            sheet.write(row, 8, 'Closing Stock', table_header_left)
            sheet.write(row, 9, 'Average Stock', table_header_left)
            sheet.write(row, 10, 'Sale', table_header_left)
            sheet.write(row, 11, 'Turnover Ratio', table_header_left)
            sheet.write(row, 12, 'FSN Classification', table_header_left)

            row += 1
            for line in obj.sm_lines:
                sheet.write(row, 5, line.product_id.display_name, table_row_left)
                sheet.write(row, 6, line.product_category.display_name, table_row_left)
                sheet.write(row, 7, line.opening_stock, format7)
                sheet.write(row, 8, line.closing_stock, format7)
                sheet.write(row, 9, line.average_stock, format7)
                sheet.write(row, 10, line.sale, format7)
                sheet.write(row, 11, line.turnover_ratio, format7)
                sheet.write(row, 12, line.fsn, table_row_left)
                row += 1
