"""Stream type classes for tap-exact."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_exact.client import ExactOnlineStream

from datetime import datetime

# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")
# TODO: - Override `UsersStream` and `GroupsStream` with your own stream definition.
#       - Copy-paste as many times as needed to create multiple stream types.


class SalesInvoicesStream(ExactOnlineStream):
    """Define custom stream."""

    name = "sales_invoices"
    primary_keys = ["InvoiceID"]
    replication_key = "Modified"
    date_fields = ['InvoiceDate', 'Modified', 'OrderDate']
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property(
            "InvoiceID",
            th.StringType,
            description="The unique identifier of the invoice"
        ),
        th.Property(
            "InvoiceDate",
            th.DateTimeType,
            description="The invoice date"
        ),
        th.Property(
            "InvoiceNumber",
            th.IntegerType,
            description="The invoice number"
        ),
        th.Property(
            "InvoiceTo",
            th.StringType,
            description="The customer whom the invoice is made for"
        ),
        th.Property(
            "InvoiceToName",
            th.StringType,
            description="The name of the customer whom the invoice is made for"
        ),
        th.Property(
            "OrderDate",
            th.DateTimeType,
            description="The order date"
        ),
        th.Property(
            "OrderedBy",
            th.StringType,
            description="The customer who made the order"
        ),
        th.Property(
            "OrderedByName",
            th.StringType,
            description="The name of the customer who made the order"
        ),
        th.Property(
            "Creator",
            th.StringType,
            description="The creator of the sales invoice"
        ),
        th.Property(
            "CreatorFullName",
            th.StringType,
            description="The name of the creator"
        ),
        th.Property(
            "Salesperson",
            th.StringType,
            description="The sales person of the sales invoice"
        ),
        th.Property(
            "SalespersonFullName",
            th.StringType,
            description="The name of the salesperson"
        ),
        th.Property(
            "AmountDC",
            th.NumberType,
            description="Amount in the default currency of the company"
        ),
        th.Property(
            "AmountDiscount",
            th.NumberType,
            description="Amount of discount given"
        ),
        th.Property(
            "VATAmountDC",
            th.NumberType,
            description="Amount of VAT in the default currency of the company"
        ),
        th.Property(
            "Modified",
            th.DateTimeType,
            description="Last modified date"
        ),
    ).to_dict()

    def get_path(self, context: Optional[dict]) -> str:
        """Return the path of the Exact API"""

        replication_key_value = self.get_starting_timestamp(context).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        path = "/salesinvoice/SalesInvoices?" \
            f"$filter={self.replication_key}%20ge%20datetime%27{replication_key_value}%27&" \
            "$select=InvoiceID,InvoiceDate,InvoiceNumber,InvoiceTo,InvoiceToName,OrderDate,OrderedBy,OrderedByName,Creator,CreatorFullName,Salesperson,SalespersonFullName,AmountDC,AmountDiscount,VATAmountDC,Modified"

        return path

class PurchaseInvoicesStream(ExactOnlineStream):
    """Define custom stream."""

    name = "purchase_invoices"
    primary_keys = ["ID"]
    replication_key = "Modified"
    date_fields = ['InvoiceDate', 'Modified', 'DueDate']
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property(
            "ID",
            th.StringType,
            description="The unique identifier of the invoice"
        ),
        th.Property(
            "InvoiceDate",
            th.DateTimeType,
            description="The invoice date"
        ),
        th.Property(
            "YourRef",
            th.StringType,
            description="The invoice number provided by the supplier"
        ),
        th.Property(
            "Supplier",
            th.StringType,
            description="The supplier who sent the invoice"
        ),
        th.Property(
            "Description",
            th.StringType,
            description="The description of the invoice"
        ),
        th.Property(
            "DueDate",
            th.DateTimeType,
            description="The due date"
        ),
        th.Property(
            "PaymentCondition",
            th.StringType,
            description="The code of the payment conditino that is used to calculate the due date and discount"
        ),
        th.Property(
            "Status",
            th.IntegerType,
            description="The code of the payment conditino that is used to calculate the due date and discount"
        ),
        th.Property(
            "Journal",
            th.StringType,
            description="The code of the purchase journal in which the invoice is entered"
        ),
        th.Property(
            "Amount",
            th.NumberType,
            description="Amount including VAT in the default currency of the company"
        ),
        th.Property(
            "VATAmount",
            th.NumberType,
            description="VAT Amount in the default currency of the company"
        ),
        th.Property(
            "Modified",
            th.DateTimeType,
            description="Last modified date"
        ),
    ).to_dict()

    def get_path(self, context: Optional[dict]) -> str:
        """Return the path of the Exact API"""

        replication_key_value = self.get_starting_timestamp(context).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        path = "/purchase/PurchaseInvoices?" \
            f"$filter={self.replication_key}%20ge%20datetime%27{replication_key_value}%27&" \
            "$select=ID,InvoiceDate,YourRef,Supplier,Description,DueDate,PaymentCondition,Status,Journal,Amount,VATAmount,Modified"

        return path

class GeneralLedgerAccountsStream(ExactOnlineStream):
    """Define custom stream."""

    name = "general_ledger_accounts"
    primary_keys = ["ID"]
    replication_key = "Modified"
    date_fields = ['Modified']
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property(
            "ID",
            th.StringType,
            description="The unique identifier of the account"
        ),
        th.Property(
            "Code",
            th.StringType,
            description="The unique code of the account"
        ),
        th.Property(
            "Description",
            th.StringType,
            description="The description of the account"
        ),
        th.Property(
            "Costcenter",
            th.StringType,
            description="The cost center linked to the account"
        ),
        th.Property(
            "CostcenterDescription",
            th.StringType,
            description="The cost center description"
        ),
        th.Property(
            "Costunit",
            th.StringType,
            description="The cost unit linked to the account"
        ),
        th.Property(
            "CostunitDescription",
            th.StringType,
            description="The cost unit description"
        ),
        th.Property(
            "Modified",
            th.DateTimeType,
            description="Last modified date"
        ),
    ).to_dict()

    def get_path(self, context: Optional[dict]) -> str:
        """Return the path of the Exact API"""

        # This stream should disregard the start_date as earliest starting timestamp
        if datetime.strptime(self.config.get("start_date"), '%Y-%m-%d').strftime('%Y-%m-%d') != self.get_starting_timestamp(context).strftime('%Y-%m-%d'):
            replication_key_value = self.get_starting_timestamp(context).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            
            filter_path = f"$filter={self.replication_key}%20ge%20datetime%27{replication_key_value}%27&"
                
        path = f"/financial/GLAccounts?{filter_path if 'filter_path' in locals() else ''}" \
            "$select=ID,Code,Description,Costcenter,CostcenterDescription,Costunit,CostunitDescription,Modified"

        return path

class BankEntryLinesStream(ExactOnlineStream):
    """Define custom stream."""

    name = "bank_entry_lines"
    primary_keys = ["ID"]
    replication_key = "Modified"
    date_fields = ['Date', 'Modified']
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property(
            "ID",
            th.StringType,
            description="The unique identifier of the line"
        ),
        th.Property(
            "AccountCode",
            th.StringType,
            description="The unique code of the corresponding CRM account"
        ),
        th.Property(
            "AccountName",
            th.StringType,
            description="The name of the account"
        ),
        th.Property(
            "GLAccount",
            th.StringType,
            description="The unique identifier of the corresponding GL account"
        ),
        th.Property(
            "GLAccountCode",
            th.StringType,
            description="The unique code of the corresponding GL account"
        ),
        th.Property(
            "Date",
            th.DateTimeType,
            description="THe date of the statement line"
        ),
        th.Property(
            "Description",
            th.StringType,
            description="The description of the entry"
        ),
        th.Property(
            "OurRef",
            th.IntegerType,
            description="The invoice number"
        ),
        th.Property(
            "LineNumber",
            th.IntegerType,
            description="The line number of the entry"
        ),
        th.Property(
            "AmountDC",
            th.StringType,
            description="The amount in the default currency of the company"
        ),
        th.Property(
            "Modified",
            th.DateTimeType,
            description="Last modified date"
        ),
    ).to_dict()

    def get_path(self, context: Optional[dict]) -> str:
        """Return the path of the Exact API"""

        replication_key_value = self.get_starting_timestamp(context).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        path = "/financialtransaction/BankEntryLines?" \
            f"$filter={self.replication_key}%20ge%20datetime%27{replication_key_value}%27&" \
            "$select=ID,AccountCode,AccountName,GLAccount,GLAccountCode,Date,Description,OurRef,LineNumber,AmountDC,Modified"

        return path

class CashEntryLinesStream(ExactOnlineStream):
    """Define custom stream."""

    name = "cash_entry_lines"
    primary_keys = ["ID"]
    replication_key = "Modified"
    date_fields = ['Date', 'Modified']
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property(
            "ID",
            th.StringType,
            description="The unique identifier of the line"
        ),
        th.Property(
            "AccountCode",
            th.StringType,
            description="The unique code of the corresponding CRM account"
        ),
        th.Property(
            "AccountName",
            th.StringType,
            description="The name of the account"
        ),
        th.Property(
            "GLAccount",
            th.StringType,
            description="The unique identifier of the corresponding GL account"
        ),
        th.Property(
            "GLAccountCode",
            th.StringType,
            description="The unique code of the corresponding GL account"
        ),
        th.Property(
            "Date",
            th.DateTimeType,
            description="THe date of the statement line"
        ),
        th.Property(
            "Description",
            th.StringType,
            description="The description of the entry"
        ),
        th.Property(
            "OurRef",
            th.IntegerType,
            description="The invoice number"
        ),
        th.Property(
            "LineNumber",
            th.IntegerType,
            description="The line number of the entry"
        ),
        th.Property(
            "AmountDC",
            th.StringType,
            description="The amount in the default currency of the company"
        ),
        th.Property(
            "Modified",
            th.DateTimeType,
            description="Last modified date"
        ),
    ).to_dict()

    def get_path(self, context: Optional[dict]) -> str:
        """Return the path of the Exact API"""

        replication_key_value = self.get_starting_timestamp(context).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        path = "/financialtransaction/CashEntryLines?" \
            f"$filter={self.replication_key}%20ge%20datetime%27{replication_key_value}%27&" \
            "$select=ID,AccountCode,AccountName,GLAccount,GLAccountCode,Date,Description,OurRef,LineNumber,AmountDC,Modified"

        return path

class GeneralJournalEntryLinesStream(ExactOnlineStream):
    """Define custom stream."""

    name = "general_journal_entry_lines"
    primary_keys = ["ID"]
    replication_key = "Modified"
    date_fields = ['Date', 'Modified']
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property(
            "ID",
            th.StringType,
            description="The unique identifier of the line"
        ),
        th.Property(
            "AccountCode",
            th.StringType,
            description="The unique code of the corresponding CRM account"
        ),
        th.Property(
            "AccountName",
            th.StringType,
            description="The name of the account"
        ),
        th.Property(
            "GLAccount",
            th.StringType,
            description="The unique identifier of the corresponding GL account"
        ),
        th.Property(
            "GLAccountCode",
            th.StringType,
            description="The unique code of the corresponding GL account"
        ),
        th.Property(
            "Date",
            th.DateTimeType,
            description="THe date of the statement line"
        ),
        th.Property(
            "Description",
            th.StringType,
            description="The description of the entry"
        ),
        th.Property(
            "OurRef",
            th.IntegerType,
            description="The invoice number"
        ),
        th.Property(
            "LineNumber",
            th.IntegerType,
            description="The line number of the entry"
        ),
        th.Property(
            "AmountDC",
            th.StringType,
            description="The amount in the default currency of the company"
        ),
        th.Property(
            "AmountVATDC",
            th.StringType,
            description="The amount of VAT in the default currency of the company"
        ),
        th.Property(
            "Modified",
            th.DateTimeType,
            description="Last modified date"
        ),
    ).to_dict()

    def get_path(self, context: Optional[dict]) -> str:
        """Return the path of the Exact API"""

        replication_key_value = self.get_starting_timestamp(context).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        path = "/generaljournalentry/GeneralJournalEntryLines?" \
            f"$filter={self.replication_key}%20ge%20datetime%27{replication_key_value}%27&" \
            "$select=ID,AccountCode,AccountName,GLAccount,GLAccountCode,Date,Description,OurRef,LineNumber,AmountDC,AmountVATDC,Modified"

        return path

class PurchaseEntriesStream(ExactOnlineStream):
    """Define custom stream."""

    name = "purchase_entries"
    primary_keys = ["EntryID"]
    replication_key = "Modified"
    date_fields = ['Created', 'EntryDate', 'DueDate', 'Modified']
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property(
            "EntryID",
            th.StringType,
            description="The unique identifier of the line"
        ),
        th.Property(
            "Created",
            th.DateTimeType,
            description="The creation date"
        ),
        th.Property(
            "EntryDate",
            th.DateTimeType,
            description="The invoice date"
        ),
        th.Property(
            "InvoiceNumber",
            th.IntegerType,
            description="The invoice number"
        ),
        th.Property(
            "EntryNumber",
            th.IntegerType,
            description="The entry number"
        ),
        th.Property(
            "Description",
            th.StringType,
            description="The description of the invoice"
        ),
        th.Property(
            "OrderNumber",
            th.IntegerType,
            description="The order number"
        ),
        th.Property(
            "DueDate",
            th.DateTimeType,
            description="The due date"
        ),
        th.Property(
            "PaymentCondition",
            th.StringType,
            description="The code of the payment conditino that is used to calculate the due date and discount"
        ),
        th.Property(
            "Status",
            th.IntegerType,
            description="The code of the payment conditino that is used to calculate the due date and discount"
        ),
        th.Property(
            "Journal",
            th.StringType,
            description="The code of the purchase journal in which the invoice is entered"
        ),
        th.Property(
            "Supplier",
            th.StringType,
            description="The code of supplier"
        ),
        th.Property(
            "SupplierName",
            th.StringType,
            description="The name of supplier"
        ),
        th.Property(
            "AmountDC",
            th.NumberType,
            description="Amount including VAT in the default currency of the company"
        ),
        th.Property(
            "VATAmountDC",
            th.NumberType,
            description="VAT Amount in the default currency of the company"
        ),
        th.Property(
            "Modified",
            th.DateTimeType,
            description="Last modified date"
        ),
    ).to_dict()

    def get_path(self, context: Optional[dict]) -> str:
        """Return the path of the Exact API"""

        replication_key_value = self.get_starting_timestamp(context).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        path = "/purchaseentry/PurchaseEntries?" \
            f"$filter={self.replication_key}%20ge%20datetime%27{replication_key_value}%27&" \
            "$select=EntryID,Created,EntryDate,InvoiceNumber,EntryNumber,Description,OrderNumber,DueDate,PaymentCondition,Status,Journal,Supplier,SupplierName,AmountDC,VATAmountDC,Modified"

        return path

class SalesEntriesStream(ExactOnlineStream):
    """Define custom stream."""

    name = "sales_entries"
    primary_keys = ["EntryID"]
    replication_key = "Modified"
    date_fields = ['Created', 'EntryDate', 'DueDate', 'Modified']
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property(
            "EntryID",
            th.StringType,
            description="The unique identifier of the line"
        ),
        th.Property(
            "Created",
            th.DateTimeType,
            description="The creation date"
        ),
        th.Property(
            "EntryDate",
            th.DateTimeType,
            description="The invoice date"
        ),
        th.Property(
            "YourRef",
            th.StringType,
            description="The invoice number"
        ),
        th.Property(
            "EntryNumber",
            th.IntegerType,
            description="The entry number"
        ),
        th.Property(
            "Description",
            th.StringType,
            description="The description of the invoice"
        ),
        th.Property(
            "OrderNumber",
            th.IntegerType,
            description="The order number"
        ),
        th.Property(
            "DueDate",
            th.DateTimeType,
            description="The due date"
        ),
        th.Property(
            "PaymentCondition",
            th.StringType,
            description="The code of the payment conditino that is used to calculate the due date and discount"
        ),
        th.Property(
            "Status",
            th.IntegerType,
            description="The code of the payment conditino that is used to calculate the due date and discount"
        ),
        th.Property(
            "Journal",
            th.StringType,
            description="The code of the purchase journal in which the invoice is entered"
        ),
        th.Property(
            "Customer",
            th.StringType,
            description="The code of customer"
        ),
        th.Property(
            "CustomerName",
            th.StringType,
            description="The name of customer"
        ),
        th.Property(
            "AmountDC",
            th.NumberType,
            description="Amount including VAT in the default currency of the company"
        ),
        th.Property(
            "VATAmountDC",
            th.NumberType,
            description="VAT Amount in the default currency of the company"
        ),
        th.Property(
            "Modified",
            th.DateTimeType,
            description="Last modified date"
        ),
    ).to_dict()

    def get_path(self, context: Optional[dict]) -> str:
        """Return the path of the Exact API"""

        replication_key_value = self.get_starting_timestamp(context).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        path = "/salesentry/SalesEntries?" \
            f"$filter={self.replication_key}%20ge%20datetime%27{replication_key_value}%27&" \
            "$select=EntryID,Created,EntryDate,YourRef,EntryNumber,Description,OrderNumber,DueDate,PaymentCondition,Status,Journal,Customer,CustomerName,AmountDC,VATAmountDC,Modified"

        return path

class CrmAccountsStream(ExactOnlineStream):
    """Define custom stream."""

    name = "crm_accounts"
    primary_keys = ["ID"]
    replication_key = "Modified"
    date_fields = ['Modified']
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property(
            "ID",
            th.StringType,
            description="The unique identifier of the account"
        ),
        th.Property(
            "AccountManager",
            th.StringType,
            description="The accountmanager ID"
        ),
        th.Property(
            "AccountManagerFullName",
            th.StringType,
            description="The name of the accountmanager"
        ),
        th.Property(
            "Code",
            th.StringType,
            description="The unique account code"
        ),
        th.Property(
            "City",
            th.StringType,
            description="The city the customer has its visit address"
        ),
        th.Property(
            "CountryName",
            th.StringType,
            description="The country the customer is in"
        ),
        th.Property(
            "Latitude",
            th.NumberType,
            description="The latitude of the customer address"
        ),
        th.Property(
            "Longitude",
            th.NumberType,
            description="The longitude of the customer address"
        ),
        th.Property(
            "Name",
            th.StringType,
            description="The customer name"
        ),
        th.Property(
            "SearchCode",
            th.StringType,
            description="The customer search code"
        ),
        th.Property(
            "Modified",
            th.DateTimeType,
            description="Last modified date"
        ),
    ).to_dict()

    def get_path(self, context: Optional[dict]) -> str:
        """Return the path of the Exact API"""

        # This stream should disregard the start_date as earliest starting timestamp
        if datetime.strptime(self.config.get("start_date"), '%Y-%m-%d').strftime('%Y-%m-%d') != self.get_starting_timestamp(context).strftime('%Y-%m-%d'):
            replication_key_value = self.get_starting_timestamp(context).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            
            filter_path = f"$filter={self.replication_key}%20ge%20datetime%27{replication_key_value}%27&"
        
        path = f"/crm/Accounts?{filter_path if 'filter_path' in locals() else ''}" \
            "$select=ID,AccountManager,AccountManagerFullName,Code,City,CountryName,Latitude,Longitude,Name,SearchCode,Modified"

        return path

class CashflowPaymentConditionsStream(ExactOnlineStream):
    """Define custom stream."""

    name = "cashflow_payment_conditions"
    primary_keys = ["ID"]
    replication_key = "Modified"
    date_fields = ['Modified']
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property(
            "ID",
            th.StringType,
            description="The unique identifier of the payment condition"
        ),
        th.Property(
            "Code",
            th.StringType,
            description="The code of the payment condition"
        ),
        th.Property(
            "Description",
            th.StringType,
            description="The description of the payment condition"
        ),
        th.Property(
            "Modified",
            th.DateTimeType,
            description="Last modified date"
        ),
    ).to_dict()

    def get_path(self, context: Optional[dict]) -> str:
        """Return the path of the Exact API"""

        # This stream should disregard the start_date as earliest starting timestamp
        if datetime.strptime(self.config.get("start_date"), '%Y-%m-%d').strftime('%Y-%m-%d') != self.get_starting_timestamp(context).strftime('%Y-%m-%d'):
            replication_key_value = self.get_starting_timestamp(context).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            
            filter_path = f"$filter={self.replication_key}%20ge%20datetime%27{replication_key_value}%27&"
        
        path = f"/cashflow/PaymentConditions?{filter_path if 'filter_path' in locals() else ''}" \
            "$select=ID,Code,Description,Modified"

        return path

class CashflowPaymentsStream(ExactOnlineStream):
    """Define custom stream."""

    name = "cashflow_payments"
    primary_keys = ["ID"]
    replication_key = "Modified"
    date_fields = ['Created', 'DiscountDueDate', 'DueDate', 'InvoiceDate', 'Modified']
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property(
            "ID",
            th.StringType,
            description="The unique identifier of the account"
        ),
        th.Property(
            "Account",
            th.StringType,
            description="The supplier to which the payment has to be done"
        ),
        th.Property(
            "AccountCode",
            th.StringType,
            description="The supplier to which the payment has to be done"
        ),
        th.Property(
            "AmountDC",
            th.NumberType,
            description="Amount in the default currency of the company"
        ),
        th.Property(
            "AmountDiscountDC",
            th.NumberType,
            description="Amount of discount in the default currency of the company"
        ),
        th.Property(
            "Created",
            th.DateTimeType,
            description="The creation date"
        ),
        th.Property(
            "Description",
            th.StringType,
            description="Extra description for the payment that is included in the bank export file"
        ),
        th.Property(
            "DiscountDueDate",
            th.DateTimeType,
            description="The date before payment must be done to be eligible for discount"
        ),
        th.Property(
            "DocumentNumber",
            th.NumberType,
            description="Number of the document"
        ),
        th.Property(
            "DocumentSubject",
            th.StringType,
            description="Subject of the document"
        ),
        th.Property(
            "DueDate",
            th.DateTimeType,
            description="The date before the payment must be done"
        ),
        th.Property(
            "InvoiceDate",
            th.DateTimeType,
            description="The invoice date of the linked transaction"
        ),
        th.Property(
            "InvoiceNumber",
            th.StringType,
            description="The invoice number of the linked transaction"
        ),
        th.Property(
            "PaymentCondition",
            th.StringType,
            description="The payment condition of the linked transaction"
        ),
        th.Property(
            "Status",
            th.NumberType,
            description="The status of the payment"
        ),
        th.Property(
            "YourRef",
            th.StringType,
            description="Invoice number of the supplier. In case the payment belongs to a bank entry line and is matched with one invoice, YourRef is filled with the YourRef of this invoice."
        ),
        th.Property(
            "Modified",
            th.DateTimeType,
            description="Last modified date"
        ),
    ).to_dict()

    def get_path(self, context: Optional[dict]) -> str:
        """Return the path of the Exact API"""

        # This stream should disregard the start_date as earliest starting timestamp
        if datetime.strptime(self.config.get("start_date"), '%Y-%m-%d').strftime('%Y-%m-%d') != self.get_starting_timestamp(context).strftime('%Y-%m-%d'):
            replication_key_value = self.get_starting_timestamp(context).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            
            filter_path = f"$filter={self.replication_key}%20ge%20datetime%27{replication_key_value}%27&"
        
        path = f"/cashflow/Payments?{filter_path if 'filter_path' in locals() else ''}" \
            "$select=ID,Account,AccountCode,AmountDC,AmountDiscountDC,Created,Description,DiscountDueDate,DocumentNumber,DocumentSubject,DueDate,InvoiceDate,InvoiceNumber,PaymentCondition,Status,YourRef,Modified"

        return path

class CashflowReceivablesStream(ExactOnlineStream):
    """Define custom stream."""

    name = "cashflow_receivables"
    primary_keys = ["ID"]
    replication_key = "Modified"
    date_fields = ['Created', 'DiscountDueDate', 'DueDate', 'InvoiceDate', 'Modified']
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property(
            "ID",
            th.StringType,
            description="The unique identifier of the account"
        ),
        th.Property(
            "Account",
            th.StringType,
            description="The supplier to which the payment has to be done"
        ),
        th.Property(
            "AccountCode",
            th.StringType,
            description="The supplier to which the payment has to be done"
        ),
        th.Property(
            "AmountDC",
            th.NumberType,
            description="Amount in the default currency of the company"
        ),
        th.Property(
            "AmountDiscountDC",
            th.NumberType,
            description="Amount of discount in the default currency of the company"
        ),
        th.Property(
            "Created",
            th.DateTimeType,
            description="The creation date"
        ),
        th.Property(
            "Description",
            th.StringType,
            description="Extra description for the payment that is included in the bank export file"
        ),
        th.Property(
            "DiscountDueDate",
            th.DateTimeType,
            description="The date before payment must be done to be eligible for discount"
        ),
        th.Property(
            "DocumentNumber",
            th.NumberType,
            description="Number of the document"
        ),
        th.Property(
            "DocumentSubject",
            th.StringType,
            description="Subject of the document"
        ),
        th.Property(
            "DueDate",
            th.DateTimeType,
            description="The date before the payment must be done"
        ),
        th.Property(
            "InvoiceDate",
            th.DateTimeType,
            description="The invoice date of the linked transaction"
        ),
        th.Property(
            "InvoiceNumber",
            th.StringType,
            description="The invoice number of the linked transaction"
        ),
        th.Property(
            "PaymentCondition",
            th.StringType,
            description="The payment condition of the linked transaction"
        ),
        th.Property(
            "Status",
            th.NumberType,
            description="The status of the payment"
        ),
        th.Property(
            "YourRef",
            th.StringType,
            description="Invoice number of the supplier. In case the payment belongs to a bank entry line and is matched with one invoice, YourRef is filled with the YourRef of this invoice."
        ),
        th.Property(
            "Modified",
            th.DateTimeType,
            description="Last modified date"
        ),
    ).to_dict()

    def get_path(self, context: Optional[dict]) -> str:
        """Return the path of the Exact API"""

        # This stream should disregard the start_date as earliest starting timestamp
        if datetime.strptime(self.config.get("start_date"), '%Y-%m-%d').strftime('%Y-%m-%d') != self.get_starting_timestamp(context).strftime('%Y-%m-%d'):
            replication_key_value = self.get_starting_timestamp(context).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            
            filter_path = f"$filter={self.replication_key}%20ge%20datetime%27{replication_key_value}%27&"
        
        path = f"/cashflow/Receivables?{filter_path if 'filter_path' in locals() else ''}" \
            "$select=ID,Account,AccountCode,AmountDC,AmountDiscountDC,Created,Description,DiscountDueDate,DocumentNumber,DocumentSubject,DueDate,InvoiceDate,InvoiceNumber,PaymentCondition,Status,YourRef,Modified"

        return path

class TransactionLinesStream(ExactOnlineStream):
    """Define custom stream."""

    name = "transaction_lines"
    primary_keys = ["ID"]
    replication_key = "Modified"
    date_fields = ['Date', 'Modified']
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property(
            "ID",
            th.StringType,
            description="The unique identifier of the line"
        ),
        th.Property(
            "AccountCode",
            th.StringType,
            description="The unique code of the corresponding CRM account"
        ),
        th.Property(
            "AccountName",
            th.StringType,
            description="The name of the account"
        ),
        th.Property(
            "GLAccount",
            th.StringType,
            description="The unique identifier of the corresponding GL account"
        ),
        th.Property(
            "GLAccountCode",
            th.StringType,
            description="The unique code of the corresponding GL account"
        ),
        th.Property(
            "Date",
            th.DateTimeType,
            description="THe date of the statement line"
        ),
        th.Property(
            "Description",
            th.StringType,
            description="The description of the entry"
        ),
        th.Property(
            "LineNumber",
            th.IntegerType,
            description="The line number of the entry"
        ),
        th.Property(
            "AmountDC",
            th.StringType,
            description="The amount in the default currency of the company"
        ),
        th.Property(
            "AmountVATBaseFc",
            th.StringType,
            description="The amount of VAT in the default currency of the company"
        ),
        th.Property(
            "Modified",
            th.DateTimeType,
            description="Last modified date"
        ),
    ).to_dict()

    def get_path(self, context: Optional[dict]) -> str:
        """Return the path of the Exact API"""

        replication_key_value = self.get_starting_timestamp(context).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        path = "/financialtransaction/TransactionLines?" \
            f"$filter={self.replication_key}%20ge%20datetime%27{replication_key_value}%27&" \
            "$select=ID,AccountCode,AccountName,GLAccount,GLAccountCode,Date,Description,LineNumber,AmountDC,AmountVATBaseFC,Modified"

        return path

class QuotationsStream(ExactOnlineStream):
    """Define custom stream."""

    name = "quotations"
    primary_keys = ["QuotationID"]
    replication_key = "Modified"
    date_fields = ['QuotationDate', 'Modified', 'DueDate']
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property(
            "QuotationID",
            th.StringType,
            description="The unique identifier of the quotation"
        ),
        th.Property(
            "QuotationDate",
            th.DateTimeType,
            description="The quotation date"
        ),
        th.Property(
            "QuotationNumber",
            th.IntegerType,
            description="The quotation number"
        ),
        th.Property(
            "OrderAccount",
            th.StringType,
            description="The customer whom the quotation is made for"
        ),
        th.Property(
            "OrderAccountName",
            th.StringType,
            description="The name of the customer whom the quotation is made for"
        ),
        th.Property(
            "DueDate",
            th.DateTimeType,
            description="The due date"
        ),
        th.Property(
            "Creator",
            th.StringType,
            description="The creator of the sales invoice"
        ),
        th.Property(
            "CreatorFullName",
            th.StringType,
            description="The name of the creator"
        ),
        th.Property(
            "Salesperson",
            th.StringType,
            description="The sales person of the sales invoice"
        ),
        th.Property(
            "SalespersonFullName",
            th.StringType,
            description="The name of the salesperson"
        ),
        th.Property(
            "AmountDC",
            th.NumberType,
            description="Amount in the default currency of the company"
        ),
        th.Property(
            "AmountDiscount",
            th.NumberType,
            description="Amount of discount given"
        ),
        th.Property(
            "VATAmountFC",
            th.NumberType,
            description="Amount of VAT in the currency of the transaction"
        ),
        th.Property(
            "Status",
            th.IntegerType,
            description="Statusnumber of the quotation"
        ),
        th.Property(
            "StatusDescription",
            th.StringType,
            description="Statusdescription of the quotation"
        ),
        th.Property(
            "Modified",
            th.DateTimeType,
            description="Last modified date"
        )
    ).to_dict()

    def get_path(self, context: Optional[dict]) -> str:
        """Return the path of the Exact API"""

        replication_key_value = self.get_starting_timestamp(context).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        path = "/crm/Quotations?" \
            f"$filter={self.replication_key}%20ge%20datetime%27{replication_key_value}%27&" \
            "$select=QuotationID,QuotationDate,QuotationNumber,OrderAccount,OrderAccountName,DueDate,Creator,CreatorFullName,Salesperson,SalespersonFullName,AmountDC,AmountDiscount,VATAmountFC,Status,StatusDescription,Modified"

        return path

class SalesOrdersStream(ExactOnlineStream):
    """Define custom stream."""

    name = "sales_orders"
    primary_keys = ["OrderID"]
    replication_key = "Modified"
    date_fields = ['OrderDate', 'Modified']
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property(
            "OrderID",
            th.StringType,
            description="The unique identifier of the order"
        ),
        th.Property(
            "OrderDate",
            th.DateTimeType,
            description="The order date"
        ),
        th.Property(
            "OrderNumber",
            th.IntegerType,
            description="The order number"
        ),
        th.Property(
            "OrderedBy",
            th.StringType,
            description="The customer whom the order is made for"
        ),
        th.Property(
            "OrderedByName",
            th.StringType,
            description="The name of the customer whom the order is made for"
        ),
        th.Property(
            "Creator",
            th.StringType,
            description="The creator of the sales invoice"
        ),
        th.Property(
            "CreatorFullName",
            th.StringType,
            description="The name of the creator"
        ),
        th.Property(
            "Salesperson",
            th.StringType,
            description="The sales person of the sales invoice"
        ),
        th.Property(
            "SalespersonFullName",
            th.StringType,
            description="The name of the salesperson"
        ),
        th.Property(
            "AmountFCExclVat",
            th.NumberType,
            description="Amount excl. VAT in the currency of the transaction"
        ),
        th.Property(
            "AmountDiscountExclVat",
            th.NumberType,
            description="Amount of discount given excl. VAT"
        ),
        th.Property(
            "Status",
            th.IntegerType,
            description="Statusnumber of the order"
        ),
        th.Property(
            "StatusDescription",
            th.StringType,
            description="Statusdescription of the order"
        ),
        th.Property(
            "Modified",
            th.DateTimeType,
            description="Last modified date"
        )
    ).to_dict()

    def get_path(self, context: Optional[dict]) -> str:
        """Return the path of the Exact API"""

        replication_key_value = self.get_starting_timestamp(context).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        path = "/salesorder/SalesOrders?" \
            f"$filter={self.replication_key}%20ge%20datetime%27{replication_key_value}%27&" \
            "$select=OrderID,OrderDate,OrderNumber,OrderedBy,OrderedByName,Creator,CreatorFullName,Salesperson,SalespersonFullName,AmountFCExclVat,AmountDiscountExclVat,Status,StatusDescription,Modified"

        return path

# class SystemUsersStream(ExactOnlineStream):
#     """Define custom stream."""

#     name = "system_users"
#     primary_keys = ["UserID"]
#     replication_key = "Modified"
#     date_fields = ['StartDate', 'EndDate', 'Modified']
#     # Optionally, you may also use `schema_filepath` in place of `schema`:
#     # schema_filepath = SCHEMAS_DIR / "users.json"
#     schema = th.PropertiesList(
#         th.Property(
#             "UserID",
#             th.StringType,
#             description="The unique identifier of the user"
#         ),
#         th.Property(
#             "FullName",
#             th.StringType,
#             description="The name of the user"
#         ),
#         th.Property(
#             "Email",
#             th.StringType,
#             description="The e-mailaddress of the user"
#         ),
#         th.Property(
#             "StartDate",
#             th.DateTimeType,
#             description="The start date the user was allowed to log in"
#         ),
#         th.Property(
#             "EndDate",
#             th.DateTimeType,
#             description="The date after which the user login is disabled"
#         ),
#         th.Property(
#             "Modified",
#             th.DateTimeType,
#             description="Last modified date"
#         ),
#     ).to_dict()

#     def get_path(self, context: Optional[dict]) -> str:
#         """Return the path of the Exact API"""

#         # This stream should disregard the start_date as earliest starting timestamp
#         if datetime.strptime(self.config.get("start_date"), '%Y-%m-%d').strftime('%Y-%m-%d') != self.get_starting_timestamp(context).strftime('%Y-%m-%d'):
#             replication_key_value = self.get_starting_timestamp(context).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            
#             filter_path = f"$filter={self.replication_key}%20ge%20datetime%27{replication_key_value}%27&"
        
#         path = f"/system/Users?{filter_path if 'filter_path' in locals() else ''}" \
#             "$select=UserID,FullName,Email,StartDate,EndDate,Modified"

#         return path