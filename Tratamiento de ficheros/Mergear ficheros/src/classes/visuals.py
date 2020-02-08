#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Dependencias propias
from decorators.panel_decorator import PanelDecorator

@PanelDecorator((),conf_filename='mergeConfiguration.conf')
class Panel():
    def merge_files(self):
        print("dentro de merge_files")
        #self.logger.info("logger utilizado en clase panel correctamente")