import requests
from  pyzettle.authenticate import Authenticate
from dotenv import load_dotenv
import os
import pandas as pd
from pyzettle.payments import drop_columns
from datetime import datetime

API_URL = "https://purchase.izettle.com/purchases/v2"
CASH_CARD_MAPPING = {
    'IZETTLE_CARD': 'card',
    'IZETTLE_CASH': 'cash',
    'GIFTCARD' : 'giftcard',
}


class GetPayments(Authenticate):
    def __init__(self, client_id: str, api_key:str):
        self.api_url = API_URL
        self.data = pd.DataFrame()
        
        super().__init__(client_id, api_key)
        
    def fetch_purchases(self,start:datetime=None, end:datetime=None):
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        params = {"descending": "true"}

        if not start is None:
            params['startDate'] = start.strftime("%Y-%m-%dT%H:%M:%S%z")
        if not end is None:
            params['endDate'] = end.strftime("%Y-%m-%dT%H:%M:%S%z")

        while True:
            response = requests.get(self.api_url, headers=headers, params=params)
            response.raise_for_status()  # Ensure we notice bad responses
            response_json = response.json()
            
            # Append the purchases data to the DataFrame
            purchases = pd.DataFrame(response_json.get('purchases', []))
            self.data = pd.concat([self.data, purchases], ignore_index=True)

            # Check if there are more pages
            last_purchase_hash = response_json.get('lastPurchaseHash')
            if not last_purchase_hash:
                break  # Exit loop if no more pages

            # Update params with the lastPurchaseHash for the next request
            params['lastPurchaseHash'] = last_purchase_hash
        
        self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
        return self


    def _drop_columns(self, list_name:str):
        
        if list_name.lower() == "initial":
            list_name_ref = drop_columns.INITIAL
        elif list_name.lower() == "final":
            list_name_ref = drop_columns.FINAL
        else:
            raise ValueError(f"\"list_name\" must be \"initial\" or \"final\". Got {list_name}.")
        
        self.data = self.data.drop(columns=list_name_ref, errors='ignore')
        return self

    def _format_payment_col(self):
        
        if 'payments' in self.data.columns:
            payments = self.data.explode('payments')
            payments = pd.json_normalize(payments['payments'])
            payments = payments.drop(columns=drop_columns.PAYMENTS, errors='ignore')
            
            self.data = self.data.drop(columns=['payments'], errors='ignore').reset_index(drop=True).join(payments.reset_index(drop=True))        
            self.data['type'] = self.data['type'].replace(CASH_CARD_MAPPING)
            
            return self
        
        else:
            raise ValueError("\"Payments\" column is not in the DataFrame so cannot be completed")
    
    def _format_products_col(self):
        
        if 'products' in self.data.columns:
            products = self.data.explode('products')
            
            products_norm = pd.json_normalize(products['products'])
            products_norm = products_norm.drop(columns=drop_columns.PRODUCTS, errors='ignore')
            
            products = products.drop(columns=['products'], errors='ignore').reset_index(drop=True)
            self.data = products.join(products_norm.reset_index(drop=True))
            return self
        
        else:
            raise ValueError("\"products\" column is not in the DataFrame so cannot be completed")
    
    def format_payments(self):
        
        column_name_mapping = {
        "purchaseNumber" : "purchase_number",
        "customAmountSale" : "custom_amount_sale",
        "type" : "payment_type",
        "unitPrice" : "unit_price",
        "name" : "product",
            "userDisplayName": "user_display_name"
        }
        
        instance = self._drop_columns("initial")
        instance = instance._format_payment_col()
        instance = instance._format_products_col()
        instance = instance._drop_columns("final")
        data = instance.data
        data['name'] = data['name'].replace('', "unknown")
        
        self.data = data.rename(columns=column_name_mapping)
        
        return self
