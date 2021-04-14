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

def test_service_config(shared_arq_instance:TestingArq):
	config_service = shared_arq_instance.get_config_service()
	property = config_service.getProperty("logical","avaliableInputKeys")
	assert property is not None

def test_service_sql(shared_arq_instance:TestingArq):
	sql_service = shared_arq_instance.get_sql_service()
	user:User = sql_service.select_unique_item_filtering_by(User,username="RafaelGB")
	assert user.username=="RafaelGB"


def test_service_concurrent(shared_arq_instance:TestingArq):
	try:
		concurrentTools = shared_arq_instance.get_concurrent_tools()
		logger = shared_arq_instance.get_logger_service().testingLogger()
		iter = 24
		centinel = 0
		test_isOK = False
		args = 3,6

		def __procesoPesado(arg):
			time.sleep(1)
			arg = arg*2
			return arg
		
		for i in range(iter):
			concurrentTools.createProcess(
				__procesoPesado,
				*args
			)
		
		logger.info("Lanzando los procesos en paralelo")
		# Check sobre funcionamiento correcto
		timeout = 0
		while not test_isOK and timeout<10:
			time.sleep(1)
			timeout= timeout+1
		logger.info("centinela tras la espera:%s",str(centinel))
	except Exception as e:
		test_isOK = False
		raise e
	finally:
		assert test_isOK