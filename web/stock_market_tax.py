#!/usr/bin/env python
# coding: utf-8

from datetime import datetime
from exchange_rates import conversion_dict

def load_user_transactions_from_file(filename="Transactions.csv"):
    transactions = open("Transactions.csv", "r").readlines()

    return load_user_transactions(transactions)

def load_user_transactions(transactions):
    columns = list(transactions[0].strip().split(","))

    # Custom columns fixup, not necessary, may be subject to change as per degiros returned format
    columns[6] = "Waluta lokalna"
    columns[8] = "Waluta wartości lokalnej"

    columns[10] = "Waluta rachunku"
    columns[13] = "Waluta wymieniana"
    columns[15] = "Waluta opłaty"
    return columns, transactions


class Stock:
    def __init__(self, name, ISIN, datet, price, currency, transaction_id, fee, currency_fee):
        self.name = name
        self.ISIN = ISIN
        self.datet = datet
        self.price = price
        self.currency = currency
        self.transaction_id = transaction_id
        self.fee = fee
        self.currency_fee = currency_fee

    def __repr__(self):
        return str(self)

    def __str__(self):
        return " " + self.name + " " + str(self.price) + self.currency + " "

class StockManager:
    def __init__(self, tax=0.19):
        self.vault = {}
        self.taxable_income_reduction = 0
        self.total_income = 0
        self.loss = 0
        self.tax = tax

    def buy(self, ISIN, name, datet, amount, price, currency, transaction_id, fee, currency_fee):
        if ISIN not in self.vault:
            self.vault[ISIN] = []

        for i in range(amount):
            self.vault[ISIN].append(Stock(name, ISIN, datet, price, currency, transaction_id, fee/amount, currency_fee))

        self.vault[ISIN] = sorted(self.vault[ISIN], key=lambda x: (x.datet))

    def sell(self, ISIN, name, datet, amount, price, currency, transaction_id, fee, currency_fee):
        gross = 0

        for i in range(abs(amount)):
            s = self.pop(ISIN)

            exchange_rate_date_of_buy = 1.0
            exchange_rate_date_of_sell = 1.0
            if currency != "PLN":
                # TODO: Should be getting D-1
                exchange_rate_date_of_buy = conversion_dict[currency][s.datet.strftime("%Y%m%d")]
                exchange_rate_date_of_sell = conversion_dict[currency][datet.strftime("%Y%m%d")]

            difference_in_price = abs(price*exchange_rate_date_of_sell - s.price*exchange_rate_date_of_buy)
            # calculate tax
            if s.price < price:
                self.deduct_fee_from_tax(s.fee, s.datet, s.currency_fee)
                self.deduct_fee_from_tax(fee/amount, datet, currency_fee)

                gross += difference_in_price

            elif s.price >= price:
                self.loss += difference_in_price

        self.total_income += gross

    @property
    def total_tax(self):
        return self.taxable_income * self.tax

    @property
    def taxable_income(self):
        return (self.total_income-self.loss) - self.taxable_income_reduction

    def deduct_fee_from_tax(self, fee, datet, currency):
        exchange_rate_date_of_transaction = conversion_dict[currency][datet.strftime("%Y%m%d")]
        
        self.taxable_income_reduction += abs(fee) * exchange_rate_date_of_transaction

    def pop(self, ISIN):
        return self.vault[ISIN].pop(0)

    def __repr__(self):
        return(str(self))

    def __str__(self):
        out = ""
        for k, v in self.vault.items():
            out += str(k) + " " + str(v) + "\n"
        return out


def calculate_tax(transactions):
    sv = StockManager()

    for line in transactions[1:][::-1]:
        splitted = line.strip().split(",")
        date, time, product, ISIN, market, amount, \
            currency_local, price, currency_local_2, \
            local_price, value, currency_wallet, exchange_rate, \
            currency_exchange, fee, currency_fee, total, identifier = splitted

        # data type classification
        datet = datetime.strptime(date + " " + time, "%d-%m-%Y %H:%M")
        amount = int(amount)
        price = float(price)
        fee = float(fee)

        if amount > 0:
            sv.buy(ISIN, product, datet, amount, price, currency_local, identifier, fee, currency_fee)
        if amount < 0:
            sv.sell(ISIN, product, datet, amount, price, currency_local, identifier, fee, currency_fee)

    return sv

def main():
    columns, transactions = load_user_transactions_from_file()
    sv = calculate_tax(transactions)

    print(f"Total income: {sv.total_income}")
    print(f"Total loss: {sv.loss}")
    print(f"Total tax reductions: {sv.taxable_income_reduction}")
    print(f"Taxable income (income-loss-deductions): {sv.taxable_income}")
    print(f"Tax to pay (19%): {sv.total_tax}")

if __name__ == '__main__':
    main()



