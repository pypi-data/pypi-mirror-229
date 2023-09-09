# About(このライブラリについて)

This Python library can perform various calculations for scientific field.  
このPythonライブラリは電気関係の各種計算を行うことができます。
  
- [Document](https://nishizumi-lab.github.io/libs/python/calc2/docs/html/index.html)
- [Source code](https://github.com/nishizumi-lab/libs/tree/master/python/calc2/calc2/electricity)
- [Pypi](https://pypi.org/project/calc2/)  
 

## Getting started(導入方法)

Install with `pip`.  
pipでインストールできます。

```
pip install calc2
```


## Ex.1 Parameter calculation for external short circuit test.(外部短絡試験のパラメータ計算) 

Calculate the configuration of the external short-circuit test equipment that satisfies the required test conditions (target voltage, target current).  
試験条件（目標電圧、目標電流）を満たす外部短絡試験装置の構成を計算します。  

- [Sample code](https://github.com/nishizumi-lab/libs/blob/master/python/calc2/examples/short_test/sample1.py)
- [Sample code（webアプリ版）](https://github.com/nishizumi-lab/libs/tree/master/python/calc2/examples/short_test_webapp)  

## Ex.2 Parameter calculation of three-phase AC circuit(三相交流回路のパラメータ計算) 

The parameters of the three-phase AC circuit can be calculated from the given conditions. For example, when "line voltage", "power consumption" and "power factor" are determined, "line current", "impedance" and "phase voltage" can be calculated.  

与えられた条件から三相交流回路の各パラメータを計算できます。例えば、「線間電圧」「消費電力」「力率」が決まっているとき、「線電流」「インピーダンス」「相電圧」を計算できます。  

- [Sample code](https://github.com/nishizumi-lab/libs/blob/master/python/calc2/examples/ac3_test/sample1.py)  


## Ex.3 Detailed analysis of pulse wave(パルス波の詳細解析)

Analyzes various parameters of pulse signals.  
パルス信号のさまざまなパラメータを分析します。 
  
- [Sample code](https://github.com/nishizumi-lab/libs/blob/master/python/calc2/examples/pulse_test/sample1.py)    

## Ex.4 Battery capacity measurement(電池の容量測定)

Analyze the data obtained in the storage battery capacity measurement (discharge, charge, discharge).  
蓄電池の容量測定（捨て放電、充電、放電）で得られたデータを解析します。  

- [Sample code](https://github.com/nishizumi-lab/libs/blob/master/python/calc2/examples/battery_capacity_ah/sample1.py)  

