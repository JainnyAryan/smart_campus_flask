from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Driver:
    license_number: str

    def to_dict(self):
        return {"license_number": self.license_number}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            license_number=data["license_number"]
        )


@dataclass
class Student:
    registration_number: str
    wallet_id: Optional[str] = None

    def to_dict(self):
        return {"registration_number": self.registration_number, "wallet_id": self.wallet_id}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            registration_number=data["registration_number"],
            wallet_id=data.get("wallet_id")
        )


@dataclass
class User:
    id: str
    name: str
    email: str
    mobile: str
    type: str
    student: Optional[Student] = None
    driver: Optional[Driver] = None

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "mobile": self.mobile,
            "type": self.type,
            "student": self.student.to_dict() if self.student else None,
            "driver": self.driver.to_dict() if self.driver else None
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data["id"],
            name=data["name"],
            email=data["email"],
            mobile=data["mobile"],
            type=data["type"],
            student=Student.from_dict(data["student"]) if data.get("student") else None,
            driver=Driver.from_dict(data["driver"]) if data.get("driver") else None
        )


@dataclass
class Wallet:
    id: str
    amount: float
    lastUsed: datetime = None

    def to_dict(self):  
        return {
            "id": self.id,
            "amount": self.amount,
            "lastUsed": self.lastUsed.isoformat() if self.lastUsed else None,
        }

    @staticmethod
    def from_dict(data: dict):
        return Wallet(
            id=data["id"],
            amount=data["amount"],
            lastUsed=datetime.fromisoformat(data["lastUsed"]) if data.get("lastUsed") else None,
        )


@dataclass
class Shuttle:
    vehicle_number: str
    region_type: str
    lat: float
    lng: float
    driver: Optional[User] = None
    id: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.id,
            "vehicle_number": self.vehicle_number,
            "region_type": self.region_type,
            "lat": self.lat,
            "lng": self.lng,
            "driver": self.driver.to_dict() if self.driver is not None else None,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get("id"),
            vehicle_number=data["vehicle_number"],
            region_type=data["region_type"],
            lat=data["lat"],
            lng=data["lng"],
            driver=User.from_dict(data["driver"]) if data.get("driver") else None,
        )


@dataclass
class WalletHistoryItem:
    wallet_id: str
    addition: bool
    amount: float
    time: datetime
    id: Optional[str] = None
    shuttle: Optional[Shuttle] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "wallet_id": self.wallet_id,
            "addition": self.addition,
            "amount": self.amount,
            "time": self.time.isoformat(),
            "shuttle": self.shuttle.to_dict() if self.shuttle is not None else None,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get("id"),
            wallet_id=data["wallet_id"],
            addition=data["addition"],
            amount=data["amount"],
            time=datetime.fromisoformat(data["time"]),
            shuttle=Shuttle.from_dict(data["shuttle"]) if data.get("shuttle") else None
        )
