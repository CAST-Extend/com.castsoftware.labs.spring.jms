'''
Created on Dec 29, 2017

@author: NNA
'''

import cast.application
import logging
import ast
import re

class ExtensionApplication(cast.application.ApplicationLevelExtension):

    def end_application(self, application):
        logging.info("Running code at the end of an Application")
        self.Createxmljmslink(application,'SpringJmsListener')
        
    def Createxmljmslink(self,application,jmstext):
        jmsObjectReferences = list(application.search_objects(category=jmstext, load_properties= True))
        javaMethodObjectReferences = list(application.search_objects(category='JV_METHOD', load_properties=False))
        javaMethodclassReferences = list(application.search_objects(category='JV_CLASS', load_properties=False))
        if len(jmsObjectReferences)>0:
            for jmsObject in jmsObjectReferences :
                    #logging.info('method_name --> ' + jmsObject.get_name())
                    xml_type = jmsObject.get_property('JmsListenerProperties.sourcefile')
                    if xml_type.lower() == 'xml':
                        method_name = jmsObject.get_property('JmsListenerProperties.containerFactory')
                        for javaObject in javaMethodObjectReferences : 
                            javamethod_name = javaObject.get_name()
                            if javamethod_name ==  method_name:
                                #logging.info('method_name --> '+javamethod_name)
                                cast.application.create_link("callLink", jmsObject, javaObject, bookmark=None) 
                                logging.debug("link created-->" + method_name)
                                for javaclassObject in javaMethodclassReferences : 
                                    #logging.info('class_name --> ' + javaclassObject.get_name())
                                    javaclassmethod_name = javaclassObject.get_name()
                                    classmethod_name = jmsObject.get_property('JmsListenerProperties.id')
                                    if javaclassmethod_name ==  classmethod_name:
                                        #logging.info('method_name --> '+javaclassmethod_name)
                                        cast.application.create_link("callLink", jmsObject, javaclassObject, bookmark=None)
                                        logging.debug("link created-->" + classmethod_name) 
        