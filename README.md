# **ABDEC 2024 提取视向速度小组总结** 

7.12-7.16 云南昆明



内容持续更新中！完整的高精度视向速度提取的pipeline将在某些日子后上传， stay tuned!




## 需要的软件



- iSpec: https://www.blancocuaresma.com/s/iSpec 

- PySME(非必需) :https://github.com/MingjieJian/SME (Python环境要求：3.7-3.11) 



## 成果

- ### 绝对视向速度测量 

  主要内容：使用iSpec计算FEROS 光谱相对于标准星的视向速度，过程中包含清理光谱，去除宇宙线以及Tulleric line

  code、数据在FEROS文件夹中，标准星的选取参考了https://www.aanda.org/articles/aa/pdf/2004/25/aa0081-04.pdf，我们使用了HD 81797

  FROS spectra 可以从ESO FEROS archive 下载

  http://archive.eso.org/wdb/wdb/adp/phase3_spectral/form?collection_name=FEROS

-----

- ### 高精度视向速度测量 

  - 绝对视向速度

  - 相对视向速度

    主要内容：一个手搓的pipeline，从多个观测的光谱出发，得到相对于一个template的视向速度及其误差 (目前可以到达10m/s的精度)，并且对FEROS有一个抽取二维光谱的过程

    目前简单的一个demo在prv文件夹中，pipeline将在后续更新上传

    

    - 如果你有自己的数据想要用成熟的软件处理：

    https://github.com/mzechmeister/serval

  

  

  

  -----

  

  
