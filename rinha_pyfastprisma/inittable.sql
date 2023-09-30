\c rinhadb

-- CreateTable
CREATE TABLE IF NOT EXISTS "Pessoas" (
    "id" TEXT NOT NULL,
    "apelido" VARCHAR(32) NOT NULL,
    "nome" VARCHAR(100) NOT NULL,
    "nascimento" DATE NOT NULL,
    "stack" VARCHAR(32)[],

    CONSTRAINT "Pessoas_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "Pessoas_apelido_key" ON "Pessoas"("apelido");
