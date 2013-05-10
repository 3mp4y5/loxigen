# Copyright 2013, Big Switch Networks, Inc.
#
# LoxiGen is licensed under the Eclipse Public License, version 1.0 (EPL), with
# the following special exception:
#
# LOXI Exception
#
# As a special exception to the terms of the EPL, you may distribute libraries
# generated by LoxiGen (LoxiGen Libraries) under the terms of your choice, provided
# that copyright and licensing notices generated by LoxiGen are not altered or removed
# from the LoxiGen Libraries and the notice provided below is (i) included in
# the LoxiGen Libraries, if distributed in source code form and (ii) included in any
# documentation for the LoxiGen Libraries, if distributed in binary form.
#
# Notice: "Copyright 2013, Big Switch Networks, Inc. This library was generated by the LoxiGen Compiler."
#
# You may not use this file except in compliance with the EPL or LOXI Exception. You may obtain
# a copy of the EPL at:
#
# http://www.eclipse.org/legal/epl-v10.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# EPL for the specific language governing permissions and limitations
# under the EPL.

import copy
import of_g
import loxi_front_end.type_maps as type_maps
from loxi_ir import *

class InputError(Exception):
    pass

def create_member(m_ast):
    if m_ast[0] == 'pad':
        return OFPadMember(length=m_ast[1])
    elif m_ast[0] == 'type':
        return OFTypeMember(name=m_ast[2], oftype=m_ast[1], value=m_ast[3])
    elif m_ast[0] == 'data':
        if m_ast[2] == 'length' or m_ast[2] == 'len': # Should be moved to parser
            return OFLengthMember(name=m_ast[2], oftype=m_ast[1])
        elif m_ast[2] == 'actions_len':
            # HACK only usage so far
            return OFFieldLengthMember(name=m_ast[2], oftype=m_ast[1], field_name='actions')
        else:
            return OFDataMember(name=m_ast[2], oftype=m_ast[1])

def create_ofinput(ast):
    """
    Create an OFInput from an AST

    @param ast An AST as returned by loxi_front_end.parser.parse

    @returns An OFInput object
    """

    ofinput = OFInput(wire_versions=set(), classes=[], enums=[])

    for decl_ast in ast:
        if decl_ast[0] == 'struct':
            members = [create_member(m_ast) for m_ast in decl_ast[2]]
            ofclass = OFClass(name=decl_ast[1], members=members)
            ofinput.classes.append(ofclass)
            if ofclass.name in type_maps.inheritance_map:
                # Clone class into header class and add to list
                # TODO figure out if these are actually used
                ofclass_header = OFClass(ofclass.name + '_header',
                                         copy.deepcopy(members))
                ofinput.classes.append(ofclass_header)
        if decl_ast[0] == 'enum':
            enum = OFEnum(name=decl_ast[1], values=[(x[0], x[1]) for x in decl_ast[2]])
            ofinput.enums.append(enum)
        elif decl_ast[0] == 'metadata':
            if decl_ast[1] == 'version':
                if decl_ast[2] == 'any':
                    ofinput.wire_versions.update(of_g.wire_ver_map.keys())
                elif int(decl_ast[2]) in of_g.supported_wire_protos:
                    ofinput.wire_versions.add(int(decl_ast[2]))
                else:
                    raise InputError("Unrecognized wire protocol version %r" % decl_ast[2])
                found_wire_version = True

    if not ofinput.wire_versions:
        raise InputError("Missing #version metadata")

    return ofinput