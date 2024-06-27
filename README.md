# FragmentationStudy

Using MadGraph, we aim to produce particle level samples of pure QCD, like:


```
e+ e- > j j j
```

(And later we may want to have `p p > j j j`)

and also samples that happen via boosted color singlets such as

```
e+ e- > z a (z > j j)
```

And then we'll compare their fragmentation as a function of lab frame pT.


## How to: running ROC_Proc.py

using a docker image 
```bash
docker run --rm -ti -v $PWD:$PWD -w $PWD ghcr.io/scipp-atlas/mapyde/delphes
```

The above command essentially switches you to a container that has most of the libraries needed to run `ROC_Proc.py`. One must install numpy and uproot4 because this docker image does not contain the two, so `pip3 install numpy uproot4`.

Usage:  `python3 ROC_Proc.py <event_file_name.root> <run#>` 

