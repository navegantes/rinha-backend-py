from typing import List, Optional, Union
from datetime import datetime
from fastapi import (
    FastAPI,
    HTTPException,
    status,
)
from uuid import UUID, uuid4
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.prisma_client import prismadb

# -------------------------------
# models.py


class Pessoa(BaseModel):
    apelido: str = Field(..., max_length=32)
    nome: str = Field(..., max_length=100)
    nascimento: str = Field(...)
    stack: Optional[List[str]] = None


# Isso aqui é toque. Pro Id ficar em primeiro
class PessoaID(BaseModel):
    id: UUID


class PessoaDb(Pessoa, PessoaID):
    pass

# -------------------------------


app = FastAPI()


@app.get("/")
async def read_users():

    return {"Hello Rinha de Backend!"}


@app.post("/pessoas")
async def cria_pessoa(pessoa: Pessoa):

    req_pessoa = Pessoa(**pessoa.model_dump())

    if req_pessoa.nome.isnumeric():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O campo nome deve ser string e não número"
        )
    if req_pessoa.stack is None:
        req_pessoa.stack = []
    elif req_pessoa.stack is None and any(item.isnumeric() for item in nova_pessoa.stack):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O campo stack dever ser uma lista de strings"
        )

    async with prismadb as db:
        query = await db.pessoas.find_unique(
            where={'apelido': req_pessoa.apelido},
        )
        if query is not None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"O apelido {req_pessoa.apelido} já existe."
            )

        nova_pessoa = await db.pessoas.create(
            data={
                **req_pessoa.model_dump(),
                "nascimento": datetime.strptime(req_pessoa.nascimento, "%Y-%m-%d"),
            }
        )

    headers = {"Location": f"/pessoas/{nova_pessoa.id}"}

    return JSONResponse(
        content={"created": jsonable_encoder(nova_pessoa)},
        headers=headers,
        status_code=status.HTTP_201_CREATED
    )


@app.get("/pessoas/{id}")
async def busca_id(id: str):
    async with prismadb as db:
        pessoa = await db.pessoas.find_unique(
            where={'id': id},
        )

        if pessoa is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"A pessoa com ID {id} não existe."
            )
        pessoa = PessoaDb(
            **pessoa.model_dump(exclude={"nascimento"}),
            nascimento=pessoa.nascimento.strftime("%Y-%m-%d")
        )

    return JSONResponse(
        content=jsonable_encoder(pessoa),
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
