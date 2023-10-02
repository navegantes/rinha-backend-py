from typing import List, Optional, Union
from datetime import datetime
from fastapi import (
    FastAPI,
    HTTPException,
    Request,
    status,
)
from uuid import uuid4
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, UUID4, validator

from src.prisma_client import prismadb

# -------------------------------
# models.py


class Pessoa(BaseModel):
    apelido: str = Field(..., max_length=32)
    nome: str = Field(..., max_length=100)
    nascimento: str = Field(...)
    stack: Optional[List[str]] = None


# class PessoaDb(Pessoa):
#     id: UUID4

# # Isso aqui é toque. Pro Id ficar em primeiro
# class PessoaID(BaseModel):
#     id: UUID4
# class PessoaDb(Pessoa, PessoaID):
#     pass
# -------------------------------


app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(req: Request, exc: RequestValidationError):
    details = exc.errors()
    print("DETAIL", details)
    # if detail['input'], int)
    if any(detail['type'] == 'string_type' and isinstance(detail['input'], int) for detail in details):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder({'detail': details}),
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({'detail': details}),
    )


@app.get("/")
async def read_users():

    return {"Hello Rinha de Backend!"}


@app.post("/pessoas")
async def cria_pessoa(pessoa: Pessoa):

    async with prismadb as db:
        query = await db.pessoas.find_first(
            where={'apelido': pessoa.apelido},
        )
        if query is not None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"O apelido {pessoa.apelido} já existe."
            )

        if pessoa.stack is None:
            pessoa.stack = []

        nova_pessoa = await db.pessoas.create(
            data={
                **pessoa.model_dump(),
                "nascimento": datetime.strptime(pessoa.nascimento, "%Y-%m-%d"),
            }
        )

    headers = {"Location": f"/pessoas/{nova_pessoa.id}"}

    return JSONResponse(
        content={"created": nova_pessoa.id},
        headers=headers,
        status_code=status.HTTP_201_CREATED
    )


@app.get("/pessoas/{id}")
async def busca_id(id: str):
    async with prismadb as db:
        pessoa = await db.pessoas.find_unique(where={'id': id})

        if pessoa is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"A pessoa com ID {id} não existe."
            )

    return JSONResponse(
        content=jsonable_encoder(pessoa.id),
        status_code=status.HTTP_200_OK
    )


@app.get("/pessoas")
async def busca_termo(t: str):

    if t == "":
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    async with prismadb as db:
        pessoas = await db.pessoas.find_many(
            take=50,
            where={
                'OR': [
                    {'apelido': {'contains': t, 'mode': 'insensitive'}, },
                    {'nome': {'contains': t, 'mode': 'insensitive'}},
                    {'stack': {'has': t.capitalize()}},
                    {'stack': {'has': t.lower()}},
                ]
            }
        )

    return JSONResponse(
        content=jsonable_encoder({
            "search": t,
            "pessoas": pessoas
        }),
        status_code=status.HTTP_200_OK
    )


@app.get("/contagem-pessoas", status_code=status.HTTP_200_OK)
async def contagem() -> dict:
    async with prismadb as db:
        pessoas = await db.pessoas.count()

    return {
        "count": f"{pessoas} registros encontrados",
    }
