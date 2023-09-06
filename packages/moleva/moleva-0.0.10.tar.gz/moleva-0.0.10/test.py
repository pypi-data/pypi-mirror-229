from moleva import MolEva


model_dir = "/home/shuzhang/models/moleva/models"
smiles = '''
    COC(=O)C1=CC(NC(=O)CN2CCOCC2)=CC=C1N1CCC(C2=CC=CC=C2)CC1
    CC(C)C1=CC=C(NC(=O)C2CCCN(S(=O)(=O)C3=CN(C)C=N3)C2)C=C1
    YYDS
    CC1=NN2CC(NCC(=O)NCC3=CC=CO3)CCC2=N1
    COC1=CC=C(NC(=O)CN2N=CC3=C4C=CC=CC4=NC3=C2O)C=C1
    CC(C)(C)C1=CC(NC(=O)NC2=CC=C(C3=CN4C(=N3)SC3=CC=CC=C34)C=C2)=NO1
'''
smiles = map(lambda x: x.strip(), smiles.split())
smiles = filter(lambda x: x, smiles)
smiles = list(smiles)

eva = MolEva(model_dir)
scores = eva.dili(smiles)
for smi, score in zip(smiles, scores):
    print(f"score: {score}, smiles: {smi}")
