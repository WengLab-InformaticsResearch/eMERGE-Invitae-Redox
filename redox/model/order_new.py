# generated by datamodel-codegen:
#   filename:  order-new.json
#   timestamp: 2022-07-01T22:34:37+00:00

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class Source(BaseModel):
    ID: Optional[Optional[str]] = None
    Name: Optional[Optional[str]] = None


class Destination(BaseModel):
    ID: Optional[Optional[str]] = None
    Name: Optional[Optional[str]] = None


class Log(BaseModel):
    ID: Optional[Optional[str]] = None
    AttemptID: Optional[Optional[str]] = None


class Message(BaseModel):
    ID: Optional[Optional[float]] = None


class Transmission(BaseModel):
    ID: Optional[Optional[float]] = None


class Meta(BaseModel):
    DataModel: str
    EventType: str
    EventDateTime: Optional[Optional[str]] = None
    Test: Optional[Optional[bool]] = None
    Source: Optional[Source] = None
    Destinations: Optional[List[Destination]] = None
    Logs: Optional[List[Log]] = None
    Message: Optional[Message] = None
    Transmission: Optional[Transmission] = None
    FacilityCode: Optional[Optional[str]] = None


class Identifier(BaseModel):
    ID: str
    IDType: str


class PhoneNumber(BaseModel):
    Home: Optional[Optional[str]] = None
    Office: Optional[Optional[str]] = None
    Mobile: Optional[Optional[str]] = None


class Address(BaseModel):
    StreetAddress: Optional[Optional[str]] = None
    City: Optional[Optional[str]] = None
    State: Optional[Optional[str]] = None
    ZIP: Optional[Optional[str]] = None
    County: Optional[Optional[str]] = None
    Country: Optional[Optional[str]] = None


class Demographics(BaseModel):
    FirstName: Optional[Optional[str]] = None
    MiddleName: Optional[Optional[str]] = None
    LastName: Optional[Optional[str]] = None
    DOB: Optional[Optional[str]] = None
    SSN: Optional[Optional[str]] = None
    Sex: Optional[Optional[str]] = None
    Race: Optional[Optional[str]] = None
    IsHispanic: Optional[Optional[bool]] = None
    Religion: Optional[Optional[str]] = None
    MaritalStatus: Optional[Optional[str]] = None
    IsDeceased: Optional[Optional[bool]] = None
    DeathDateTime: Optional[Optional[str]] = None
    PhoneNumber: Optional[PhoneNumber] = None
    EmailAddresses: Optional[List] = None
    Language: Optional[Optional[str]] = None
    Citizenship: Optional[List] = None
    Address: Optional[Address] = None


class Patient(BaseModel):
    Identifiers: List[Identifier]
    Demographics: Optional[Demographics] = None
    Notes: Optional[List] = None


class Address1(BaseModel):
    StreetAddress: Optional[Optional[str]] = None
    City: Optional[Optional[str]] = None
    State: Optional[Optional[str]] = None
    ZIP: Optional[Optional[str]] = None
    County: Optional[Optional[str]] = None
    Country: Optional[Optional[str]] = None


class PhoneNumber1(BaseModel):
    Office: Optional[Optional[str]] = None


class Location(BaseModel):
    Type: Optional[Optional[str]] = None
    Facility: Optional[Optional[str]] = None
    Department: Optional[Optional[str]] = None
    Room: Optional[Optional[str]] = None


class AttendingProvider(BaseModel):
    ID: Optional[Optional[str]] = None
    IDType: Optional[Optional[str]] = None
    FirstName: Optional[Optional[str]] = None
    LastName: Optional[Optional[str]] = None
    Credentials: Optional[List] = None
    Address: Optional[Address1] = None
    EmailAddresses: Optional[List] = None
    PhoneNumber: Optional[PhoneNumber1] = None
    Location: Optional[Location] = None


