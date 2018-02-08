'''
Created on DEC 29, 2017

@author: NNA
'''

import cast.analysers.jee
import cast.application
import cast.analysers.log as LOG
import os
from cast.analysers import Member,Bookmark
from setuptools.sandbox import _file
import xml.etree.ElementTree as ET
from Cython.Compiler.Options import annotate


def get_overriden(_type, member):
    """
    Get the ancestor's member this member overrides
    """
    member_name = member.get_name()
    
    result = []
    
    for parent in _type.get_inherited_types():
        
        for child in parent.get_children():
            if child.get_name() == member_name:
                result.append(child)
        
        result += get_overriden(parent, member)
        
    return result

class search(cast.analysers.jee.Extension):
    def __init__(self):
        self.result = None
        self.count = 0
        self.jmstext=""
        self.jmsmetamodeltext =""
        
               
    def start_analysis(self,options):
        LOG.info('Successfully spring jms analyzer Started')
        options.add_classpath('jars')
        options.handle_xml_with_xpath('/beans')
        options.handle_xml_with_xpath('/')
        
       
      
    def start_member(self, member):
        for anno in member.get_annotations():
            LOG.info('memebr'+ str(anno[0]))
            self.findannotation(anno, 'org.springframework.jms.annotation.JmsListener', member)
            
         
       
    # receive a java parser from platform
    @cast.Event('com.castsoftware.internal.platform', 'jee.java_parser')
    def receive_java_parser(self, parser):
        self.java_parser = parser
        LOG.info('Successfully receive_java_parser')
        pass
        
    def findannotation(self, anno, annotext, member):
        if anno[0].get_fullname() == annotext:
            LOG.info('anno'+ str(anno[1]))
            annvalue=anno[1]
            if annvalue['destination'] is not None:
                self.jmstext='destination'
                self.jmsmetamodeltext= 'SpringJmsListener'
                #LOG.info('JmsListener'+ str(annvalue['destination']))
                self.Createannjms(member,anno[1],  annotext)
               
    def Createannjms(self,typ,annoValue, annotext):
        annjms = cast.analysers.CustomObject()
        annjms.set_name(annoValue[self.jmstext])
        annjms.set_type(self.jmsmetamodeltext)
        parentFile = typ.get_position().get_file() 
        annjms.set_parent(parentFile)
        annjms.set_fullname(typ.get_fullname())  
        self.fielPath = parentFile.get_fullname()
        self.count= self.count+1
        annjms.set_guid(self.fielPath+annoValue[self.jmstext] +str(self.count))
        annjms.save()
        annjms.save_position(typ.get_position())
        cast.analysers.create_link('callLink',  annjms, typ )
        LOG.info(annotext+  '   object is created with name '+ annoValue[self.jmstext])
        Parsing.add_property(annjms, 'destination',annoValue )
        Parsing.add_property(annjms, 'id', annoValue)
        Parsing.add_property(annjms, 'selector',annoValue )
        Parsing.add_property(annjms, 'subscription', annoValue)
        Parsing.add_property(annjms, 'containerFactory', annoValue)
        Parsing.add_property(annjms, 'concurrency', annoValue)
        Parsing.addtype_property(annjms, 'sourcetype', annotext.rsplit('.', 1)[-1])
        Parsing.addtype_property(annjms, 'sourcefile', 'java')
        return self.Createannjms; 
    
    
    def start_xml_file(self, file):
        LOG.info('Scanning XML test file :' )
        if file.get_name().endswith('.xml'):
            if (os.path.isfile(file.get_path())):
                tree = ET.parse(file.get_path(), ET.XMLParser(encoding="UTF-8"))
                root=tree.getroot()
                for a in root.iter():
                  self.findJmsXMLdestination(a, '{http://www.springframework.org/schema/jms}listener-container', file)               
    
    def findJmsXMLdestination(self, a, xsdtext, file):  
        if a.tag == xsdtext:
            LOG.info('Scanning inside jms container :' )
            for node in a.getiterator():
                if node.tag=='{http://www.springframework.org/schema/jms}listener':
                     LOG.info("inside listener child")
                     nodetext ='{http://www.springframework.org/schema/jms}listener'
                     self.jmstext='destination'
                     self.jmsmetamodeltext= 'SpringJmsListener'
                     self.CreateaXMLjms(file,a, nodetext, node)
                    
                             
    def CreateaXMLjms(self,file, a, xsdtext, node):
        try :
            
            if node.tag == xsdtext:
                self.count= self.count+1
                jmsObj = cast.analysers.CustomObject()
                jmsObj.set_name(node.get(self.jmstext))
                jmsObj.set_type(self.jmsmetamodeltext)
                jmsObj.set_parent(file)
                parentFile = file.get_position().get_file() 
                self.fielPath = parentFile.get_fullname()
                jmsObj.set_guid(self.fielPath+node.get(self.jmstext)+str(self.count))
                jmsObj.save()
                jmsObj.save_position(file.get_position())
                Parsing.add_property(jmsObj,  'destination', node)
                Parsing.add_jmsproperty(jmsObj, node,  'id', 'ref' )
                Parsing.add_jmsproperty(jmsObj, node,  'containerFactory', 'method')
                Parsing.addtype_property(jmsObj, 'sourcetype', self.jmsmetamodeltext )
                Parsing.addtype_property(jmsObj, 'sourcefile', 'XML')
                LOG.info('Creating xml JMS '+ xsdtext + ' object '+ node.get(self.jmstext))  
               
        except:
            return 
    def end_analysis(self):
        self.result
        
        #LOG.info("search Analyzer Analyzer Ended")
        
        
class Parsing():  
    
    @staticmethod
    def add_property(obj,  prop, ele ):
        if ele.get(prop) is not None:
            LOG.debug(' - %s: %s' % (prop, ele.get(prop)))
            obj.save_property('JmsListenerProperties.%s' % prop, ele.get(prop))
        else:
            obj.save_property('JmsListenerProperties.%s' % prop, "None")
            
    @staticmethod
    def add_jmsproperty(obj, ele, prop, proptext ):
        if ele.get(proptext) is not None:
            LOG.debug(' - %s: %s' % (prop, ele.get(proptext)))
            obj.save_property('JmsListenerProperties.%s' % prop, ele.get(proptext) )
        else:
            obj.save_property('JmsListenerProperties.%s' % prop, "None")  
            
            
    @staticmethod
    def addtype_property(obj,  prop, proptext):
        if proptext is not None:
            obj.save_property('JmsListenerProperties.%s' % prop, proptext)
        else:
            obj.save_property('JmsListenerProperties.%s' % prop, "None") 
            
   
