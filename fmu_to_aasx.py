"""
This module contains the functionality to generate standardized submodels from a given .fmu file

Note, that this script can only deal with .fmu files following version 2.0.* of the FMU specification

Todo: This can only deal with scalar variables
"""
import os

from lxml import etree
import zipfile
from typing import List, Optional
import dataclasses
from sys import argv

from aas import model
from aas.adapter import aasx


@dataclasses.dataclass
class FMUScalarVariable:
    name: str
    type: str
    causality: str
    unit: str = ""
    description: str = ""
    prefix: str = ""
    range: str = ""


def parse_model_variables(filename: str) -> List[FMUScalarVariable]:
    """
    Parses the model variables from the <ModelVariables> tag from the .fml file

    :return: Dict {"inputs": [...], "outputs": [...]}, where one element looks like this (name, type)
    """
    archive = zipfile.ZipFile(filename)
    xml_data = archive.open("modelDescription.xml")
    root = etree.parse(xml_data).getroot()
    for child in root:
        if child.tag == "ModelVariables":
            variables: List[FMUScalarVariable] = []
            for variable in child:
                if variable.tag == "ScalarVariable":
                    name: Optional[str] = variable.get("name")
                    if not name:
                        raise KeyError("Could not find name for {}".format(variable))
                    if name.startswith("der(") \
                            or name.startswith("ContinuousStates.") \
                            or name.startswith("Parameters."):
                        pass
                    else:
                        fmu = FMUScalarVariable(
                            name=name,
                            type=variable[0].tag,
                            unit=variable.get("unit"),
                            description=variable.get("description"),
                            causality=variable.get("causality"),
                            prefix=variable.get("prefix"),
                            range=variable.get("range")
                        )
                        if not fmu.description:
                            fmu.description = ""
                        if not fmu.unit:
                            fmu.unit = ""
                        if not fmu.prefix:
                            fmu.prefix = ""
                        if not fmu.range:
                            fmu.range = ""
                        variables.append(fmu)
            return variables


def fmu_scalar_variable_to_ports_connector_smc(
        variable: FMUScalarVariable,
        id_short: str
) -> model.SubmodelElementCollectionOrdered:
    """
    Create the SubmodelElementCollection 'portsConnector' from a given FMU Scalar Variable

    :param variable:
    :param id_short: The id_short for the portsConnector SMC. Usually numbered like: 'portsConnector01', etc.
    :return:
    """
    smc = model.SubmodelElementCollectionOrdered(id_short=id_short)
    smc.value.add(model.Property(id_short="portConName", value_type=model.datatypes.String, value=variable.name))
    smc.value.add(model.Property(id_short="portConDescription", value_type=model.datatypes.String, value=variable.description))
    smc.value.add(model.Property(id_short="unit", value_type=model.datatypes.String, value=variable.unit))

    variable_smc = model.SubmodelElementCollectionOrdered(id_short="variable01")
    variable_smc.value.add(model.Property(id_short="variableName",
                                          value_type=model.datatypes.String,
                                          value=variable.name))
    variable_smc.value.add(model.Property(id_short="variableDescription",
                                          value_type=model.datatypes.String,
                                          value=variable.description))
    variable_smc.value.add(model.Property(id_short="unitDescription",
                                          value_type=model.datatypes.String,
                                          value=variable.unit))
    variable_smc.value.add(model.Property(id_short="type",
                                          value_type=model.datatypes.String,
                                          value=variable.type))
    variable_smc.value.add(model.Property(id_short="causality",
                                          value_type=model.datatypes.String,
                                          value=variable.causality))
    variable_smc.value.add(model.Property(id_short="prefix",
                                          value_type=model.datatypes.String,
                                          value=variable.prefix))
    variable_smc.value.add(model.Property(id_short="range",
                                          value_type=model.datatypes.String,
                                          value=variable.range))

    smc.value.add(variable_smc)
    return smc


def simulation_model_from_fmu_file(filename: str, id_short: str) -> model.SubmodelElementCollectionOrdered:
    """
    Create a standardized 'SimulationModel' SubmodelElementCollection

    :param filename:
    :param id_short: id_short of the returned 'SimulationModel' SMC (typically numbered, e.g. 'SimulationModel01')
    :return:
    """
    sm = model.SubmodelElementCollectionOrdered(id_short=id_short)

    model_file = model.SubmodelElementCollectionOrdered(id_short="modelFile")
    model_file.value.add(model.File(id_short="fmuFile", mime_type="application/fmu", value="/{}".format(filename)))

    sm.value.add(model_file)
    sm.value.add(
        model.Property(id_short="paramMethod", value_type=model.datatypes.String, value="Link to para-file")
    )
    sm.value.add(
        model.File(id_short="paramFile", mime_type="application/fmu", value="/{}".format(filename))
    )
    sm.value.add(
        model.Property(id_short="initStateMethod", value_type=model.datatypes.String, value="Link to para-file")
    )
    sm.value.add(
        model.File(id_short="initStateFile", mime_type="application/fmu", value="/{}".format(filename))
    )
    sm.value.add(
        model.Property(id_short="refSimDocumentation01", value_type=model.datatypes.String, value="UNKNOWN")
    )
    sm.value.add(
        model.Property(id_short="integrationMethod", value_type=model.datatypes.String, value="UNKNOWN")
    )
    sm.value.add(
        model.Property(id_short="licenceModel", value_type=model.datatypes.String, value="UNKNOWN")
    )
    sm.value.add(
        model.SubmodelElementCollectionOrdered(id_short="levelOfDetail")
    )
    sm.value.add(
        model.SubmodelElementCollectionOrdered(id_short="simulationSupportContact")
    )
    sm.value.add(
        model.Property(id_short="engineeringDomain01", value_type=model.datatypes.String, value="UNKNOWN")
    )
    sm.value.add(
        model.SubmodelElementCollectionOrdered(id_short="solverAndTolerances01")
    )
    sm.value.add(
        model.SubmodelElementCollectionOrdered(id_short="simPurpose")
    )
    sm.value.add(
        model.SubmodelElementCollectionOrdered(id_short="environment")
    )

    ports = model.SubmodelElementCollectionOrdered(id_short="ports")
    k = 0
    for variable in parse_model_variables(filename):
        k += 1
        ports.value.add(fmu_scalar_variable_to_ports_connector_smc(variable, id_short="portsConnector{}".format(k)))
    sm.value.add(ports)
    return sm