class Address2(BaseModel):
    StreetAddress: Optional[Optional[str]] = None
    City: Optional[Optional[str]] = None
    State: Optional[Optional[str]] = None
    ZIP: Optional[Optional[str]] = None
    County: Optional[Optional[str]] = None
    Country: Optional[Optional[str]] = None


class PhoneNumber2(BaseModel):
    Office: Optional[Optional[str]] = None


class Location1(BaseModel):
    Type: Optional[Optional[str]] = None
    Facility: Optional[Optional[str]] = None
    Department: Optional[Optional[str]] = None
    Room: Optional[Optional[str]] = None


class ConsultingProvider(BaseModel):
    ID: Optional[Optional[str]] = None
    IDType: Optional[Optional[str]] = None
    FirstName: Optional[Optional[str]] = None
    LastName: Optional[Optional[str]] = None
    Credentials: Optional[List] = None
    Address: Optional[Address2] = None
    EmailAddresses: Optional[List] = None
    PhoneNumber: Optional[PhoneNumber2] = None
    Location: Optional[Location1] = None


class Address3(BaseModel):
    StreetAddress: Optional[Optional[str]] = None
    City: Optional[Optional[str]] = None
    State: Optional[Optional[str]] = None
    ZIP: Optional[Optional[str]] = None
    County: Optional[Optional[str]] = None
    Country: Optional[Optional[str]] = None


class PhoneNumber3(BaseModel):
    Office: Optional[Optional[str]] = None


class Location2(BaseModel):
    Type: Optional[Optional[str]] = None
    Facility: Optional[Optional[str]] = None
    Department: Optional[Optional[str]] = None
    Room: Optional[Optional[str]] = None


class ReferringProvider(BaseModel):
    ID: Optional[Optional[str]] = None
    IDType: Optional[Optional[str]] = None
    FirstName: Optional[Optional[str]] = None
    LastName: Optional[Optional[str]] = None
    Credentials: Optional[List] = None
    Address: Optional[Address3] = None
    EmailAddresses: Optional[List] = None
    PhoneNumber: Optional[PhoneNumber3] = None
    Location: Optional[Location2] = None


class Spouse(BaseModel):
    FirstName: Optional[Optional[str]] = None
    LastName: Optional[Optional[str]] = None


class Address4(BaseModel):
    StreetAddress: Optional[Optional[str]] = None
    City: Optional[Optional[str]] = None
    State: Optional[Optional[str]] = None
    ZIP: Optional[Optional[str]] = None
    County: Optional[Optional[str]] = None
    Country: Optional[Optional[str]] = None


class PhoneNumber4(BaseModel):
    Home: Optional[Optional[str]] = None
    Business: Optional[Optional[str]] = None
    Mobile: Optional[Optional[str]] = None


class Address5(BaseModel):
    StreetAddress: Optional[Optional[str]] = None
    City: Optional[Optional[str]] = None
    State: Optional[Optional[str]] = None
    ZIP: Optional[Optional[str]] = None
    County: Optional[Optional[str]] = None
    Country: Optional[Optional[str]] = None


class Employer(BaseModel):
    Name: Optional[Optional[str]] = None
    Address: Optional[Address5] = None
    PhoneNumber: Optional[Optional[str]] = None


class Guarantor(BaseModel):
    Number: Optional[Optional[str]] = None
    FirstName: Optional[Optional[str]] = None
    MiddleName: Optional[Optional[str]] = None
    LastName: Optional[Optional[str]] = None
    SSN: Optional[Optional[str]] = None
    DOB: Optional[Optional[str]] = None
    Sex: Optional[Optional[str]] = None
    Spouse: Optional[Spouse] = None
    Address: Optional[Address4] = None
    PhoneNumber: Optional[PhoneNumber4] = None
    EmailAddresses: Optional[List] = None
    Type: Optional[Optional[str]] = None
    RelationToPatient: Optional[Optional[str]] = None
    Employer: Optional[Employer] = None


