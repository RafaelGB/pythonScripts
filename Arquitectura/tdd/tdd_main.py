#!/usr/bin/env python
# Testing
import pytest
from mock import patch
# System
import time
# Own
from tdd.services.mocked_services import TestingArq
from arq_server.services.data_access.relational.models.User import User

SCOPE="session"

@pytest.fixture(scope=SCOPE)
def monkeysession(request):
	# Mockea variables de entorno en el scope fixture
    from _pytest.monkeypatch import MonkeyPatch
    mpatch = MonkeyPatch()
    mpatch.setenv('config_path_file', '/Users/rafaelgomezbermejo/Repositorios/pythonScripts/Arquitectura/tdd/resources/config.yml')
    yield mpatch
    mpatch.undo()

@pytest.fixture(scope=SCOPE)
def shared_arq_instance(monkeysession):
    instance = TestingArq()
    yield instance

def test_check_config(shared_arq_instance:TestingArq):
	config = shared_arq_instance.config_container()
	# Check core is not null
	assert 'log_conf_path' in config.core.logger()

def test_logger_service(shared_arq_instance:TestingArq):
	logger_service = shared_arq_instance.get_logger_service()
	test_passed = False
	try:
		arqLogger = logger_service.arqLogger()
		arqLogger.info("Traza de info")
		arqLogger.debug("Traza de debug")
		test_passed = True
	except Exception as ex:
		test_passed = False
		raise ex
	finally:
		assert test_passed

def test_config_service(shared_arq_instance:TestingArq):
	config_service = shared_arq_instance.get_config_service()
	property = config_service.getProperty("logical","avaliableInputKeys")
	assert property is not None

def test_sql_service(shared_arq_instance:TestingArq):
	sql_service = shared_arq_instance.get_sql_service()
	sql_service.select_items_filtering_by(User,)
	assert property is not None