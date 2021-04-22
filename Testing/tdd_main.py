#!/usr/bin/env python
# Testing
from attr import s
import pytest
# System
import time
import os
import signal

from sqlalchemy.sql.expression import true
# Own
from .services.mocked_services import TestingArq
from arq_server.services.data_access.relational.models.User import User
from arq_server.services.protocols.logical.NormalizeSelector import NormalizeSelector

# Cases list
from .cases.core.PTConfig import pt_config_cases
from .cases.data.PTRedis import pt_redis_cases_without_caching

""" GLOBAL CONFIG """
SCOPE="session"

# Prevent pytest from trying to collect webtest's TestApp as tests:
TestingArq.__test__ = False

@pytest.fixture(scope=SCOPE)
def monkeysession(request):
	# Mockea variables de entorno en el scope fixture
    from _pytest.monkeypatch import MonkeyPatch
    mpatch = MonkeyPatch()
    mpatch.setenv('config_path_file', '/Users/rafaelgomezbermejo/Repositorios/pythonScripts/Arquitectura/arq_server/resources/config.yml')
    yield mpatch
    mpatch.undo()

@pytest.fixture(scope=SCOPE,autouse=True)
def shared_arq_instance(monkeysession):
    instance = TestingArq()
    yield instance

def obtain_test_cases_from(test_name):
	"""
	Dado el nombre del test, devuelve los casos de uso y su respuesta esperada
	"""
	
	cases_dict = {
		"service_config": pt_config_cases,
		"data_redis_without_caching" : pt_redis_cases_without_caching
	}

	return cases_dict[test_name]

def test_service_logger(shared_arq_instance:TestingArq):
	"""
	Objetivo, comprobar que funcionan todos los tipos de trazas
	"""
	logger_test= shared_arq_instance._logger_test
	test_passed = False
	try:
		logger_test.info("Traza de info")
		logger_test.debug("Traza de debug")
		logger_test.warning("Traza de warning")
		test_passed = True
	except Exception as ex:
		test_passed = False
		raise ex
	finally:
		assert test_passed

@pytest.mark.parametrize("group,key", obtain_test_cases_from("service_config"))
def test_service_config(group,key,shared_arq_instance:TestingArq):
	config_service = shared_arq_instance._config
	property = config_service.getProperty(group,key)
	assert property is not None

def test_service_sql(shared_arq_instance:TestingArq):
	sql_service = shared_arq_instance.sql_tools()
	user:User = sql_service.select_unique_item_filtering_by(User,username="RafaelGB")
	assert user.username=="RafaelGB"

@pytest.mark.parametrize("key,value", obtain_test_cases_from("data_redis_without_caching"))
def test_data_redis(key,value,shared_arq_instance:TestingArq):
	redis_cli = shared_arq_instance.redis_cli()
	redis_cli.setVal(key,value,volatile=True,timeToExpire=10)
	assert redis_cli.getVal(key)==value

def test_docker_cli(shared_arq_instance:TestingArq):
	docker_tools = shared_arq_instance.docker_cli()
	docker_tools.runContainer("hello-world","prueba",auto_remove=True,detach=True)
	time.sleep(5)
	docker_tools.removeContainer("prueba")
	
def test_unconfigure(shared_arq_instance:TestingArq):
    # I close all ssh connection here
	shared_arq_instance.restTools.stop_server()
	assert True