class Plan(BaseModel):
    ID: Optional[Optional[str]] = None
    IDType: Optional[Optional[str]] = None
    Name: Optional[Optional[str]] = None
    Type: Optional[Optional[str]] = None


class Address6(BaseModel):
    StreetAddress: Optional[Optional[str]] = None
    City: Optional[Optional[str]] = None
    State: Optional[Optional[str]] = None
    ZIP: Optional[Optional[str]] = None
    County: Optional[Optional[str]] = None
    Country: Optional[Optional[str]] = None


class Company(BaseModel):
    ID: Optional[Optional[str]] = None
    IDType: Optional[Optional[str]] = None
    Name: Optional[Optional[str]] = None
    Address: Optional[Address6] = None
    PhoneNumber: Optional[Optional[str]] = None


class Identifier1(BaseModel):
    ID: Optional[Optional[str]] = None
    IDType: Optional[Optional[str]] = None


class Address7(BaseModel):
    StreetAddress: Optional[Optional[str]] = None
    City: Optional[Optional[str]] = None
    State: Optional[Optional[str]] = None
    ZIP: Optional[Optional[str]] = None
    County: Optional[Optional[str]] = None
    Country: Optional[Optional[str]] = None


class Insured(BaseModel):
    Identifiers: Optional[List[Identifier1]] = None
    LastName: Optional[Optional[str]] = None
    MiddleName: Optional[Optional[str]] = None
    FirstName: Optional[Optional[str]] = None
    SSN: Optional[Optional[str]] = None
    Relationship: Optional[Optional[str]] = None
    DOB: Optional[Optional[str]] = None
    Sex: Optional[Optional[str]] = None
    Address: Optional[Address7] = None


class Insurance(BaseModel):
    Plan: Optional[Plan] = None
    MemberNumber: Optional[Optional[str]] = None
    Company: Optional[Company] = None
    GroupNumber: Optional[Optional[str]] = None
    GroupName: Optional[Optional[str]] = None
    EffectiveDate: Optional[Optional[str]] = None
    ExpirationDate: Optional[Optional[str]] = None
    PolicyNumber: Optional[Optional[str]] = None
    Priority: Optional[Optional[str]] = None
    AgreementType: Optional[Optional[str]] = None
    CoverageType: Optional[Optional[str]] = None
    Insured: Optional[Insured] = None


class Location3(BaseModel):
    Type: Optional[Optional[str]] = None
    Facility: Optional[Optional[str]] = None
    Department: Optional[Optional[str]] = None
    Room: Optional[Optional[str]] = None
    Bed: Optional[Optional[str]] = None


class Visit(BaseModel):
    VisitNumber: Optional[Optional[str]] = None
    AccountNumber: Optional[Optional[str]] = None
    PatientClass: Optional[Optional[str]] = None
    VisitDateTime: Optional[Optional[str]] = None
    AttendingProvider: Optional[AttendingProvider] = None
    ConsultingProvider: Optional[ConsultingProvider] = None
    ReferringProvider: Optional[ReferringProvider] = None
    Guarantor: Optional[Guarantor] = None
    Insurances: Optional[List[Insurance]] = None
    Location: Optional[Location3] = None


class Specimen(BaseModel):
    Source: Optional[Optional[str]] = None
    BodySite: Optional[Optional[str]] = None
    ID: Optional[Optional[str]] = None


class Procedure(BaseModel):
    Code: Optional[Optional[str]] = None
    Codeset: Optional[Optional[str]] = None
    Description: Optional[Optional[str]] = None


class Address8(BaseModel):
    StreetAddress: Optional[Optional[str]] = None
    City: Optional[Optional[str]] = None
    State: Optional[Optional[str]] = None
    ZIP: Optional[Optional[str]] = None
    County: Optional[Optional[str]] = None
    Country: Optional[Optional[str]] = None


class PhoneNumber5(BaseModel):
    Office: Optional[Optional[str]] = None


