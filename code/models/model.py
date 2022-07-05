from datetime import date, datetime
from pydantic import BaseModel, Field, EmailStr


#class PostSchema(BaseModel):
#    id: int = Field(default=None)
#    title: str = Field(...)
#    content: str = Field(...)

#    class Config:
#        schema_extra = {
#            "example": {
#                "title": "Titulo do post...",
#                "content": "Conteúdo do post..."
#            }
#        }

#class UserSchema(BaseModel):
#    fullname: str = Field(...)
#    email: EmailStr = Field(...)
#    password: str = Field(...)
#
#    class Config:
#        schema_extra = {
#            "example": {
#                "fullname": "Jean Pablo Dreyer",
#                "email": "djean@tcheturbo.com.br",
#                "password": "testej"
#            }
#        }

class UserLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "email": "",
                "password": ""
            }
        }

class WhTelecallSchema(BaseModel):
    PORTABILITY: str = Field(...)
    STATUS: str = Field(...)
    NAME: str = Field(...)
    DOCUMENT_ID: str = Field(...)
    IS_LEGAL_ENTITY: str = Field(...)
    MSISDN: str = Field(...)
    REQUESTED_DATE: datetime = Field(...)
    SCHEDULED_DATE: datetime = Field(...)
    OPERATION_DATE: datetime = Field(...)
    MESSAGE: str = Field(...)

    class Config:
        schema_extra = {
            "request_exemple": {
                                "PORTABILITY":"IN",	
                                "STATUS":"Sucesso",	
                                "NAME":"TESTE JEAN!",	
                                "DOCUMENT_ID":"000.000.082-47",	
                                "IS_LEGAL_ENTITY":"Pessoa_Fisica",	
                                "MSISDN":"5516936180000",	
                                "REQUESTED_DATE":"2021-04-01 10:59:59",	
                                "SCHEDULED_DATE":"2021-04-10 14:59:59",	
                                "OPERATION_DATE":"2021-04-25 23:59:59",	
                                "MESSAGE":"Processo Concluido com Sucesso"
            }
        }