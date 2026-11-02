from pydantic import BaseModel
from typing import Dict, List

import json


class Parameters(BaseModel):
    apartments_json_path: str = 'data/apartments.json'
    tenants_json_path: str = 'data/tenants.json'
    transfers_json_path: str = 'data/transfers.json'
    bills_json_path: str = 'data/bills.json'


class Room(BaseModel):
    name: str
    area_m2: float


class Apartment(BaseModel):
    key: str
    name: str
    location: str
    area_m2: float
    rooms: Dict[str, Room]

    @staticmethod
    def from_json_file(file_path: str) -> Dict[str,'Apartment']:
        data = None
        with open(file_path, 'r') as file:
            data = json.load(file)
        assert isinstance(data, dict), "Expected a dictionary of apartments"
        return {key: Apartment(**apartment) for key, apartment in data.items()}

    
class Tenant(BaseModel):
    name: str
    apartment: str
    room: str
    rent_pln: float
    deposit_pln: float
    date_agreement_from: str
    date_agreement_to: str

    @staticmethod
    def from_json_file(file_path: str) -> Dict[str,'Tenant']:
        data = None
        with open(file_path, 'r') as file:
            data = json.load(file)
        assert isinstance(data, dict), "Expected a dictionary of tenants"
        return {key: Tenant(**tenant) for key, tenant in data.items()}
    

class Transfer(BaseModel):
    amount_pln: float
    date: str
    settlement_year: int | None
    settlement_month: int | None
    tenant: str

    @staticmethod
    def from_json_file(file_path: str) -> List['Transfer']:
        data = None
        with open(file_path, 'r') as file:
            data = json.load(file)
        assert isinstance(data, list), "Expected a list of transfers"
        return [Transfer(**transfer) for transfer in data]


class Bill(BaseModel):
    amount_pln: float
    date_due: str
    apartment: str
    settlement_year: int
    settlement_month: int
    type: str

    @staticmethod
    def from_json_file(file_path: str) -> List['Bill']:
        data = None
        with open(file_path, 'r') as file:
            data = json.load(file)
        assert isinstance(data, list), "Expected a list of bills"
        return [Bill(**bill) for bill in data]


class TenantSettlement(BaseModel):
    tenant: str
    settlement_year: int
    settlement_month: int
    apartment: str
    rent_pln: float
    bills_pln: float
    transfers_pln: float

    @property
    def balance_pln(self) -> float:
        return self.transfers_pln - self.rent_pln - self.bills_pln
class ApartmentSettlement(BaseModel):
    apart: str
    year: int
    month: int
    total_bills_pln: float
    total_rent_pln: float
    total_due_pln: float


class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)


if __name__ == '__main__':
    parameters = Parameters()
    manager = Manager(parameters)

    print('=== MIESZKANIA ===')
    for apartment in manager.apartments.values():
        print(f'\n{apartment.name} ({apartment.key})')
        print(f'  Adres: {apartment.location}')
        print(f'  Powierzchnia: {apartment.area_m2:.2f} m2')

        print('  Pokoje:')
        for room in apartment.rooms.values():
            print(f'    - {room.name}: {room.area_m2:.2f} m2')

        print('  Rachunki:')
        for bill in manager.bills:
            if bill.apartment == apartment.key:
                print(f'    - {bill.type}: {bill.amount_pln:.2f} PLN, okres: {bill.settlement_month}/{bill.settlement_year}, termin: {bill.date_due}')

    print('\n=== NAJEMCY ===')
    for tenant in manager.tenants.values():
        print(f'\n{tenant.name}')
        print(f'  Mieszkanie: {tenant.apartment}, pokój: {tenant.room}')
        print(f'  Czynsz: {tenant.rent_pln:.2f} PLN, kaucja: {tenant.deposit_pln:.2f} PLN')
        print(f'  Umowa: {tenant.date_agreement_from} - {tenant.date_agreement_to}')

        print('  Przelewy:')
        for transfer in manager.transfers:
            if transfer.tenant == tenant.name:
                print(f'    - {transfer.amount_pln:.2f} PLN, data: {transfer.date}, okres: {transfer.settlement_month}/{transfer.settlement_year}')
