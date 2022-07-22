from data_types import *
all_classes = [StateArray, SwitchStates, CapacitorStates, RegulatorStates, CostArray, RealCostFunctions, ReactiveCostFunctions, RealWholesalePrices, ReactiveWholesalePrices, OperationalCosts, MeasurementArray, VoltagesMagnitude, VoltagesAngle, VoltagesReal, VoltagesImaginary, CurrentsMagnitude, CurrentsAngle, CurrentsReal, CurrentsImaginary, PowersMagnitude, PowersAngle, PowersReal, PowersImaginary, PowersImaginary, SolarIrradiances, Temperatures, WindSpeeds, StatesOfCharge, Topology, AdmittanceSparse, AdmittanceMatrix]

all_data = ''

for klass in all_classes:
    json_data = klass.schema_json(indent=4)
    #json_data = json_data.replace('\\n','\n')
    all_data += json_data
    all_data+='\n'

with open('data_types.json','w') as fp:
    fp.write(all_data)


