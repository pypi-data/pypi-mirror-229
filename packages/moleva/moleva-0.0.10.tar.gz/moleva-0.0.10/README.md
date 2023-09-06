# 概述

预测分子属性，包含`DILI`等。


# 安装与卸载

```bash
pip install moleva
pip uninstall moleva
```


# 使用介绍

```python
from moleva import MolEva


model_dir = "/path/to/moleva/models"
eva = MolEva(model_dir)
smiles = ["CC1=NN2CC(NCC(=O)NCC3=CC=CO3)CCC2=N1"]
scores = eva.dili(smiles)
```

- `model_dir`说明

模型目录，文件列表如下，注意需要包含`LICENSE`文件

```text
.
├── dili
│   ├── config.iip
│   ├── model_0.iip
│   ├── model_1.iip
│   ├── model_2.iip
│   ├── model_3.iip
│   ├── model_4.iip
│   ├── model_5.iip
│   ├── model_6.iip
│   ├── model_7.iip
│   ├── model_8.iip
│   └── model_9.iip
├── fpscores.pkl.gz
├── LICENSE
└── mol2vec_model_300dim.pkl
```

- `scores`说明

预测结果，按照输入`smiles`的顺序，返回每个分子的`DILI`性质。

如果某个分子`无效`，则对应位置返回`None`。(具体情况请参考下面的测试用例)


# 测试代码

```python
from moleva import MolEva


model_dir = "/path/to/moleva/models"
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
```

- 运行结果

```text
score: 0.5689959526062012, smiles: COC(=O)C1=CC(NC(=O)CN2CCOCC2)=CC=C1N1CCC(C2=CC=CC=C2)CC1
score: 0.4833740293979645, smiles: CC(C)C1=CC=C(NC(=O)C2CCCN(S(=O)(=O)C3=CN(C)C=N3)C2)C=C1
score: None, smiles: YYDS
score: 0.4385642111301422, smiles: CC1=NN2CC(NCC(=O)NCC3=CC=CO3)CCC2=N1
score: 0.5384153127670288, smiles: COC1=CC=C(NC(=O)CN2N=CC3=C4C=CC=CC4=NC3=C2O)C=C1
score: 0.7214223146438599, smiles: CC(C)(C)C1=CC(NC(=O)NC2=CC=C(C3=CN4C(=N3)SC3=CC=CC=C34)C=C2)=NO1
```

# 公司官网

https://www.iipharma.cn
