# DICE Embeddings: Hardware-agnostic Framework for Large-scale Knowledge Graph Embeddings

Knowledge graph embedding research has mainly focused on learning continuous representations of knowledge graphs towards the link prediction problem. 
Recently developed frameworks can be effectively applied in a wide range of research-related applications.
Yet, using these frameworks in real-world applications becomes more challenging as the size of the knowledge graph grows.

We developed the DICE Embeddings framework (dicee) to compute embeddings for large-scale knowledge graphs in a hardware-agnostic manner.
To achieve this goal, we rely on
1. **[Pandas](https://pandas.pydata.org/) & Co.** to use parallelism at preprocessing a large knowledge graph,
2. **[PyTorch](https://pytorch.org/) & Co.** to learn knowledge graph embeddings via multi-CPUs, GPUs, TPUs or computing cluster, and
3. **[Huggingface](https://huggingface.co/)** to ease the deployment of pre-trained models.

**Why [Pandas](https://pandas.pydata.org/) & Co. ?**
A large knowledge graph can be read and preprocessed (e.g. removing literals) by pandas, modin, or polars in parallel.
Through polars, a knowledge graph having more than 1 billion triples can be read in parallel fashion. 
Importantly, using these frameworks allow us to perform all necessary computations on a single CPU as well as a cluster of computers.

**Why [PyTorch](https://pytorch.org/) & Co. ?**
PyTorch is one of the most popular machine learning frameworks available at the time of writing. 
PytorchLightning facilitates scaling the training procedure of PyTorch without boilerplate.
In our framework, we combine [PyTorch](https://pytorch.org/) & [PytorchLightning](https://www.pytorchlightning.ai/).
Users can choose the trainer class (e.g., DDP by Pytorch) to train large knowledge graph embedding models with billions of parameters.
PytorchLightning allows us to use state-of-the-art model parallelism techniques (e.g. Fully Sharded Training, FairScale, or DeepSpeed)
without extra effort.
With our framework, practitioners can directly use PytorchLightning for model parallelism to train gigantic embedding models.

**Why [Hugging-face Gradio](https://huggingface.co/gradio)?**
Deploy a pre-trained embedding model without writing a single line of code.

## For more please visit [dice-embeddings](https://dice-group.github.io/dice-embeddings/)!

## Installation
<details><summary> Details </summary>

``` bash
git clone https://github.com/dice-group/dice-embeddings.git
conda create -n dice python=3.9 --no-default-packages && conda activate dice
pip3 install -r requirements.txt
```
or
```bash
pip install dicee
```
To test the Installation
```bash
wget https://hobbitdata.informatik.uni-leipzig.de/KG/KGs.zip --no-check-certificate
unzip KGs.zip
pytest -p no:warnings -x # it takes circa 15 minutes
pytest -p no:warnings --lf # run only the last failed test
pytest -p no:warnings --ff # to run the failures first and then the rest of the tests.
```
To see the software architecture, execute the following command
```
pyreverse dicee/ && dot -Tpng -x classes.dot -o dice_software.png && eog dice_software.png
# or
pyreverse dicee/trainer && dot -Tpng -x classes.dot -o trainer.png && eog trainer.png
```
</details>

## Knowledge Graph Embedding Models
<details> <summary> To see available Models</summary>

1. TransE, DistMult, ComplEx, ConEx, QMult, OMult, ConvO, ConvQ, Keci
2. All 44 models available in https://github.com/pykeen/pykeen#models

> For more, please refer to `examples`.
</details>

## How to Train
<details> <summary> To see  examples</summary>

Train a KGE model and evaluate it on the train, validation, and test sets of the UMLS benchmark dataset.
```bash
python main.py --path_dataset_folder "KGs/UMLS" --model Keci --eval_model "train_val_test"
```
where the data is in the following form
```bash
$ head -3 KGs/UMLS/train.txt 
acquired_abnormality    location_of     experimental_model_of_disease
anatomical_abnormality  manifestation_of        physiologic_function
alga    isa     entity
```
Models can be easily trained in a single node multi-gpu setting
```bash
python main.py --accelerator "gpu" --strategy "ddp" --path_dataset_folder "KGs/UMLS" --model Keci --eval_model "train_val_test" 
```

Train a KGE model by providing the path of a single file and store all parameters under newly created directory
called `KeciFamilyRun`.
```bash
python main.py --path_single_kg "KGs/Family/train.txt" --model Keci --path_to_store_single_run KeciFamilyRun
```
where the data is in the following form
```bash
$ head -3 KGs/Family/train.txt 
_:1 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Ontology> .
<http://www.benchmark.org/family#hasChild> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty> .
<http://www.benchmark.org/family#hasParent> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty> .
```
**Apart from n-triples or standard link prediction dataset formats, we support ["owl", "nt", "turtle", "rdf/xml", "n3"]***.
Moreover, a KGE model can be also trained  by providing **an endpoint of a triple store**.
```bash
python main.py --sparql_endpoint "http://localhost:3030/mutagenesis/" --model Keci
```
For more, please refer to `examples`.
</details>

## How to Deploy
<details> <summary> To see a single line of code</summary>

```python
from dicee import KGE
KGE(path='...').deploy(share=True,top_k=10)
```
</details>

<details> <summary> To see the interface of the webservice</summary>
<img src="dicee/lp.png" alt="Italian Trulli">
</details>

### Downstream Applications
#### Triple Classification
##### Using pre-trained ConEx on DBpedia 03-2022
```bash
# To download a pretrained ConEx
mkdir ConEx && cd ConEx && wget -r -nd -np https://hobbitdata.informatik.uni-leipzig.de/KGE/DBpedia/ConEx/ && cd ..
```
**Stay tune for Keci with >10B parameters on DBpedia!**
```python
from dicee import KGE
# (1) Load a pretrained ConEx on DBpedia 
pre_trained_kge = KGE(path='ConEx')

pre_trained_kge.triple_score(h=["http://dbpedia.org/resource/Albert_Einstein"],r=["http://dbpedia.org/ontology/birthPlace"],t=["http://dbpedia.org/resource/Ulm"]) # tensor([0.9309])
pre_trained_kge.triple_score(h=["http://dbpedia.org/resource/Albert_Einstein"],r=["http://dbpedia.org/ontology/birthPlace"],t=["http://dbpedia.org/resource/German_Empire"]) # tensor([0.9981])
pre_trained_kge.triple_score(h=["http://dbpedia.org/resource/Albert_Einstein"],r=["http://dbpedia.org/ontology/birthPlace"],t=["http://dbpedia.org/resource/Kingdom_of_Württemberg"]) # tensor([0.9994])
pre_trained_kge.triple_score(h=["http://dbpedia.org/resource/Albert_Einstein"],r=["http://dbpedia.org/ontology/birthPlace"],t=["http://dbpedia.org/resource/Germany"]) # tensor([0.9498])
pre_trained_kge.triple_score(h=["http://dbpedia.org/resource/Albert_Einstein"],r=["http://dbpedia.org/ontology/birthPlace"],t=["http://dbpedia.org/resource/France"]) # very low
pre_trained_kge.triple_score(h=["http://dbpedia.org/resource/Albert_Einstein"],r=["http://dbpedia.org/ontology/birthPlace"],t=["http://dbpedia.org/resource/Italy"]) # very low
```
### Relation Prediction
```python
from dicee import KGE
pre_trained_kge = KGE(path='ConEx')
pre_trained_kge.predict_topk(h=["http://dbpedia.org/resource/Albert_Einstein"],t=["http://dbpedia.org/resource/Ulm"])
```
### Entity Prediction
```python
from dicee import KGE
pre_trained_kge = KGE(path='ConEx')
pre_trained_kge.predict_topk(h=["http://dbpedia.org/resource/Albert_Einstein"],r=["http://dbpedia.org/ontology/birthPlace"]) 
pre_trained_kge.predict_topk(r=["http://dbpedia.org/ontology/birthPlace"],t=["http://dbpedia.org/resource/Albert_Einstein"]) 
```
### Finding Missing Triples
```python
from dicee import KGE
pre_trained_kge = KGE(path='ConEx')
missing_triples = pre_trained_kge.find_missing_triples(confidence=0.95, entities=[''], relations=[''])
```
### Complex Query Answering
The beam search technique proposed in [Complex Query Answering with Neural Link Predictors](https://arxiv.org/abs/2011.03459)
```python
from dicee import KGE
# (1) Load a pretrained KGE model on KGs/Family
pretrained_model = KGE(path='Experiments/2022-12-08 11:46:33.654677')
# (2) Query: ?P : \exist Married(P,E) \land hasSibling(E, F9M167) (To whom a sibling of F9M167 is married to?   
# (3) Decompose (2) into two query
# (3.1) Who is a sibling of F9M167? => hasSibling(E, F9M167) => {F9F141,F9M157}
# (3.2) To whom a results of (3.1) is married to ? {F9M142, F9F158}
pretrained_model.predict_conjunctive_query(entity='<http://www.benchmark.org/family#F9M167>',
                                          relations=['<http://www.benchmark.org/family#hasSibling>',
                                                     '<http://www.benchmark.org/family#married>'], topk=1)
```

### Description Logic Concept Learning (soon)
```python
from dicee import KGE
# (1) Load a pretrained KGE model on KGs/Family
pretrained_model = KGE(path='Experiments/2022-12-08 11:46:33.654677')
pretrained_model.learn_concepts(pos={''},neg={''},topk=1)
```

## Pre-trained Models
Please contact:  ```caglar.demir@upb.de ``` or ```caglardemir8@gmail.com ``` , if you lack hardware resources to obtain embeddings of a specific knowledge Graph.
- [DBpedia version: 06-2022 Embeddings](https://hobbitdata.informatik.uni-leipzig.de/KGE/DBpediaQMultEmbeddings_03_07):
  - Models: ConEx, QMult
- [YAGO3-10 ConEx embeddings](https://hobbitdata.informatik.uni-leipzig.de/KGE/conex/YAGO3-10.zip)
- [FB15K-237 ConEx embeddings](https://hobbitdata.informatik.uni-leipzig.de/KGE/conex/FB15K-237.zip)
- [WN18RR ConEx embeddings](https://hobbitdata.informatik.uni-leipzig.de/KGE/conex/WN18RR.zip)
- For more please look at [Hobbit Data](https://hobbitdata.informatik.uni-leipzig.de/KGE/)

## Docker
<details> <summary> Details</summary>
To build the Docker image:
```
docker build -t dice-embeddings .
```

To test the Docker image:
```
docker run --rm -v ~/.local/share/dicee/KGs:/dicee/KGs dice-embeddings ./main.py --model AConEx --embedding_dim 16
```
</details>

## How to cite
Currently, we are working on our manuscript describing our framework. 
If you really like our work and want to cite it now, feel free to chose one :) 
```
# DICE Embedding Framework
@article{demir2022hardware,
  title={Hardware-agnostic computation for large-scale knowledge graph embeddings},
  author={Demir, Caglar and Ngomo, Axel-Cyrille Ngonga},
  journal={Software Impacts},
  year={2022},
  publisher={Elsevier}
}
# Keci
Accepted at ECML. Stay tuned for the manuscript!
# KronE
@inproceedings{demir2022kronecker,
  title={Kronecker decomposition for knowledge graph embeddings},
  author={Demir, Caglar and Lienen, Julian and Ngonga Ngomo, Axel-Cyrille},
  booktitle={Proceedings of the 33rd ACM Conference on Hypertext and Social Media},
  pages={1--10},
  year={2022}
}
# QMult, OMult, ConvQ, ConvO
@InProceedings{pmlr-v157-demir21a,
  title = 	 {Convolutional Hypercomplex Embeddings for Link Prediction},
  author =       {Demir, Caglar and Moussallem, Diego and Heindorf, Stefan and Ngonga Ngomo, Axel-Cyrille},
  booktitle = 	 {Proceedings of The 13th Asian Conference on Machine Learning},
  pages = 	 {656--671},
  year = 	 {2021},
  editor = 	 {Balasubramanian, Vineeth N. and Tsang, Ivor},
  volume = 	 {157},
  series = 	 {Proceedings of Machine Learning Research},
  month = 	 {17--19 Nov},
  publisher =    {PMLR},
  pdf = 	 {https://proceedings.mlr.press/v157/demir21a/demir21a.pdf},
  url = 	 {https://proceedings.mlr.press/v157/demir21a.html},
}
# ConEx
@inproceedings{demir2021convolutional,
title={Convolutional Complex Knowledge Graph Embeddings},
author={Caglar Demir and Axel-Cyrille Ngonga Ngomo},
booktitle={Eighteenth Extended Semantic Web Conference - Research Track},
year={2021},
url={https://openreview.net/forum?id=6T45-4TFqaX}}
# Shallom
@inproceedings{demir2021shallow,
  title={A shallow neural model for relation prediction},
  author={Demir, Caglar and Moussallem, Diego and Ngomo, Axel-Cyrille Ngonga},
  booktitle={2021 IEEE 15th International Conference on Semantic Computing (ICSC)},
  pages={179--182},
  year={2021},
  organization={IEEE}
```
For any questions or wishes, please contact:  ```caglar.demir@upb.de``` or ```caglardemir8@gmail.com```

