#!/usr/bin/env python
# Testing
import pytest
from mock import patch
# System
import time
# Own
from tdd.services.mocked_services import TestingArq
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

@pytest.fixture(scope=SCOPE)
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

def test_container_config(shared_arq_instance:TestingArq):
	config = shared_arq_instance.config_container()
	# Check core is not null
	assert 'log_conf_path' in config.core.logger()

def test_service_logger(shared_arq_instance:TestingArq):
	"""
	Objetivo, comprobar que funcionan todos los tipos de trazas
	"""
	logger_service = shared_arq_instance.get_logger_service()
	test_passed = False
	try:
		arqLogger = logger_service.testingLogger()
		arqLogger.info("Traza de info")
		arqLogger.debug("Traza de debug")
		arqLogger.warning("Traza de warning")
		test_passed = True
	except Exception as ex:
		test_passed = False
		raise ex
	finally:
		assert test_passed

@pytest.mark.parametrize("group,key", obtain_test_cases_from("service_config"))
def test_service_config(group,key,shared_arq_instance:TestingArq):
	config_service = shared_arq_instance.get_config_service()
	property = config_service.getProperty(group,key)
	assert property is not None

def test_service_sql(shared_arq_instance:TestingArq):
	sql_service = shared_arq_instance.get_sql_service()
	user:User = sql_service.select_unique_item_filtering_by(User,username="RafaelGB")
	assert user.username=="RafaelGB"

@pytest.mark.parametrize("key,value", obtain_test_cases_from("data_redis_without_caching"))
def test_data_redis(key,value,shared_arq_instance:TestingArq):
	redis_cli = shared_arq_instance.get_redis_data_cli()
	redis_cli.setVal(key,value,volatile=True,timeToExpire=10)
	assert redis_cli.getVal(key)==value


