import asyncio
import httpx
import random

from datetime import datetime

from prisma_client import prismadb


async def main() -> None:

    print("Requesting ramdom data...")

    url = "https://randomuser.me/api/?results=8&nat=br&exc=gender,location,city,state,country,registered,nat,picture,id,cell,phone,email"

    r2 = httpx.get(url)
    resp = r2.json()['results']

    stack = [
        "python",
        "javascript",
        "C#",
        "rust",
        "ruby",
        "prisma",
        "sqlalchemy",
        "postgres",
        "mysql",
        "docker"
    ]

    print("Saving to database...")

    async with prismadb as db:
        user = await db.pessoas.create_many(
            data=[{
                'apelido': p['login']['username'],
                'nome': p['name']['first'],
                'nascimento': datetime.strptime(p['dob']['date'].split('T')[0], "%Y-%m-%d"),
                'stack': random.sample(stack, random.randint(1, len(stack)))
            } for p in resp]
        )

    print("Done.")

if __name__ == '__main__':
    asyncio.run(main())

    # resp = [{'name': {'title': 'Mr', 'first': 'Hermínio', 'last': 'da Conceição'},
    #          'login': {'uuid': '73a75fef-9113-4d80-bcf3-407db826a7a8',
    #                    'username': 'yellowelephant337',
    #                    'password': 'robins',
    #                    'salt': 'Mefo1HcS',
    #                    'md5': '6666cfd5ceebe027326859661f5a4697',
    #                    'sha1': '23245fef5a4e1f7dd1003683ee5c499fc9e3e1f2',
    #                    'sha256': '1d3751fadc578746f7374bb56e6e0d7400f755a7d23e157d9324a2bf98cf5a65'},
    #          'dob': {'date': '1945-03-27T09:55:48.591Z', 'age': 78}},
    #         {'name': {'title': 'Ms', 'first': 'Gisélida', 'last': 'Araújo'},
    #          'login': {'uuid': 'f65d832d-08cb-47b6-a98e-8d5e60e97550',
    #                    'username': 'yellowgoose980',
    #                    'password': 'misfit99',
    #                    'salt': 'Z4mWTSx7',
    #                    'md5': 'dbccf8bebdeea59d4ed6119d49b709c7',
    #                    'sha1': '58eba13f1312b9d01fcea7ba7dc52f8c42e2f8ca',
    #                    'sha256': '62c0059d6c7ba4f49ce79d68bb3b898daef9096da57f5ee172c95214c6af6615'},
    #          'dob': {'date': '1995-10-31T00:40:53.145Z', 'age': 27}},
    #         {'name': {'title': 'Mr', 'first': 'Abraim', 'last': 'de Souza'},
    #          'login': {'uuid': 'e3cbb6f9-f5fe-484e-a735-8d55edb092e5',
    #                    'username': 'blackcat830',
    #                    'password': 'sirius',
    #                    'salt': 'lgQR4aVa',
    #                    'md5': '6c5dd513b103454ca1a551003bd86b5e',
    #                    'sha1': 'ea1fbd207e643311c86e51053e6e67c5a7cab811',
    #                    'sha256': 'c3cdeb4ae2e3ee36dd7935ed645d1fbafebf13695b1b9e5b43aff62cfc85f333'},
    #          'dob': {'date': '1947-01-18T22:13:54.179Z', 'age': 76}},
    #         {'name': {'title': 'Miss', 'first': 'Nairele', 'last': 'Campos'},
    #          'login': {'uuid': 'f15ee6c1-88bc-4070-9ce3-3b221abe0c0d',
    #                    'username': 'orangecat583',
    #                    'password': '000007',
    #                    'salt': '9QuTSKoC',
    #                    'md5': '38c704d35ef75b15e530beaf53868af3',
    #                    'sha1': '4cb3d7d1ad3e40811eb5496df00320e96b7bdd81',
    #                    'sha256': '721b5b8ea51e7e8fb4577ee2838ffd442663014f99370f33e9259fef029bd938'},
    #          'dob': {'date': '1984-07-08T10:09:07.576Z', 'age': 39}}]
