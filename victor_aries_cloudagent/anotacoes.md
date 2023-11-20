# Anotações

Para instalar os Ledgers no exemplo Alice/Faber, foi necessário instalar o Ubuntu 18.04, seguir o guia de instalação (https://github.com/LDVictor/victor-aries-cloudagent/blob/main/demo/README.md) e instalar todas as extensões via pip 3.

Para executar o exemplo, é necessário a seguinte adaptação:

 - Executando VON Network:

$ cd von-network/
$ ./manage build
$ ./manage start --logs

 - Instalando extensões necessárias:

$ sudo -H pip3 install --upgrade pip

$ pip3 install multidict typing_extensions attr yarl async_timeout idna_ssl attrs charset_normalizer aiosignal qrcode asyncpg "prompt-toolkit<3.0.0" pygments aries-askar==0.2.7 pydid aiohttp-apispec aiohttp_cors PyJWT PyLD nest-asyncio markdown deepmerge indy-vdr indy-credx python-dateutil==2.8.2

$ python3 -m pip install aiohttp configargparse base58

$ pip install runners

 - Executando Faber

$ cd victor-aries-cloudagent/demo/
$ LEDGER_URL=http://localhost:9000 DEFAULT_POSTGRES=true python3 -m runners.faber --port 8020

 - Executando Alice

$ cd victor-aries-cloudagent/demo/
$ LEDGER_URL=http://localhost:9000 DEFAULT_POSTGRES=true python3 -m runners.alice --port 8030
