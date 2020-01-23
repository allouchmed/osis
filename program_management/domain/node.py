##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from typing import List

from program_management.domain.link import Link
from program_management.models.enums import node_type


class NodeFactory:
    def get_node(self, type, **kwargs):
        node_cls = {
            node_type.EDUCATION_GROUP: NodeEducationGroupYear,   # TODO: Remove when migration is done

            node_type.GROUP: NodeGroupYear,
            node_type.LEARNING_UNIT: NodeLearningUnitYear,
            node_type.LEARNING_CLASS: NodeLearningClassYear
        }[type]
        return node_cls(**kwargs)


factory = NodeFactory()


class Node:
    def __init__(self, node_id: int, path: str = None, children: List[Link] = None):
        self.node_id = node_id
        self.path = path
        if children is None:
            children = []
        self.children = children

    def add_child(self, node, **kwargs):
        child = Link(parent=self, child=node, **kwargs)
        self.children.append(child)

    @property
    def pk(self):
        return self.node_id


class NodeEducationGroupYear(Node):
    def __init__(self, node_id: int, acronym, title, year, path: str = None, children: List[Link] = None):
        super().__init__(node_id, path, children)
        self.acronym = acronym
        self.title = title
        self.year = year


class NodeGroupYear(Node):
    def __init__(self, node_id: int, acronym, title, year, path: str = None, children: List[Link] = None):
        super().__init__(node_id, path, children)
        self.acronym = acronym
        self.title = title
        self.year = year


class NodeLearningUnitYear(Node):
    def __init__(self, node_id: int, acronym, title, year, path: str = None, children: List[Link] = None):
        super().__init__(node_id, path, children)
        self.acronym = acronym
        self.title = title
        self.year = year


class NodeLearningClassYear(Node):
    def __init__(self, node_id: int, year, path: str, children: List[Link] = None):
        super().__init__(node_id, path, children)
        self.year = year


class NodeNotFoundException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__("The node cannot be found on the current tree")
