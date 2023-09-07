import os
import logging
import uuid
from pathlib import Path
from typing import List

from rdflib import Graph
from rdflib.query import Result, ResultRow
from dataclasses import dataclass, field

from drb.topics.dao.topic_dao import DrbTopicDao
from drb.core.signature import parse_signature, Signature
from drb.topics.topic import DrbTopic, TopicCategory
from drb.exceptions.core import DrbException

logger = logging.getLogger('DrbTopic')


class RDFDao(DrbTopicDao):

    __triple = {'.owl': 'application/rdf+xml', '.ttl': 'turtle'}

    def __init__(self, path: str):
        # if not existing, generate a new file.
        Path(path).touch(exist_ok=True)
        self.__file = path
        self.__format = self.__triple[os.path.splitext(path)[1]]
        self.__result = self.__query_rdf_file()

    def __query_rdf_file(self) -> Result:
        """
        Search for all topics in an RDF supported resource.
        Returns:
            SPARQLResult: list containing found topics
        """

        path = os.path.join(self.__file)
        self.graph = Graph()
        self.graph.parse(source=path, format=self.__format)
        result = self.graph.query("""
                SELECT ?Class ?label ?id ?category ?factory
                (GROUP_CONCAT(DISTINCT IF(BOUND(?parentClassId),
                STR(?parentClassId),
                ?parentClass); separator="§ ") AS ?parentClasses)
                WHERE {
                ?Class a owl:Class .
                ?Class rdfs:label ?label .
                OPTIONAL { ?Class drb:id ?id .}
                OPTIONAL { ?Class drb:category ?category .}
                OPTIONAL { ?Class drb:implementationIdentifier ?factory .}
                OPTIONAL {
                ?Class rdfs:subClassOf ?parentClass .
                OPTIONAL { ?parentClass drb:id ?parentClassId .}
                }
                }
                GROUP BY ?Class
                """)

        return result

    def get_topic_signature(self, topic: DrbTopic):

        result = self.graph.query(f'''
                SELECT ?name
                WHERE {{
                ?Class a owl:Class .
                FILTER(?Class = <{topic.uri}>)
                ?Class drb:signature ?signature .
                OPTIONAL {{ ?signature drb:nameMatch ?name . }}
                }}
                GROUP BY ?signature
                ''')
        signatures = []
        for row in result:
            signature = {}
            for k in row.asdict().keys():
                signature.update({k: row[k].toPython()})
            signatures.append(parse_signature(signature))

        topic.signatures = signatures
        topic.sign_is_loaded = True
        return signatures

    def __generate_topic_from_rdf(self, row: ResultRow) -> DrbTopic:
        """
        Converts a row into a dictionary used for generating RDFTopic(s).
        Parameters:
            row (ResultRow): row to convert
        Returns:
            DrbTopic: the corresponding topic
        """
        data = {}
        uri_parents = str(row.parentClasses).split("§ ") if str(
            row.parentClasses) else None
        data['uri'] = row.Class.toPython()
        data['label'] = row.label.toPython()
        if row.id is not None:
            data['id'] = uuid.UUID(row.id.toPython())
        else:
            data['id'] = self.generate_id(data['uri'])
        if row.category is not None:
            data['category'] = TopicCategory(row.category.toPython())
        else:
            data['category'] = TopicCategory('CONTAINER')
        if row.factory is not None:
            data['factory'] = row.factory.toPython()

        parents = []
        if uri_parents is not None:
            for uri_parent in uri_parents:
                try:
                    parents.append(uuid.UUID(uri_parent))
                except ValueError:
                    parents.append(self.generate_id(uri_parent))
            data['subClassOf'] = parents

        topic = RDFTopic(**data, dao=self)
        return topic

    @staticmethod
    def generate_id(uri: str) -> uuid.UUID:
        """
        Generates an unique UUID from topic's unique URI.
        Parameters:
            uri (str): topic's unique URI
        Returns:
            UUID: topic's unique
        """
        return uuid.uuid3(uuid.NAMESPACE_DNS, uri)

    def read(self, identifier: uuid.UUID) -> DrbTopic:
        """
        Reads a topic from an RDF file.
        Parameters:
            identifier (UUID): id of topic to read from file
        Returns:
            DrbTopic: the topic corresponding to the given identifier
                """

        for r in self.__result:
            if r.id is not None:

                if uuid.UUID(r.id.toPython()) == identifier:
                    topic = self.__generate_topic_from_rdf(r)
                    return topic
            else:
                uri = r.Class.toPython()
                id_from_uri = self.generate_id(uri)
                if id_from_uri == identifier:
                    topic = self.__generate_topic_from_rdf(r)
                    return topic

            continue

        raise DrbException

    def find(self, search: str) -> List[DrbTopic]:
        """
        Finds a topic from an RDF file.
        Parameters:
            search (str): label of topic to read from file
        Returns:
            List[DrbTopic]: the topic corresponding to the given label
        """
        topics = []
        for r in self.__result:
            if search in r.label.toPython():
                topic = self.__generate_topic_from_rdf(r)
                topics.append(topic)

        return topics

    def read_all(self) -> List[DrbTopic]:
        """
        Loads all topics defined in RDF files.
        """

        topics = []

        for r in self.__result:

            try:
                topic = self.__generate_topic_from_rdf(r)
                topics.append(topic)

            except TypeError:
                continue

        return topics

    def create(self, topic: DrbTopic) -> DrbTopic:
        raise NotImplementedError

    def update(self, topic: DrbTopic) -> DrbTopic:
        raise NotImplementedError

    def delete(self, identifier: uuid.UUID) -> None:
        raise NotImplementedError


@dataclass
class RDFTopic(DrbTopic):
    dao: RDFDao = field(default=None, repr=False)
    sign_is_loaded: bool = field(default=False, repr=False)

    @property
    def signatures(self) -> List[Signature]:
        if self.sign_is_loaded:
            return self._signatures
        else:
            return self.dao.get_topic_signature(self)

    @signatures.setter
    def signatures(self, signatures: List[Signature]):
        self._signatures = signatures
