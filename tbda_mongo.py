import os

from pymongo import MongoClient
from bottle import route, run, template, static_file, TEMPLATE_PATH


# add template folders to bottlepy path
TEMPLATE_PATH.extend(('./templates/', './templates/blocks/'))

# detect if on heroku
on_heroku = 'DYNO' in os.environ

# connect with mongo (heroku)
if (on_heroku):
    client = MongoClient(
        host="mongodb://tbda_vdm:vdm_mongo_1234@ds043942.mongolab.com:43942/heroku_646gdt3n")
    db = client.heroku_646gdt3n
else:
    client = MongoClient()
    db = client.dba

# get collections
medicos = db.Medico
doentes = db.Doente

# static files
@route('/static/:path#.+#', name='static')
def index(path):
    return static_file(path, root='static')


# index
@route('/')
def index():
    return template('page', header="Trabalho 3 - MongoDB", bodyTemplate="index")


@route('/doentes')
def index():
    return template('page', rows=list(doentes.find({})), header="Listar doentes", bodyTemplate="make_table")


@route('/medicos')
def index():
    return template('page', rows=list(medicos.find({})), header="Listar médicos", bodyTemplate="make_table")


@route('/a')
def index():
    return template('page', rows=list(medicos.find({"especialidade": "Oftalmologia"},
                                                   {"nome": True, "data_nasce": True, "_id": False})),
                    header="a) Médicos Oftalmologistas", bodyTemplate="make_table")


@route('/b')
def index():
    medicos = list(globals()['medicos'].find({}, {'codm': True, 'nome': True, 'agenda': True, "_id": False}))
    for medico in medicos:
        agenda = medico['agenda']
        del medico['agenda']

        doentes = globals()['doentes'].aggregate([
            {'$unwind': '$consultas'},
            {'$match': {'consultas.codm': medico['codm']}},
            {'$project': {'nome': True, 'consultas.situacao': True, 'consultas.hora': True, 'consultas.nagenda': True,
                          'consultas.codm': True}},
            {'$group': {'_id': '$_id', 'nome': {'$first': '$nome'}, 'consultas': {'$push': '$consultas'}}}])

        medico['doentes'] = list(doentes)

        # filtrar doentes e obter dia
        for doente in medico['doentes']:
            del doente['_id']
            for consulta in doente['consultas']:
                for itemAgenda in agenda:
                    if itemAgenda['nagenda'] == consulta['nagenda']:
                        consulta['dia'] = itemAgenda['dia']
                        break		
                del consulta['nagenda']

    return template('page', rows=medicos,
                    header="b) Relatório de atividade clínica", bodyTemplate="make_table")


@route('/c')
def index():
    doentes = globals()['doentes'].aggregate([
        {'$unwind': '$consultas'},
        {'$match': {'consultas.relatorio': {'$in': ['Angina', 'Enfarte']}}},
        {'$project': {'consultas.codm': True}},
        {'$group': {'_id': '$_id', 'consultas': {'$push': '$consultas'}}}])

    medicos = list()
    codMedicos = list()

    for doente in doentes:
        for consulta in doente['consultas']:
            if consulta['codm'] not in codMedicos:
                medico = globals()['medicos'].find_one({'codm': consulta['codm']},
                                                       {'nome': True, 'especialidade': True, '_id': False})
                medicos.append(medico)
                codMedicos.append(consulta['codm'])

    return template('page', rows=medicos, header="c) Médicos que diagnosticaram 'Enfarte' ou 'Angina'",
                    bodyTemplate="make_table")


run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