def add_ports_to_simulation_model(sm: model.SubmodelElementCollection,
                                  fmu: str) -> model.SubmodelElementCollection:
    """
    Add the ports (in and output) from a given fmu to a SimulationModel SubmodelElementCollectionOrdered
    """
    if sm.get_referable("ports") is not None:
        sm.remove_referable("ports")
    ports = model.SubmodelElementCollectionOrdered(id_short="ports")
    k = 0
    for variable in parse_model_variables(fmu):
        k += 1
        ports.value.add(fmu_scalar_variable_to_ports_connector_smc(variable, id_short="portsConnector{}".format(k)))
    sm.value.add(ports)
    return sm


def add_ports_to_existing_aasx(aasx_file: str,
                               fmu: str,
                               simulation_models_id: str,
                               simulation_model_id_short: str,
                               output_file: str):
    """
    Add the ports to an existing AASX file

    :param aasx_file: The AASX file
    :param fmu: The FMU file
    :param simulation_models_id: The IRI of the identifier of the SimulationModels submodel
    :param simulation_model_id_short: The id_short of the SimulationModel SubmodelElementCollection
    :param output_file: Name of the output aasx file
    """
    os: model.DictObjectStore[model.Identifiable] = model.DictObjectStore()
    file_store = aasx.DictSupplementaryFileContainer()
    with aasx.AASXReader(aasx_file) as reader:
        reader.read_into(object_store=os,
                         file_store=file_store)
    simulation_models = os.get_identifiable(model.Identifier(simulation_models_id, model.IdentifierType.IRI))
    assert isinstance(simulation_models, model.Submodel)
    simulation_model = simulation_models.get_referable(simulation_model_id_short)
    assert isinstance(simulation_model, model.SubmodelElementCollection)
    add_ports_to_simulation_model(simulation_model, fmu)
    aas: List[model.AssetAdministrationShell] = []
    for i in os:
        if isinstance(i, model.AssetAdministrationShell):
            aas.append(i)
    with aasx.AASXWriter(output_file) as writer:
        for i in aas:
            writer.write_aas(aas_id=i.identification,
                             object_store=os,
                             file_store=file_store,
                             submodel_split_parts=False)


def write_aasx_file_from_fmu(aas_id_short: str, input_file: str, output_file: str):
    """
    Writes an aasx file with the standardized simulationModel submodel from an .fmu file
    """
    asset = model.Asset(
                kind=model.AssetKind.INSTANCE,
                identification=model.Identifier(id_="https://example.com/resources/asset/{}".format(aas_id_short),
                                                id_type=model.IdentifierType.IRI)
            )
    simulation_models = model.Submodel(
            identification=model.Identifier(
                id_="https://example.com/resources/sm/{}".format(aas_id_short),
                id_type=model.IdentifierType.IRI
            ),
            id_short="SimulationModels"
        )
    simulation_models.submodel_element.add(simulation_model_from_fmu_file(input_file, id_short="simulationModel01"))
    aas = model.AssetAdministrationShell(
            asset=model.AASReference.from_referable(asset),
            identification=model.Identifier(id_="https://example.com/resources/aas/{}".format(aas_id_short),
                                            id_type=model.IdentifierType.IRI),
            id_short=aas_id_short,
            submodel={model.AASReference.from_referable(simulation_models)}
        )
    os = model.DictObjectStore([aas, asset, simulation_models])
    file_store = aasx.DictSupplementaryFileContainer()
    with open(input_file, "rb") as f:
        file_store.add_file("/{}".format(input_file), f, "application/fmu")
    with aasx.AASXWriter(output_file) as writer:
        writer.write_aas(aas_id=model.Identifier('https://example.com/resources/aas/{}'.format(aas.id_short),
                                                 model.IdentifierType.IRI),
                         object_store=os,
                         file_store=file_store,
                         submodel_split_parts=False)  # for compatibility with AASX Package Explorer


def main():
    write_aasx_file_from_fmu(
        aas_id_short=argv[1],
        input_file=argv[2],
        output_file=argv[3]
    )


if __name__ == '__main__':
    # check if paths were provided as commandline parameters
    if len(argv) > 1:
        main()
    else:
        print("Not enough arguments")