class Location4(BaseModel):
    Type: Optional[Optional[str]] = None
    Facility: Optional[Optional[str]] = None
    Department: Optional[Optional[str]] = None
    Room: Optional[Optional[str]] = None


class Provider(BaseModel):
    NPI: Optional[Optional[str]] = None
    ID: Optional[Optional[str]] = None
    IDType: Optional[Optional[str]] = None
    FirstName: Optional[Optional[str]] = None
    LastName: Optional[Optional[str]] = None
    Credentials: Optional[List] = None
    Address: Optional[Address8] = None
    EmailAddresses: Optional[List] = None
    PhoneNumber: Optional[PhoneNumber5] = None
    Location: Optional[Location4] = None


class Address9(BaseModel):
    StreetAddress: Optional[Optional[str]] = None
    City: Optional[Optional[str]] = None
    State: Optional[Optional[str]] = None
    ZIP: Optional[Optional[str]] = None
    County: Optional[Optional[str]] = None
    Country: Optional[Optional[str]] = None


class PhoneNumber6(BaseModel):
    Office: Optional[Optional[str]] = None


class Location5(BaseModel):
    Type: Optional[Optional[str]] = None
    Facility: Optional[Optional[str]] = None
    Department: Optional[Optional[str]] = None
    Room: Optional[Optional[str]] = None


class ResultCopyProvider(BaseModel):
    ID: Optional[Optional[str]] = None
    IDType: Optional[Optional[str]] = None
    FirstName: Optional[Optional[str]] = None
    LastName: Optional[Optional[str]] = None
    Credentials: Optional[List] = None
    Address: Optional[Address9] = None
    EmailAddresses: Optional[List] = None
    PhoneNumber: Optional[PhoneNumber6] = None
    Location: Optional[Location5] = None


class Address10(BaseModel):
    StreetAddress: Optional[Optional[str]] = None
    City: Optional[Optional[str]] = None
    State: Optional[Optional[str]] = None
    ZIP: Optional[Optional[str]] = None
    County: Optional[Optional[str]] = None
    Country: Optional[Optional[str]] = None


class OrderingFacility(BaseModel):
    Name: Optional[Optional[str]] = None
    Address: Optional[Address10] = None
    PhoneNumber: Optional[Optional[str]] = None


class Diagnose(BaseModel):
    Code: Optional[Optional[str]] = None
    Codeset: Optional[Optional[str]] = None
    Name: Optional[Optional[str]] = None
    Type: Optional[Optional[str]] = None
    DocumentedDateTime: Optional[Optional[str]] = None


class ClinicalInfoItem(BaseModel):
    Code: Optional[Optional[str]] = None
    Codeset: Optional[Optional[str]] = None
    Description: Optional[Optional[str]] = None
    Value: Optional[Optional[str]] = None
    Units: Optional[Optional[str]] = None
    Abbreviation: Optional[Optional[str]] = None
    Notes: Optional[List] = None


class Order(BaseModel):
    ID: str
    ApplicationOrderID: Optional[Optional[str]] = None
    Status: Optional[Optional[str]] = None
    TransactionDateTime: Optional[Optional[str]] = None
    CollectionDateTime: Optional[Optional[str]] = None
    Specimen: Optional[Specimen] = None
    Procedure: Optional[Procedure] = None
    Provider: Optional[Provider] = None
    ResultCopyProviders: Optional[List[ResultCopyProvider]] = None
    OrderingFacility: Optional[OrderingFacility] = None
    Priority: Optional[Optional[str]] = None
    Expiration: Optional[Optional[str]] = None
    Comments: Optional[Optional[str]] = None
    Notes: Optional[List] = None
    Diagnoses: Optional[List[Diagnose]] = None
    ClinicalInfo: Optional[List[ClinicalInfoItem]] = None


class Model(BaseModel):
    Meta: Meta
    Patient: Patient
    Visit: Optional[Visit] = None
    Order: Order
